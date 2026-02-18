import numpy as np
import soundfile as sf
import sys

def analyze_audio(file_path):
    """Analyze audio quality metrics"""
    # Load audio
    audio, sr = sf.read(file_path, dtype='float32')
    
    # Calculate metrics
    peak = np.abs(audio).max()
    peak_db = 20 * np.log10(peak) if peak > 0 else -np.inf
    
    rms = np.sqrt(np.mean(audio ** 2))
    rms_db = 20 * np.log10(rms) if rms > 0 else -np.inf
    
    dynamic_range = peak_db - rms_db
    
    # Stereo correlation
    if audio.shape[1] == 2:
        left = audio[:, 0]
        right = audio[:, 1]
        correlation = np.corrcoef(left, right)[0, 1]
    else:
        correlation = 1.0
    
    # Frequency analysis
    from scipy import signal
    freqs, psd = signal.welch(audio.flatten(), fs=sr, nperseg=4096)
    
    # Calculate energy in different bands
    def energy_in_band(freqs, psd, low, high):
        mask = (freqs >= low) & (freqs < high)
        return np.sum(psd[mask])
    
    total_energy = np.sum(psd)
    bass_energy = energy_in_band(freqs, psd, 20, 250) / total_energy * 100
    mid_energy = energy_in_band(freqs, psd, 250, 4000) / total_energy * 100
    high_energy = energy_in_band(freqs, psd, 4000, 10000) / total_energy * 100
    ultra_high = energy_in_band(freqs, psd, 10000, 20000) / total_energy * 100
    
    print(f"\n{'='*70}")
    print(f"Audio Quality Analysis: {file_path.split('\\\\')[-1]}")
    print(f"{'='*70}")
    print(f"\n📊 Loudness & Dynamics:")
    print(f"   Peak: {peak:.3f} ({peak_db:.2f} dB)")
    print(f"   RMS: {rms:.3f} ({rms_db:.2f} dB)")
    print(f"   Dynamic Range: {dynamic_range:.2f} dB")
    
    print(f"\n🎧 Stereo Imaging:")
    print(f"   Stereo Correlation: {correlation:.3f}")
    print(f"   {'Natural wide stereo' if 0.0 < correlation < 0.3 else 'Moderate stereo' if correlation < 0.6 else 'Narrow stereo'}")
    
    print(f"\n🎵 Frequency Balance:")
    print(f"   Bass (20-250Hz): {bass_energy:.1f}%")
    print(f"   Mids (250-4kHz): {mid_energy:.1f}%")
    print(f"   Highs (4-10kHz): {high_energy:.1f}%")
    print(f"   Ultra-High (>10kHz): {ultra_high:.1f}%")
    
    print(f"\n✨ Processing Character:")
    if dynamic_range > 14:
        print(f"   ✅ Excellent dynamics - natural and uncompressed")
    elif dynamic_range > 12:
        print(f"   ✅ Good dynamics - balanced")
    else:
        print(f"   ⚠️  Limited dynamics - may sound compressed")
    
    if 0.05 < correlation < 0.15:
        print(f"   ✅ Wide stereo image - immersive 3D")
    elif 0.0 < correlation < 0.3:
        print(f"   ✅ Natural stereo width")
    else:
        print(f"   ⚠️  Narrow or excessive stereo")
    
    if 15 < bass_energy < 30:
        print(f"   ✅ Balanced bass - not muddy or thin")
    elif bass_energy > 30:
        print(f"   ⚠️  Heavy bass - may sound muddy")
    else:
        print(f"   ⚠️  Light bass - may sound thin")
    
    if 0.1 < ultra_high < 0.5:
        print(f"   ✅ Natural high-frequency rolloff - warm")
    elif ultra_high > 1.0:
        print(f"   ⚠️  Bright/harsh - may fatigue ears")
    else:
        print(f"   ✅ Smooth highs")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_output.py <audio_file>")
        sys.exit(1)
    
    analyze_audio(sys.argv[1])
