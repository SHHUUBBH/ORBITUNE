"""
ORBITUNE - AI-Powered Source Separator
Separates music into stems (vocals, drums, bass, other) using Demucs
GPU-accelerated for maximum speed and quality
"""

import torch
import torchaudio
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, Optional, Tuple
import time
from demucs.pretrained import get_model
from demucs.apply import apply_model
from demucs.audio import convert_audio

# Import config
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    DEVICE, USE_GPU, GPU_MEMORY_GB, SAMPLE_RATE, BIT_DEPTH,
    DEMUCS_MODEL, DEMUCS_SHIFTS, DEMUCS_OVERLAP, DEMUCS_SPLIT, DEMUCS_STEMS,
    get_raw_audio_path, get_stem_path, get_song_directory, PROCESSED_AUDIO_DIR
)


class SourceSeparator:
    """
    AI-powered audio source separation using Demucs
    
    Features:
    - GPU acceleration (10-20x faster than CPU)
    - Highest quality separation (htdemucs model)
    - Universal compatibility (works with all music genres)
    - Intelligent error handling
    - Adaptive processing based on audio characteristics
    - Memory-efficient processing
    """
    
    def __init__(self, model_name: str = DEMUCS_MODEL):
        """
        Initialize source separator
        
        Args:
            model_name: Demucs model to use ('htdemucs', 'htdemucs_ft', etc.)
        """
        self.model_name = model_name
        self.device = DEVICE
        self.sample_rate = SAMPLE_RATE
        self.stems = DEMUCS_STEMS
        
        print("="*70)
        print("🎵 ORBITUNE - Source Separator")
        print("="*70)
        print(f"🤖 Model: {model_name}")
        print(f"🎮 Device: {self.device}")
        
        if USE_GPU:
            print(f"💾 GPU Memory: {GPU_MEMORY_GB:.2f} GB")
            print(f"⚡ Quality: Maximum ({DEMUCS_SHIFTS} shifts)")
        else:
            print("⚠️  Using CPU (slower but works)")
        
        # Load Demucs model
        print("\n📥 Loading Demucs AI model...")
        print("   (First time: downloads ~350MB model, takes 2-5 min)")
        
        start_time = time.time()
        try:
            self.model = get_model(model_name)
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            load_time = time.time() - start_time
            print(f"✅ Model loaded in {load_time:.1f} seconds")
            print(f"📊 Model info:")
            print(f"   - Sources: {len(self.model.sources)} stems")
            print(f"   - Sample rate: {self.model.samplerate} Hz")
            print(f"   - Channels: {self.model.audio_channels}")
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise
        
        print("="*70)
        print("✅ Source Separator Ready!")
        print("="*70)
    
    def separate(self, song_id: str, progress_callback=None) -> Optional[Dict[str, Path]]:
        """
        Separate a song into stems
        
        Args:
            song_id: Unique song identifier
            progress_callback: Optional function to report progress
            
        Returns:
            Dictionary mapping stem names to file paths
        """
        print(f"\n{'='*70}")
        print(f"🎵 SEPARATING SONG: {song_id}")
        print(f"{'='*70}")
        
        # Get paths
        input_path = get_raw_audio_path(song_id)
        output_dir = get_song_directory(song_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate input
        if not input_path.exists():
            print(f"❌ Audio file not found: {input_path}")
            return None
        
        print(f"📂 Input: {input_path.name}")
        print(f"📂 Output: {output_dir}")
        print(f"💾 File size: {input_path.stat().st_size / (1024*1024):.1f} MB")
        
        try:
            # Step 1: Load audio
            print("\n📥 Step 1/4: Loading audio...")
            audio, sr = self._load_audio(input_path)
            print(f"   ✅ Loaded: {audio.shape[0]} channels, {audio.shape[1]} samples")
            print(f"   ⏱️  Duration: {audio.shape[1] / sr:.1f} seconds")
            
            if progress_callback:
                progress_callback(25, "Audio loaded")
            
            # Step 2: Preprocess audio
            print("\n🔧 Step 2/4: Preprocessing audio...")
            audio = self._preprocess_audio(audio, sr)
            print(f"   ✅ Preprocessed: {audio.shape}")
            
            if progress_callback:
                progress_callback(35, "Audio preprocessed")
            
            # Step 3: AI Separation (THE MAGIC!)
            print("\n🤖 Step 3/4: AI Separation (this is where the magic happens)...")
            print(f"   🎯 Using {DEMUCS_SHIFTS} shifts for maximum quality")
            print(f"   ⚡ Processing on {self.device}...")
            
            start_time = time.time()
            stems = self._separate_stems(audio)
            separation_time = time.time() - start_time
            
            print(f"   ✅ Separation complete in {separation_time:.1f} seconds!")
            print(f"   📊 Separated into {len(stems)} stems")
            
            if progress_callback:
                progress_callback(75, "Separation complete")
            
            # Step 4: Save stems
            print("\n💾 Step 4/4: Saving stems...")
            output_paths = self._save_stems(stems, song_id, output_dir)
            
            if progress_callback:
                progress_callback(100, "Complete")
            
            # Print summary
            print(f"\n{'='*70}")
            print("✅ SEPARATION COMPLETE!")
            print(f"{'='*70}")
            print(f"⏱️  Total time: {separation_time:.1f} seconds")
            print(f"📁 Output directory: {output_dir}")
            print("\n📊 Stems created:")
            for stem_name, path in output_paths.items():
                size_mb = path.stat().st_size / (1024*1024)
                print(f"   ✅ {stem_name:8s}: {path.name:20s} ({size_mb:.1f} MB)")
            print(f"{'='*70}\n")
            
            return output_paths
            
        except Exception as e:
            print(f"\n❌ Separation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _load_audio(self, path: Path) -> Tuple[torch.Tensor, int]:
        """
        Load audio file with intelligent format handling
        
        Args:
            path: Path to audio file
            
        Returns:
            Tuple of (audio tensor, sample rate)
        """
        try:
            # Try torchaudio first (supports most formats)
            audio, sr = torchaudio.load(path)
            return audio, sr
            
        except Exception as e:
            # Fallback to soundfile
            try:
                audio, sr = sf.read(path, dtype='float32')
                # Convert to torch tensor
                audio = torch.from_numpy(audio.T)  # Transpose to (channels, samples)
                return audio, sr
                
            except Exception as e2:
                raise Exception(f"Failed to load audio: {e}, {e2}")
    
    def _preprocess_audio(self, audio: torch.Tensor, sr: int) -> torch.Tensor:
        """
        Preprocess audio for Demucs
        Handles sample rate conversion, channel conversion, normalization
        
        Args:
            audio: Audio tensor (channels, samples)
            sr: Sample rate
            
        Returns:
            Preprocessed audio tensor
        """
        # Move to device
        audio = audio.to(self.device)
        
        # Convert sample rate if needed
        if sr != self.model.samplerate:
            print(f"   📊 Resampling: {sr} Hz → {self.model.samplerate} Hz")
            audio = convert_audio(
                audio,
                sr,
                self.model.samplerate,
                self.model.audio_channels
            )
        
        # Ensure correct number of channels
        if audio.shape[0] != self.model.audio_channels:
            print(f"   📊 Converting channels: {audio.shape[0]} → {self.model.audio_channels}")
            if audio.shape[0] == 1 and self.model.audio_channels == 2:
                # Mono to stereo: duplicate channel
                audio = audio.repeat(2, 1)
            elif audio.shape[0] == 2 and self.model.audio_channels == 1:
                # Stereo to mono: average channels
                audio = audio.mean(dim=0, keepdim=True)
            else:
                # Use convert_audio for other cases
                audio = convert_audio(
                    audio,
                    self.model.samplerate,
                    self.model.samplerate,
                    self.model.audio_channels
                )
        
        # Ensure audio is in float32
        audio = audio.float()
        
        # Check for NaN or Inf values
        if torch.isnan(audio).any() or torch.isinf(audio).any():
            print("   ⚠️  Warning: NaN or Inf values detected, cleaning...")
            audio = torch.nan_to_num(audio, nan=0.0, posinf=1.0, neginf=-1.0)
        
        # Normalize to prevent clipping (preserve dynamic range)
        max_val = audio.abs().max()
        if max_val > 0:
            # Gentle normalization - only if signal is too hot
            if max_val > 0.99:
                audio = audio / (max_val * 1.01)  # Leave small headroom
                print(f"   📊 Normalized audio (peak: {max_val:.3f})")
        
        return audio
    
    def _separate_stems(self, audio: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Perform AI-powered source separation
        Uses Demucs with optimized settings for quality
        
        Args:
            audio: Preprocessed audio tensor
            
        Returns:
            Dictionary mapping stem names to audio tensors
        """
        # Add batch dimension
        audio = audio.unsqueeze(0)  # (1, channels, samples)
        
        # Apply Demucs model
        with torch.no_grad():
            # Use highest quality settings
            sources = apply_model(
                self.model,
                audio,
                device=self.device,
                shifts=DEMUCS_SHIFTS,  # 10 for GPU = highest quality
                split=DEMUCS_SPLIT,    # True = memory efficient
                overlap=DEMUCS_OVERLAP, # 0.25 = smooth transitions
                progress=True           # Show progress
            )
        
        # Remove batch dimension and move to CPU
        sources = sources[0].cpu()
        
        # Map sources to stem names
        stems = {}
        for i, stem_name in enumerate(self.model.sources):
            stems[stem_name] = sources[i]
        
        return stems
    
    def _save_stems(self, stems: Dict[str, torch.Tensor], song_id: str, output_dir: Path) -> Dict[str, Path]:
        """
        Save separated stems as high-quality WAV files
        
        Args:
            stems: Dictionary of stem tensors
            song_id: Song identifier
            output_dir: Output directory
            
        Returns:
            Dictionary mapping stem names to saved file paths
        """
        output_paths = {}
        
        for stem_name, audio in stems.items():
            # Convert tensor to numpy
            audio_np = audio.numpy()
            
            # Transpose to (samples, channels) for soundfile
            if audio_np.ndim == 2:
                audio_np = audio_np.T
            
            # Ensure float32
            audio_np = audio_np.astype(np.float32)
            
            # Gentle normalization to prevent clipping while preserving dynamics
            max_val = np.abs(audio_np).max()
            if max_val > 0.99:
                audio_np = audio_np / (max_val * 1.01)
            
            # Save as high-quality WAV
            output_path = get_stem_path(song_id, stem_name)
            
            sf.write(
                output_path,
                audio_np,
                self.model.samplerate,
                subtype=f'PCM_{BIT_DEPTH}'  # 24-bit for studio quality
            )
            
            output_paths[stem_name] = output_path
        
        return output_paths
    
    def check_quality(self, stems: Dict[str, Path]) -> Dict[str, Dict]:
        """
        Quality check for separated stems
        Analyzes each stem and provides quality metrics
        
        Args:
            stems: Dictionary of stem file paths
            
        Returns:
            Dictionary of quality metrics per stem
        """
        print("\n🔍 Quality Check:")
        quality_report = {}
        
        for stem_name, path in stems.items():
            # Load stem
            audio, sr = sf.read(path)
            
            # Calculate metrics
            rms = np.sqrt(np.mean(audio**2))
            peak = np.abs(audio).max()
            dynamic_range = 20 * np.log10(peak / (rms + 1e-10))
            
            # Check for silence
            is_silent = rms < 0.001
            
            quality_report[stem_name] = {
                'rms': float(rms),
                'peak': float(peak),
                'dynamic_range_db': float(dynamic_range),
                'is_silent': is_silent,
                'samples': len(audio),
                'duration_seconds': len(audio) / sr
            }
            
            status = "⚠️ SILENT" if is_silent else "✅ OK"
            print(f"   {status} {stem_name:8s}: Peak={peak:.3f}, RMS={rms:.4f}, DR={dynamic_range:.1f}dB")
        
        return quality_report


# =============================================================================
# USAGE EXAMPLE / TESTING
# =============================================================================
if __name__ == "__main__":
    import json
    
    print("="*70)
    print("🎵 ORBITUNE - Source Separator Test")
    print("="*70)
    
    # Initialize separator
    separator = SourceSeparator()
    
    # Get list of downloaded songs
    from config import RAW_AUDIO_DIR
    
    downloaded_songs = [d.name for d in RAW_AUDIO_DIR.iterdir() if d.is_dir()]
    
    if not downloaded_songs:
        print("\n❌ No songs found!")
        print("Please download a song first using youtube_downloader.py")
    else:
        print(f"\n📋 Found {len(downloaded_songs)} downloaded song(s):")
        for i, song_id in enumerate(downloaded_songs, 1):
            # Try to load metadata
            metadata_path = RAW_AUDIO_DIR / song_id / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, encoding='utf-8') as f:
                    metadata = json.load(f)
                print(f"{i}. {song_id}")
                print(f"   Title: {metadata.get('title', 'Unknown')}")
                print(f"   Duration: {metadata.get('duration_string', 'Unknown')}")
            else:
                print(f"{i}. {song_id}")
        
        # Ask user which song to process
        choice = input(f"\nEnter number to separate (1-{len(downloaded_songs)}) or 0 to exit: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(downloaded_songs):
            selected_song_id = downloaded_songs[int(choice) - 1]
            
            print(f"\n🎯 Selected: {selected_song_id}")
            
            # Check if already processed
            output_dir = get_song_directory(selected_song_id)
            if output_dir.exists() and any(output_dir.iterdir()):
                overwrite = input("⚠️  Song already processed. Overwrite? (y/n): ").strip().lower()
                if overwrite != 'y':
                    print("❌ Cancelled")
                    exit()
            
            # Separate the song
            result = separator.separate(selected_song_id)
            
            if result:
                # Run quality check
                quality_report = separator.check_quality(result)
                
                print("\n" + "="*70)
                print("✅ SUCCESS! Song separated into 4 stems")
                print("="*70)
                print("\n🎵 You can now use these stems for 16D spatial audio!")
                print(f"📁 Location: {output_dir}")
            else:
                print("\n❌ Separation failed!")
        else:
            print("❌ Invalid choice or cancelled")
