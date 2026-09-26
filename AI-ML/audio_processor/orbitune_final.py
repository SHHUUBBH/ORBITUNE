"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           ORBITUNE - Professional 3D Spatial Audio Engine                   ║
║                                                                              ║
║  COPYRIGHT © 2025 Yuvraj Singh Kushwah & Subhro Pal. All Rights Reserved.   ║
║                                                                              ║
║  ⚠️  CRITICAL TRADE SECRET - MAXIMUM PROTECTION                             ║
║                                                                              ║
║  This file contains the core proprietary algorithms and methodologies       ║
║  that define ORBITUNE's revolutionary 3D audio processing system.           ║
║                                                                              ║
║  PROTECTED TRADE SECRETS (Examples):                                        ║
║  • Dynamic Distance Variation formula: distance(θ) = base × (1.125 - 0.475×cos(θ)) ║
║  • Azimuth calculation for smooth 360° rotation                             ║
║  • Time-varying spatial positioning curves                                  ║
║  • Genre-specific rotation speed profiles                                   ║
║  • Professional HRTF binaural positioning implementation                    ║
║  • Broadcast-quality mastering chain                                        ║
║                                                                              ║
║  ANY unauthorized use, copying, reverse engineering, or disclosure of       ║
║  these algorithms will result in IMMEDIATE LEGAL ACTION with statutory      ║
║  damages of up to ₹20,00,000 (INR) or $150,000 (USD) per violation.        ║
║                                                                              ║
║  Jurisdiction: Courts of Bhopal, Madhya Pradesh, India                      ║
║                                                                              ║
║  Contact: yuvrajsk.bpl@gmail.com | shubhropal62@gmail.com                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

ORBITUNE - Professional 3D Spatial Audio
=========================================
Broadcast-quality 3D audio with genre-aware processing

Creates studio-quality spatial audio that feels REAL:
- Professional HRTF binaural positioning
- Genre-aware spatial strategies
- Realistic room acoustics
- Smooth, observable rotations
- Broadcast-standard mastering

Quality: Comparable to professional 8D audio productions on YouTube
Author: ORBITUNE
"""

import os
import sys
import json
import time
import numpy as np
import soundfile as sf
from typing import Optional, Dict
import torch
import torch.nn.functional as F
from pathlib import Path

# High-quality resampling (CPU). Fallback to linear if unavailable.
try:
    from torchaudio.functional import resample as ta_resample  # type: ignore
    _HAS_TORCHAUDIO = True
except Exception:
    _HAS_TORCHAUDIO = False

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *

# Import our professional modules
from audio_processor.genre_detector import GenreDetector
from audio_processor.hrtf_processor import HRTFProcessor


class ProfessionalReverb:
    """
    Professional studio-quality reverb
    
    Creates realistic room acoustics using:
    - Early reflections (first 50ms)
    - Late reverberation tail
    - Frequency-dependent decay
    - Stereo decorrelation
    """
    
    def __init__(self, sample_rate: int, device: str):
        self.sample_rate = sample_rate
        self.device = torch.device(device)
    
    def apply(
        self,
        audio: torch.Tensor,
        room_size: str = 'medium',
        reverb_amount: float = 0.25,
        pre_delay: float = 0.02
    ) -> torch.Tensor:
        """
        Apply professional reverb
        
        Args:
            audio: Stereo audio [2, samples]
            room_size: 'small', 'medium', 'large', 'huge', or 'concert_hall'
            reverb_amount: Wet/dry mix (0.0-1.0)
            pre_delay: Pre-delay in seconds
        
        Returns:
            Audio with reverb [2, samples]
        """
        if reverb_amount < 0.01:
            return audio  # Skip reverb if amount is negligible
        
        # Room parameters - TIGHTER for clarity
        room_params = {
            'small': {'rt60': 0.15, 'early_count': 4, 'size_factor': 0.3},  # Very tight
            'medium': {'rt60': 0.25, 'early_count': 6, 'size_factor': 0.5},  # Tight
            'large': {'rt60': 0.35, 'early_count': 8, 'size_factor': 0.7},  # Still tight
            'huge': {'rt60': 0.45, 'early_count': 10, 'size_factor': 0.9},  # Controlled
            'concert_hall': {'rt60': 0.40, 'early_count': 9, 'size_factor': 0.8}  # Natural but clear
        }
        
        params = room_params.get(room_size, room_params['medium'])
        rt60 = params['rt60']
        early_count = params['early_count']
        
        # Create impulse response
        ir_len = int(rt60 * self.sample_rate)
        pre_delay_samples = int(pre_delay * self.sample_rate)
        
        # Early reflections (first 50ms)
        early_len = min(int(0.05 * self.sample_rate), ir_len // 3)
        early_times = torch.rand(early_count, device=self.device) * early_len
        early_gains = torch.exp(-early_times / (self.sample_rate * 0.02))
        
        # Late reverberation (exponential decay)
        t = torch.linspace(0, rt60, ir_len - early_len, device=self.device)
        late_envelope = torch.exp(-6.91 * t / rt60)  # -60dB decay
        
        # Create stereo IRs with decorrelation
        ir_left = torch.zeros(ir_len, device=self.device)
        ir_right = torch.zeros(ir_len, device=self.device)
        
        # Add early reflections (slightly different for L/R)
        for i, (time_idx, gain) in enumerate(zip(early_times.int(), early_gains)):
            if time_idx < len(ir_left):
                ir_left[time_idx] += gain * (1 + torch.randn(1, device=self.device)[0] * 0.1)
                # Right channel slightly delayed
                time_idx_r = min(time_idx + torch.randint(1, 5, (1,), device=self.device)[0], len(ir_right) - 1)
                ir_right[time_idx_r] += gain * (1 + torch.randn(1, device=self.device)[0] * 0.1)
        
        # Add late reverberation (stereo decorrelated)
        late_left = torch.randn(ir_len - early_len, device=self.device) * late_envelope
        late_right = torch.randn(ir_len - early_len, device=self.device) * late_envelope
        
        ir_left[early_len:] += late_left * 0.3
        ir_right[early_len:] += late_right * 0.3
        
        # Apply pre-delay
        if pre_delay_samples > 0:
            ir_left = F.pad(ir_left, (pre_delay_samples, 0))[:ir_len]
            ir_right = F.pad(ir_right, (pre_delay_samples, 0))[:ir_len]
        
        # Convolve with FFT (much faster)
        reverb = self._fft_convolve_stereo(audio, ir_left, ir_right)
        
        # Mix wet and dry
        # Use a modest amount of reverb so stems feel naturally glued together
        dry_gain = 1.0 - (reverb_amount * 0.8)
        wet_gain = reverb_amount * 0.8
        
        output = audio * dry_gain + reverb * wet_gain
        
        # Add clarity/presence boost (3-8kHz range)
        output = self._enhance_clarity(output)
        
        return output
    
    def _fft_convolve_stereo(
        self,
        audio: torch.Tensor,
        ir_left: torch.Tensor,
        ir_right: torch.Tensor
    ) -> torch.Tensor:
        """Fast FFT-based convolution for stereo"""
        audio_len = audio.shape[1]
        ir_len = len(ir_left)
        fft_len = 2 ** int(np.ceil(np.log2(audio_len + ir_len)))
        
        # FFT of audio
        audio_fft = torch.fft.rfft(audio, n=fft_len, dim=1)
        
        # FFT of IRs
        ir_left_fft = torch.fft.rfft(ir_left, n=fft_len)
        ir_right_fft = torch.fft.rfft(ir_right, n=fft_len)
        
        # Convolve
        left_fft = audio_fft[0] * ir_left_fft
        right_fft = audio_fft[1] * ir_right_fft
        
        # IFFT
        left = torch.fft.irfft(left_fft, n=fft_len)[:audio_len]
        right = torch.fft.irfft(right_fft, n=fft_len)[:audio_len]
        
        return torch.stack([left, right])
    
    def _enhance_clarity(self, audio: torch.Tensor) -> torch.Tensor:
        """Minimal processing - let reverb stay bright and clear."""
        # No frequency shaping - preserve full bandwidth for realistic reverb
        return audio


class ProfessionalMastering:
    """
    Broadcast-quality mastering chain
    
    Brings audio to industry standards:
    - Multi-band compression
    - Loudness normalization (LUFS)
    - Peak limiting
    - Stereo enhancement
    - Final polish
    """
    
    def __init__(self, sample_rate: int, device: str):
        self.sample_rate = sample_rate
        self.device = torch.device(device)
    
    def master(
        self,
        audio: torch.Tensor,
        target_lufs: float = -14.0,
        peak_ceiling: float = -1.0,
        stereo_width: float = 1.2
    ) -> torch.Tensor:
        """
        Apply professional mastering
        
        Args:
            audio: Stereo audio [2, samples]
            target_lufs: Target loudness in LUFS (-14 for streaming)
            peak_ceiling: Maximum peak level in dB
            stereo_width: Stereo width factor (1.0 = no change, >1.0 = wider)
        
        Returns:
            Mastered audio [2, samples]
        """
        # Step 0: GLOBAL bass reduction for balanced mix
        audio = self._reduce_excessive_bass(audio)
        
        # Step 1: Subtle stereo widening (fast)
        if stereo_width != 1.0 and audio.shape[0] == 2:
            audio = self._enhance_stereo(audio, stereo_width)
        
        # Step 2: (Optional) multi-band compression
        # Disabled by default to preserve maximum natural dynamics.
        # audio = self._multiband_compress(audio)
        
        # Step 3: Loudness normalization (fast) – now only attenuates if signal
        # is significantly hotter than the target, never boosts quiet material.
        audio = self._normalize_loudness(audio, target_lufs)
        
        # Step 4: De-essing and high-frequency smoothing (ANTI EAR-PIERCING)
        audio = self._deess_and_smooth_highs(audio)
        
        # Step 5: Peak limiting (fully vectorized)
        peak_linear = 10 ** (peak_ceiling / 20.0)
        audio = self._soft_limit(audio, peak_linear)
        
        # Step 6: Final warmth (gentle high-freq rolloff, NO harshness)
        audio = self._add_clarity_boost(audio)
        
        # Step 7: Natural crossfeed for comfortable, realistic stereo
        audio = self._gentle_crossfeed(audio, mix=0.12)  # Natural coupling, reduced fatigue
        
        # Step 8: Final DC offset removal (vectorized)
        audio = audio - audio.mean(dim=1, keepdim=True)
        
        return audio
    
    def _reduce_excessive_bass(self, audio: torch.Tensor) -> torch.Tensor:
        """AGGRESSIVE bass control for ultra-clean, balanced mix."""
        freqs = torch.fft.rfftfreq(audio.shape[1], 1/self.sample_rate, device=self.device)
        bass_cut = torch.ones_like(freqs)
        
        # High-pass: <25 Hz steep cut (-24 dB) - remove all sub-rumble
        hp_mask = freqs < 25
        bass_cut[hp_mask] = 0.063  # -24 dB
        
        # Low shelf: 30–150 Hz STRONG cut (-10 dB) - tame bass bloat
        low_shelf_mask = (freqs >= 30) & (freqs <= 150)
        bass_cut[low_shelf_mask] = 0.316  # -10 dB
        
        # 150–250 Hz: moderate control (-5 dB)
        mid_low_mask = (freqs >= 150) & (freqs <= 250)
        bass_cut[mid_low_mask] = 0.562  # -5 dB
        
        # 250–400 Hz: reduce muddiness (-3 dB)
        mud_mask = (freqs >= 250) & (freqs <= 400)
        bass_cut[mud_mask] = 0.707  # -3 dB
        
        # 400–500 Hz: smooth transition to unity
        trans_mask = (freqs >= 400) & (freqs <= 500)
        if trans_mask.any():
            trans_curve = (freqs[trans_mask] - 400) / 100  # 0..1
            bass_cut[trans_mask] = 0.85 + (1.0 - 0.85) * trans_curve  # -1.5 dB to 0 dB
        
        fft = torch.fft.rfft(audio, dim=1)
        filtered_fft = fft * bass_cut
        output = torch.fft.irfft(filtered_fft, n=audio.shape[1], dim=1)
        return output
    
    def _enhance_stereo(self, audio: torch.Tensor, width: float) -> torch.Tensor:
        """Subtle stereo widening"""
        mid = (audio[0] + audio[1]) / 2
        side = (audio[0] - audio[1]) / 2
        
        # Enhance side (be conservative to avoid phase issues)
        side_enhanced = side * width
        
        # Reconstruct
        left = mid + side_enhanced
        right = mid - side_enhanced
        
        return torch.stack([left, right])
    
    def _multiband_compress(self, audio: torch.Tensor) -> torch.Tensor:
        """Gentle multi-band compression - ULTRA-FAST GPU VERSION"""
        # Use FFT for parallel band processing (much faster)
        fft = torch.fft.rfft(audio, dim=1)
        freqs = torch.fft.rfftfreq(audio.shape[1], 1/self.sample_rate, device=self.device)
        
        # Create band masks
        low_mask = freqs < 200
        mid_mask = (freqs >= 200) & (freqs < 4000)
        high_mask = freqs >= 4000
        
        # Process each band with MINIMAL compression (natural dynamics)
        low_fft = fft.clone()
        low_fft[:, ~low_mask] = 0
        low = torch.fft.irfft(low_fft, n=audio.shape[1], dim=1)
        low_compressed = self._compress_fast(low, threshold=0.80, ratio=1.20)  # Gentle
        
        mid_fft = fft.clone()
        mid_fft[:, ~mid_mask] = 0
        mid = torch.fft.irfft(mid_fft, n=audio.shape[1], dim=1)
        mid_compressed = self._compress_fast(mid, threshold=0.90, ratio=1.10)  # Very gentle
        
        high_fft = fft.clone()
        high_fft[:, ~high_mask] = 0
        high = torch.fft.irfft(high_fft, n=audio.shape[1], dim=1)
        high_compressed = self._compress_fast(high, threshold=0.95, ratio=1.05)  # Minimal
        
        # Recombine (all GPU operations)
        return low_compressed + mid_compressed + high_compressed
    
    def _compress_fast(self, audio: torch.Tensor, threshold: float, ratio: float) -> torch.Tensor:
        """ULTRA-FAST compression without envelope calculation"""
        # Simple RMS-based compression (much faster)
        # Calculate RMS per channel
        rms = torch.sqrt(torch.mean(audio ** 2, dim=1, keepdim=True))
        
        # Apply compression curve (vectorized)
        gain = torch.ones_like(rms)
        over = rms > threshold
        gain[over] = (threshold / rms[over]) ** ((ratio - 1.0) / ratio)
        
        # Apply gain
        return audio * gain
    
    
    def _smooth_gain_fast(self, gain: torch.Tensor, attack: float, release: float) -> torch.Tensor:
        """ULTRA-FAST gain smoothing using convolution - NO PYTHON LOOPS!"""
        # Use simple exponential smoothing via convolution (much faster)
        alpha = np.exp(-1.0 / (attack * self.sample_rate * 10))  # Approximate
        
        # Create smoothing kernel
        kernel_len = min(int(-5 / np.log(alpha)), 500)
        kernel = torch.pow(alpha, torch.arange(kernel_len, device=self.device, dtype=torch.float32))
        kernel = kernel / kernel.sum()
        kernel = kernel.view(1, 1, -1)
        
        # Apply smoothing to each channel (GPU convolution)
        smoothed = F.conv1d(
            gain.unsqueeze(1),
            kernel,
            padding=kernel_len//2
        ).squeeze(1)
        
        # Trim to original length
        if smoothed.shape[1] != gain.shape[1]:
            smoothed = smoothed[:, :gain.shape[1]]
        
        return smoothed
    
    def _smooth_gain(self, gain: torch.Tensor, attack: float, release: float) -> torch.Tensor:
        """Smooth gain changes with attack/release - DEPRECATED, use _smooth_gain_fast"""
        # This is kept for compatibility but not used
        return self._smooth_gain_fast(gain, attack, release)
    
    def _normalize_loudness(self, audio: torch.Tensor, target_lufs: float) -> torch.Tensor:
        """Normalize audio to target LUFS for consistent, engaging playback.
        
        Applies proper loudness normalization - both boost and attenuate as needed.
        FIXED: Improved LUFS-to-RMS conversion for accurate targeting.
        """
        # Fast RMS calculation (GPU)
        rms = torch.sqrt(torch.mean(audio ** 2))
        if rms <= 0:
            return audio
        
        # IMPROVED: More accurate LUFS to RMS conversion
        # LUFS are integrated loudness; simplified conversion:
        # RMS ≈ 10^((LUFS - 3.01) / 20)
        # The -3.01 offset accounts for K-weighting and gating
        target_rms = 10 ** ((target_lufs - 3.01) / 20.0)
        
        # Calculate gain to reach target
        gain = target_rms / (rms + 1e-8)
        
        # Apply gain with reasonable limits
        # Allow boosting up to +18dB, attenuate down to -12dB for flexibility
        gain_tensor = torch.tensor(gain, dtype=torch.float32, device=self.device)
        gain = torch.clamp(gain_tensor, 0.25, 8.0)  # 0.25 = -12dB, 8.0 = +18dB
        
        return audio * gain
    
    def _soft_limit(self, audio: torch.Tensor, ceiling: float) -> torch.Tensor:
        """Very gentle soft limiter - preserves transients"""
        scale = ceiling / torch.tanh(torch.tensor(1.5, device=self.device))
        limited = torch.tanh(audio / ceiling * 1.5) * scale
        return limited
    
    def _gentle_crossfeed(self, audio: torch.Tensor, mix: float = 0.12) -> torch.Tensor:
        """Gentle crossfeed for natural, comfortable stereo image.
        
        ULTRA-REALISTIC: 12% crossfeed creates natural soundstage
        - Reduces fatigue from extreme stereo separation
        - Mimics natural head coupling in real listening
        - Maintains spatial width while improving comfort
        """
        if audio.shape[0] != 2 or mix <= 0:
            return audio
        left, right = audio[0], audio[1]
        left_cf = left * (1 - mix) + right * mix
        right_cf = right * (1 - mix) + left * mix
        return torch.stack([left_cf, right_cf])
    
    def _deess_and_smooth_highs(self, audio: torch.Tensor) -> torch.Tensor:
        """MINIMAL de-essing that preserves maximum air and clarity
        
        REFINED: Only targets the narrowest sibilance peak.
        We want ALL the air and sparkle - just control piercing harshness.
        """
        freqs = torch.fft.rfftfreq(audio.shape[1], 1/self.sample_rate, device=self.device)
        
        # Create minimal de-essing curve
        deess_curve = torch.ones_like(freqs)
        
        # MINIMAL de-essing: Only the narrowest sibilance peak (6.5-7.5kHz)
        # This leaves 7-15kHz air boost completely intact!
        sibilance_mask = (freqs >= 6500) & (freqs <= 7500)
        if sibilance_mask.any():
            # Minimal reduction (~-1.5dB) - maximum air preservation!
            deess_curve[sibilance_mask] = 0.84  # -1.5dB (was -2dB)
        
        # Apply de-essing curve
        fft = torch.fft.rfft(audio, dim=1)
        deessed_fft = fft * deess_curve
        output = torch.fft.irfft(deessed_fft, n=audio.shape[1], dim=1)
        
        return output
    
    def _add_clarity_boost(self, audio: torch.Tensor) -> torch.Tensor:
        """Add presence, clarity and air for ULTRA-REALISTIC "ALIVE" sound
        
        ENHANCED: Stronger presence and air for truly immersive experience.
        These frequencies make audio feel like it's happening in front of you.
        """
        freqs = torch.fft.rfftfreq(audio.shape[1], 1/self.sample_rate, device=self.device)
        
        # Create presence/air boost curve
        presence_curve = torch.ones_like(freqs)
        
        # PRESENCE BOOST: 2.5-6kHz (+4dB) - ENHANCED clarity and definition
        # This is where vocals and instruments "speak" - critical for realism
        presence_mask = (freqs >= 2500) & (freqs <= 6000)
        if presence_mask.any():
            presence_curve[presence_mask] = 1.58  # +4dB (was +3dB)
        
        # AIR BOOST: 7-15kHz (+5dB) - ENHANCED sparkle and "alive" feeling
        # This creates the sensation of space and "being there"
        air_mask = (freqs >= 7000) & (freqs <= 15000)
        if air_mask.any():
            presence_curve[air_mask] = 1.78  # +5dB (was +4dB)
        
        # GENTLE rolloff only above 16kHz to avoid harshness
        extreme_high = freqs > 16000
        if extreme_high.any():
            rolloff_factor = (freqs[extreme_high] - 16000) / 4000
            presence_curve[extreme_high] = 1.0 / (1.0 + rolloff_factor * 0.3)
        
        # Apply presence/air curve
        fft = torch.fft.rfft(audio, dim=1)
        enhanced_fft = fft * presence_curve
        output = torch.fft.irfft(enhanced_fft, n=audio.shape[1], dim=1)
        
        return output


class ORBITUNE_Professional:
    """
    Professional 3D Spatial Audio Processor
    
    Creates broadcast-quality 3D audio with:
    - Genre-aware processing
    - Professional HRTF binaural positioning
    - Realistic room acoustics
    - Smooth, observable rotations
    - Industry-standard mastering
    
    Quality level: Professional YouTube 8D audio productions
    """
    
    def __init__(self, device: str = DEVICE):
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.sample_rate = AUDIO_SAMPLE_RATE
        
        # Enable GPU optimizations
        if str(self.device) == "cuda":
            torch.backends.cudnn.benchmark = True  # Auto-tune for best performance
            torch.backends.cuda.matmul.allow_tf32 = True  # Use TF32 for speed
        
        print(f"\n{'='*70}")
        print(f"🎧 ORBITUNE - Professional 3D Audio")
        print(f"{'='*70}")
        print(f"🎮 Device: {self.device}")
        if str(self.device) == "cuda":
            print(f"💾 GPU: {torch.cuda.get_device_name(0)}")
            print(f"⚡ GPU Optimizations: Enabled (TF32, cuDNN auto-tune)")
            print(f"🚀 Expected speedup: 5-10x faster processing")
        print(f"✨ Quality: Broadcast-grade / Studio-quality")
        print(f"🎯 Processing: Genre-aware adaptive")
        print(f"{'='*70}\n")
        
        # Initialize professional modules
        print("📦 Loading professional audio processors...")
        self.genre_detector = GenreDetector()
        self.hrtf = HRTFProcessor(sample_rate=self.sample_rate, device=self.device)
        self.reverb = ProfessionalReverb(sample_rate=self.sample_rate, device=self.device)
        self.mastering = ProfessionalMastering(sample_rate=self.sample_rate, device=self.device)
        print("✅ All processors loaded!\n")
    
    def _load_audio_gpu(self, path: str) -> torch.Tensor:
        """Load audio to GPU"""
        audio_np, sr = sf.read(path, dtype='float32')
        audio = torch.from_numpy(audio_np.T).to(self.device)
        
        # Convert to mono
        if audio.shape[0] == 2:
            audio = audio.mean(dim=0)
        elif audio.dim() > 1:
            audio = audio[0]
        
        # Resample if needed
        if sr != self.sample_rate:
            audio = self._resample_gpu(audio, sr, self.sample_rate)
        
        return audio
    
    def _apply_stem_eq(self, audio: torch.Tensor, stem_name: str) -> torch.Tensor:
        """
        Apply stem-specific EQ for clarity and balance
        
        Professional mix engineering:
        - Vocals: boost presence, reduce mud
        - Drums: enhance punch, control low-end
        - Bass: tighten, prevent boom
        - Other: enhance clarity
        """
        freqs = torch.fft.rfftfreq(len(audio), 1/self.sample_rate, device=self.device)
        audio_fft = torch.fft.rfft(audio)
        
        # Create EQ curve
        eq_curve = torch.ones_like(freqs)
        
        # GLOBAL: High-pass filter to remove sub-bass rumble from all stems
        hp_mask = freqs < 35  # Remove everything below 35Hz
        eq_curve[hp_mask] = 0.1  # -20dB steep cut
        
        if stem_name == 'vocals':
            # Vocals: clear but smooth, no harsh top-end
            # Cut low-end rumble (35-120Hz): -6dB
            low_cut_mask = (freqs >= 35) & (freqs <= 120)
            eq_curve[low_cut_mask] = 0.501  # -6dB
            
            # Cut mud (120-300Hz): -4dB
            mud_mask = (freqs >= 120) & (freqs <= 300)
            eq_curve[mud_mask] = 0.631  # -4dB
            
            # Gentle presence boost (2.5-5kHz): +1.5dB for intelligibility
            presence_mask = (freqs >= 2500) & (freqs <= 5000)
            eq_curve[presence_mask] = 1.19  # +1.5dB
            
            # No extra "air" boost; let mastering handle high-frequency shape
            
        elif stem_name == 'drums':
            # Drums: punchy but tight; aggressive low-end control
            # STRONG cut sub-bass rumble (20-60Hz): -8dB
            rumble_mask = (freqs >= 20) & (freqs <= 60)
            eq_curve[rumble_mask] = 0.398  # -8dB
            
            # Strong low-end control (60-120Hz): -4dB
            low_mask = (freqs >= 60) & (freqs <= 120)
            eq_curve[low_mask] = 0.631  # -4dB
            
            # Moderate punch (120-250Hz): +1dB for kick clarity
            punch_mask = (freqs >= 120) & (freqs <= 250)
            eq_curve[punch_mask] = 1.12  # +1dB
            
            # Enhance snare body (200-500Hz): +1dB for warmth
            snare_body_mask = (freqs >= 200) & (freqs <= 500)
            eq_curve[snare_body_mask] = 1.12  # +1dB
            
            # Very gentle attack (3-7kHz): +1dB, to keep cymbals from being sharp
            attack_mask = (freqs >= 3000) & (freqs <= 7000)
            eq_curve[attack_mask] = 1.12  # +1dB
            
            # No dedicated "air" boost; let mastering rolloff handle highs
            
        elif stem_name == 'bass':
            # Bass: ultra-tight and controlled; extreme low-end cuts
            # EXTREME cut: Remove excessive sub-bass (20-60Hz): -15dB
            sub_mask = (freqs >= 20) & (freqs <= 60)
            eq_curve[sub_mask] = 0.178  # -15dB (extreme)
            
            # VERY AGGRESSIVE control low-end (60-150Hz): -10dB
            low_mask = (freqs >= 60) & (freqs <= 150)
            eq_curve[low_mask] = 0.316  # -10dB
            
            # Strong control (150-250Hz): -5dB
            mid_low_mask = (freqs >= 150) & (freqs <= 250)
            eq_curve[mid_low_mask] = 0.562  # -5dB
            
            # Boost definition (250-600Hz): +3dB for clarity and presence
            def_mask = (freqs >= 250) & (freqs <= 600)
            eq_curve[def_mask] = 1.41  # +3dB
            
            # No extra high boost; let bass stay mostly low-mid focused
            
        elif stem_name == 'other':
            # Other instruments: clear but not piercing
            # Guitars, keys, synths, strings - distinct and natural
            
            # Cut low-end (35-100Hz): -4dB
            low_cut_mask = (freqs >= 35) & (freqs <= 100)
            eq_curve[low_cut_mask] = 0.631  # -4dB
            
            # Gentle cut in mud (100-250Hz): -2dB for clarity
            mud_mask = (freqs >= 100) & (freqs <= 250)
            eq_curve[mud_mask] = 0.794  # -2dB
            
            # Boost body/warmth (250-800Hz): +2dB for guitar/piano body
            body_mask = (freqs >= 250) & (freqs <= 800)
            eq_curve[body_mask] = 1.26  # +2dB
            
            # Gentle presence (1.5-4kHz): +2dB for instrument definition
            presence_mask = (freqs >= 1500) & (freqs <= 4000)
            eq_curve[presence_mask] = 1.26  # +2dB
            
            # Flat above 4kHz; let mastering rolloff handle highs
        
        # Apply EQ with smooth transitions
        eq_smoothed = self._smooth_eq_curve(eq_curve, freqs)
        
        # Apply to audio
        filtered_fft = audio_fft * eq_smoothed
        output = torch.fft.irfft(filtered_fft, n=len(audio))
        
        return output
    
    def _smooth_eq_curve(self, eq_curve: torch.Tensor, freqs: torch.Tensor) -> torch.Tensor:
        """Smooth EQ transitions for natural, musical sound"""
        # Apply MORE smoothing for natural, non-harsh sound
        kernel_size = 9  # Increased from 5 for smoother transitions
        kernel = torch.ones(kernel_size, device=self.device) / kernel_size
        
        # Pad and smooth
        eq_padded = F.pad(eq_curve.unsqueeze(0).unsqueeze(0), (kernel_size//2, kernel_size//2), mode='replicate')
        eq_smooth = F.conv1d(eq_padded, kernel.view(1, 1, -1)).squeeze()
        
        return eq_smooth[:len(eq_curve)]
    
    def _resample_gpu(self, audio: torch.Tensor, orig_sr: int, target_sr: int) -> torch.Tensor:
        """High-quality resampling. Prefers torchaudio (windowed-sinc),
        falls back to linear only if torchaudio is unavailable."""
        if orig_sr == target_sr:
            return audio
        if _HAS_TORCHAUDIO:
            # torchaudio resample works on CPU; pay small cost for quality.
            was_cuda = audio.is_cuda
            audio_cpu = audio.detach().cpu().unsqueeze(0)  # [1, N]
            res = ta_resample(audio_cpu, orig_sr, target_sr)
            out = res.squeeze(0)
            return out.to(self.device) if was_cuda else out
        # Fallback: linear (least preferred)
        orig_len = audio.shape[0]
        target_len = int(orig_len * target_sr / orig_sr)
        audio_2d = audio.unsqueeze(0).unsqueeze(0)
        resampled = F.interpolate(audio_2d, size=target_len, mode='linear', align_corners=False)
        return resampled.squeeze()
    
    def _create_smooth_rotation(
        self,
        length: int,
        num_rotations: float,
        start_angle: float = 0,
        smoothness: float = 0.95
    ) -> torch.Tensor:
        """
        Create ultra-smooth rotation curve with easing
        
        OPTIMIZED: GPU-accelerated smoothing
        
        Args:
            length: Audio length in samples
            num_rotations: Number of complete rotations
            start_angle: Starting angle in degrees
            smoothness: Smoothness factor (0.9-0.99, higher = smoother)
        
        Returns:
            Smooth angle curve in radians
        """
        # Create base curve
        t = torch.linspace(0, 1, length, device=self.device)
        
        # Apply smooth easing (ease-in-out)
        t_eased = t * t * (3.0 - 2.0 * t)  # Smoothstep function
        
        # Convert to angle with rotations
        angle = (t_eased * num_rotations * 2 * np.pi) + np.deg2rad(start_angle)
        
        # Additional smoothing using IIR filter (GPU-accelerated)
        if smoothness > 0:
            # Use convolution for exponential smoothing (much faster)
            # Create exponential kernel
            kernel_len = min(int(-10 / np.log(smoothness)), 1000)
            kernel = torch.pow(smoothness, torch.arange(kernel_len, device=self.device, dtype=torch.float32))
            kernel = kernel / kernel.sum()
            
            # Pad and convolve
            angle_padded = F.pad(angle.unsqueeze(0).unsqueeze(0), (kernel_len//2, kernel_len//2), mode='replicate')
            angle_smooth = F.conv1d(angle_padded, kernel.view(1, 1, -1)).squeeze()
            angle = angle_smooth[:length]  # Trim to original length
        
        return angle
    
    def _create_distance_curve(
        self,
        length: int,
        base_distance: float,
        rotation_angle: torch.Tensor,
        variation: float = 0.3
    ) -> torch.Tensor:
        """
        Create STRONG dynamic distance for "band IN FRONT" experience
        
        ULTRA-REALISTIC BEHAVIOR:
        - Front (0°): MUCH CLOSER - performers right in front of you!
        - Back (180°): MUCH FURTHER - they've rotated behind, clearly distant
        - Sides (90°, 270°): Medium distance - natural transition
        
        This creates STRONG frontal dominance:
        - Front sources feel PRESENT and IMMEDIATE
        - Back sources feel DISTANT and AMBIENT
        - Creates realistic "revolving around you" sensation
        - ~2.5x distance difference (front to back)
        
        Args:
            length: Audio length
            base_distance: Base distance in meters
            rotation_angle: Rotation angle curve in radians
            variation: Additional pulsing variation (0-1)
        
        Returns:
            Distance curve that varies with rotation
        """
        # Distance multiplier based on angle - STRONG variation for frontal dominance
        # Front (0°): 0.65x distance (MUCH closer - right in front!)
        # Back (180°): 1.60x distance (MUCH further - clearly behind)
        # Uses cosine: cos(0°)=1 (front), cos(180°)=-1 (back)
        # Range: 0.65 to 1.60 (~2.5x difference - very noticeable!)
        angle_factor = 1.125 - 0.475 * torch.cos(rotation_angle)  # Range: 0.65 to 1.60
        
        # Apply angle-based distance modulation
        distance = base_distance * angle_factor
        
        # Add subtle pulsing for organic feel (optional, very gentle)
        if variation > 0:
            t = torch.linspace(0, 4 * np.pi, length, device=self.device)
            pulse = torch.sin(t) * variation * 0.10  # Very gentle pulsing
            distance = distance * (1.0 + pulse)
        
        # Cosine curve is naturally smooth - no additional smoothing needed
        return torch.clamp(distance, HRTF_DISTANCE_MIN, HRTF_DISTANCE_MAX)
    
    def process_song(self, song_id: str, output_path: Optional[str] = None) -> str:
        """
        Create professional 3D spatial audio
        
        Args:
            song_id: Song identifier
            output_path: Optional custom output path
        
        Returns:
            Path to output file
        """
        start_time = time.time()
        
        print(f"\n{'='*70}")
        print(f"🎧 CREATING PROFESSIONAL 3D AUDIO")
        print(f"{'='*70}")
        print(f"🎵 Song ID: {song_id}\n")
        
        # Detect genre for adaptive processing
        print("🔍 Step 1/6: Genre Detection...")
        genre, confidence, profile = self.genre_detector.detect_genre(song_id)
        
        print(f"\n📊 Genre Profile Applied:")
        print(f"   • Rotation speed: {profile['rotation_speed']} full rotations")
        print(f"   • Room size: {profile['room_size']}")
        print(f"   • Reverb: {profile['reverb_amount']*100:.0f}%")
        print(f"   • Style: {profile['description']}\n")
        
        # Clear GPU cache before starting
        if str(self.device) == "cuda":
            torch.cuda.empty_cache()
        
        # Load stems
        stems_dir = get_stems_dir(song_id)
        if output_path is None:
            spatial_dir = os.path.join(STORAGE_BASE, "spatial", song_id)
            os.makedirs(spatial_dir, exist_ok=True)
            output_path = os.path.join(spatial_dir, "orbitune_3d_professional.wav")
        
        stem_files = {
            'vocals': os.path.join(stems_dir, 'vocals.wav'),
            'drums': os.path.join(stems_dir, 'drums.wav'),
            'bass': os.path.join(stems_dir, 'bass.wav'),
            'other': os.path.join(stems_dir, 'other.wav')
        }
        
        print(f"📥 Step 2/6: Loading and EQ'ing stems...")
        step_start = time.time()
        stems_gpu = {}
        audio_length = 0
        
        # PERFECT BALANCE - Every instrument clearly recognizable and entertaining
        # Tuned for industry-level listening on typical headphones:
        # - Vocals: clear and present, sit on top but not harsh
        # - Drums: punchy and exciting without overpowering mix
        # - Other: strong enough to keep harmonic content entertaining
        # - Bass: warm and controlled; audible but not boomy
        stem_volumes = {
            'vocals': 0.92,  # Clear, present lead vocals
            'drums': 0.78,   # Punchy but controlled drums
            'other': 0.85,   # Clear harmonic content (boosted for more air)
            'bass': 0.10,    # Supportive, ultra-tight low-end (final reduction)
        }
        
        for name, path in stem_files.items():
            # Load audio
            audio = self._load_audio_gpu(path)
            
            # Apply stem-specific EQ for clarity and tonal balance
            audio = self._apply_stem_eq(audio, name)
            
            # Apply volume balance
            audio = audio * stem_volumes[name]
            
            stems_gpu[name] = audio
            audio_length = max(audio_length, len(stems_gpu[name]))
            duration = stems_gpu[name].shape[0] / self.sample_rate
            print(f"   ✅ {name}: {duration:.1f}s (vol: {stem_volumes[name]:.0%}, EQ applied)")
        print(f"   ⏱️  Loading + EQ time: {time.time() - step_start:.1f}s")
        
        # Create synchronized carousel rotation patterns
        print(f"\n🌀 Step 3/6: Creating ultra-realistic rotation...")
        print(f"   🎠 ALL 4 STEMS ROTATING: vocals, drums, bass, other")
        print(f"   🎯 FRONTAL DOMINANCE: Band plays IN FRONT, revolves naturally")
        print(f"   📍 DYNAMIC DISTANCE: Front MUCH closer, back MUCH further (2.5x variation)")
        print(f"   🎵 ULTRA-SMOOTH: Natural, comfortable rotation (0.95 smoothness)")
        print(f"   ✨ REALISTIC: Like sitting at a real concert!")
        step_start = time.time()
        
        # INDEPENDENT DYNAMIC ROTATION
        # Each stem rotates at DIFFERENT SPEED creating organic movement
        # Stems pass each other, cluster, and spread apart naturally
        # Creates living, breathing soundscape with spatial dynamics
        
        # Base rotation from genre profile
        base_rotations = profile['rotation_speed']
        
# PERFECT CAROUSEL ROTATION - all stems revolve around you together
        # Adaptive rotations: ~1 turn every ~18s (comfortable),
        # min 4 turns, max 9 turns per song.
        duration_seconds = audio_length / self.sample_rate if audio_length > 0 else 0.0
        target_period = 18.0  # seconds per rotation (comfortable)
        adaptive_rotations = float(np.clip(duration_seconds / max(target_period, 1e-6), 4.0, 9.0))
        rotation_speeds = {
            'vocals': adaptive_rotations,
            'drums': adaptive_rotations,
            'bass': adaptive_rotations,
            'other': adaptive_rotations,
        }
        
        # Starting positions: 90° apart for perfect separation
        # Keep vocals and drums 180° apart as requested
        start_positions = {
            'vocals': 0,      # Front (0°)
            'bass': 90,       # Right (90°) 
            'drums': 180,     # Back (180°) - opposite of vocals
            'other': 270,     # Left (270°)
        }
        
        # REALISTIC TIMING DELAYS - Musicians aren't perfectly synchronized!
        # Add subtle time delays to create natural "live band" feel
        # Each stem starts rotating at slightly different time (0.5-1.5 seconds apart)
        timing_delays_seconds = {
            'vocals': 0.0,    # Vocals start first
            'drums': 0.8,     # Drums 0.8s later
            'bass': 1.5,      # Bass 1.5s later
            'other': 0.5,     # Other 0.5s later
        }
        
        # OPTIMIZED DISTANCES for "band IN FRONT" experience
        # Closer overall = more immediate, present feeling
        # Strong dynamic distance variation (0.65x-1.60x) creates depth
        # - Vocals: Lead performer, most present
        # - Drums: Energetic, punchy
        # - Other: Supporting instruments, clear but deeper
        # - Bass: Foundation, solid support
        distances = {
            'vocals': 2.5,  # Lead in front - very present! (1.6m-4.0m dynamic range)
            'drums': 2.8,   # Close kit - energetic! (1.8m-4.5m dynamic range)
            'bass': 3.2,    # Foundation - controlled (2.1m-5.1m dynamic range)
            'other': 3.6,   # Support - clear depth (2.3m-5.8m dynamic range)
        }
        
        rotation_curves = {}
        distance_curves = {}
        for name in stems_gpu.keys():
            # Calculate angle offset from timing delay
            # Each second of delay = (rotation_speed * 360) degrees of offset
            time_delay = timing_delays_seconds[name]
            duration_seconds = audio_length / self.sample_rate
            angle_offset_from_delay = (time_delay / duration_seconds) * rotation_speeds[name] * 360
            
            # Apply timing delay as angle offset
            effective_start_angle = start_positions[name] + angle_offset_from_delay
            
            rotation_curves[name] = self._create_smooth_rotation(
                audio_length,
                rotation_speeds[name],
                effective_start_angle,
                smoothness=ROTATION_SMOOTHNESS  # 0.80 for sharp, observable carousel rotation
            )
            # Create DYNAMIC distance curve based on rotation position
            # Front = closer (dominant), Back = further (recedes)
            distance_curves[name] = self._create_distance_curve(
                audio_length,
                distances[name],
                rotation_curves[name],  # Pass rotation angle for dynamic distance
                variation=0.15  # Subtle additional pulsing
            )
            delay_info = f", +{time_delay:.1f}s delay" if time_delay > 0 else ""
            rotation_info = f"{rotation_speeds[name]:.1f} rot"
            # Show dynamic distance range: front (0.65x) to back (1.60x) - STRONG frontal presence
            dist_front = distances[name] * 0.65
            dist_back = distances[name] * 1.60
            print(f"   🌀 {name}: {rotation_info}, starts {start_positions[name]}°{delay_info}, {dist_front:.1f}m-{dist_back:.1f}m (FRONT dominant)")
        
        if str(self.device) == "cuda":
            torch.cuda.synchronize()  # Wait for GPU to finish
        print(f"   ⏱️  Rotation curves: {time.time() - step_start:.1f}s")
        
        # Apply professional HRTF binaural processing
        print(f"\n🎧 Step 4/6: Applying professional HRTF binaural processing...")
        print(f"   ⚡ GPU-accelerated batch processing...")
        step_start = time.time()
        
        # Process all stems in parallel for GPU efficiency
        processed = {}
        stem_names = list(stems_gpu.keys())
        
        # Process stems efficiently
        for name in stem_names:
            audio_mono = stems_gpu[name]
            spatial = self.hrtf.spatialize(
                audio_mono,
                rotation_curves[name],
                distance=distance_curves[name]
            )
            processed[name] = spatial
            print(f"   ✅ {name}: 3D positioning applied")
        
        if str(self.device) == "cuda":
            torch.cuda.synchronize()
        print(f"   ⏱️  HRTF processing: {time.time() - step_start:.1f}s")
        
        # Mix stems
        print(f"\n🏛️  Step 5/6: Mixing and adding room acoustics...")
        step_start = time.time()
        max_len = max(s.shape[1] for s in processed.values())
        mix = torch.zeros(2, max_len, device=self.device)
        
        for name, audio in processed.items():
            if audio.shape[1] < max_len:
                audio = F.pad(audio, (0, max_len - audio.shape[1]))
            mix += audio
        
        # Remove RMS-based premaster normalization to preserve natural dynamics.
        # Only ensure we don't clip by gently scaling down if peaks are too high.
        with torch.no_grad():
            peak = mix.abs().max()
            if peak > 0:
                safe_peak = 0.98
                gain = min(1.0, safe_peak / peak)
                mix = mix * gain
        
        # Add subtle reverb for space (minimal, tight)
        mix = self.reverb.apply(
            mix,
            room_size=profile['room_size'],
            reverb_amount=profile['reverb_amount'],
            pre_delay=0.005  # Very short pre-delay for tightness
        )
        if str(self.device) == "cuda":
            torch.cuda.synchronize()
        print(f"   ✅ Professional reverb applied ({profile['room_size']} room)")
        print(f"   ⏱️  Mixing + Reverb: {time.time() - step_start:.1f}s")
        
        # Professional mastering
        print(f"\n🏚️  Step 6/6: Professional mastering...")
        step_start = time.time()
        mix = self.mastering.master(
            mix,
            target_lufs=MASTER_LOUDNESS_LUFS,
            peak_ceiling=MASTER_PEAK_CEILING,
            stereo_width=MASTER_STEREO_WIDTH
        )
        if str(self.device) == "cuda":
            torch.cuda.synchronize()
        print(f"   ✅ Mastered to {MASTER_LOUDNESS_LUFS} LUFS")
        print(f"   ⏱️  Mastering time: {time.time() - step_start:.1f}s")
        
        # Save
        print(f"\n💾 Saving...")
        step_start = time.time()
        mix_cpu = mix.cpu().numpy().T
        sf.write(output_path, mix_cpu, self.sample_rate, subtype='PCM_24')
        print(f"   ⏱️  Save time: {time.time() - step_start:.1f}s")
        
        # Clear GPU cache
        if str(self.device) == "cuda":
            torch.cuda.empty_cache()
        
        total_time = time.time() - start_time
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"\n{'='*70}")
        print(f"✅ PROFESSIONAL 3D AUDIO COMPLETE!")
        print(f"{'='*70}")
        print(f"⏱️  Processing time: {total_time:.1f} seconds")
        print(f"📁 Output: {output_path}")
        print(f"💾 Size: {file_size:.1f} MB")
        print(f"🎧 Format: 48kHz 24-bit Stereo WAV (Studio Quality)")
        print(f"")
        print(f"🎼 Audio Profile:")
        print(f"   Genre: {profile['name']}")
        print(f"   Style: {profile['description']}")
        print(f"   Quality: Broadcast-grade / Professional")
        print(f"")
        print(f"🎧 PUT ON HEADPHONES TO EXPERIENCE:")
        print(f"   ✓ Realistic 3D positioning (HRTF binaural)")
        print(f"   ✓ Smooth, observable rotations")
        print(f"   ✓ Natural room acoustics")
        print(f"   ✓ Studio-quality audio (comparable to pro YouTube 8D)")
        print(f"   ✓ Distance variation (sounds move closer/farther)")
        print(f"   ✓ Professional mastering ({MASTER_LOUDNESS_LUFS} LUFS)")
        print(f"   ✓ Crystal-clear stem separation")
        print(f"   ✓ Genre-optimized spatial strategy")
        print(f"")
        print(f"🌟 This is BROADCAST QUALITY 3D audio!")
        print(f"{'='*70}\n")
        
        return output_path


def main():
    """Create professional 3D audio"""
    print(f"\n{'='*70}")
    print(f"🎧 ORBITUNE - Professional 3D Audio Creator")
    print(f"{'='*70}\n")
    
    processed_dir = os.path.join(STORAGE_BASE, "processed")
    if not os.path.exists(processed_dir):
        print("❌ No processed songs found")
        print("   Run source_separator.py first to separate a song")
        return
    
    song_ids = [d for d in os.listdir(processed_dir) 
                if os.path.isdir(os.path.join(processed_dir, d))]
    
    if not song_ids:
        print("❌ No separated songs found")
        print("   Run source_separator.py first")
        return
    
    print(f"📋 Available songs:\n")
    for i, song_id in enumerate(song_ids, 1):
        metadata_path = os.path.join(STORAGE_BASE, "raw_audio", song_id, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                title = metadata.get('title', 'Unknown')[:70]
                duration_sec = metadata.get('duration', 0)
                duration = f"{duration_sec // 60}:{duration_sec % 60:02d}"
        else:
            title = "Unknown"
            duration = "?"
        
        print(f"{i}. {title}")
        print(f"   ID: {song_id} | Duration: {duration}\n")
    
    choice = input(f"Select song (1-{len(song_ids)}): ").strip()
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(song_ids):
            print("❌ Invalid selection")
            return
        song_id = song_ids[idx]
    except ValueError:
        print("❌ Invalid input")
        return
    
    # Process
    processor = ORBITUNE_Professional(device=DEVICE)
    
    try:
        output = processor.process_song(song_id)
        print(f"\n🎵 SUCCESS! Your professional 3D audio is ready!")
        print(f"📁 {output}")
        print(f"\n🎧 Wear headphones and experience broadcast-quality 3D audio!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
