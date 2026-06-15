import soundfile as sf
import numpy as np
import torch

# Load reference audio
print("Loading reference audio...")
audio, sr = sf.read(r'D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\STORAGE\orbitune_final.wav')
print(f"Sample Rate: {sr} Hz")
print(f"Duration: {len(audio)/sr:.1f}s")
print(f"Channels: {audio.shape[1] if audio.ndim > 1 else 1}")
print(f"Shape: {audio.shape}\n")

# Convert to mono for analysis
if audio.ndim > 1:
    audio_mono = audio.mean(axis=1)
else:
    audio_mono = audio

# Basic amplitude analysis
peak = np.abs(audio).max()
rms = np.sqrt(np.mean(audio**2))
lufs_estimate = 20 * np.log10(rms) - 0.691

print("=" * 70)
print("📊 AMPLITUDE ANALYSIS")
print("=" * 70)
print(f"Peak: {peak:.6f} ({20*np.log10(peak):.2f} dB)")
print(f"RMS: {rms:.6f} ({20*np.log10(rms):.2f} dB)")
print(f"Estimated LUFS: {lufs_estimate:.1f}")
print(f"Dynamic Range: {20*np.log10(peak/rms):.2f} dB")
print(f"Headroom: {20*np.log10(1.0/peak):.2f} dB\n")

# Stereo analysis
if audio.ndim > 1:
    left_rms = np.sqrt(np.mean(audio[:, 0]**2))
    right_rms = np.sqrt(np.mean(audio[:, 1]**2))
    correlation = np.corrcoef(audio[:, 0], audio[:, 1])[0, 1]
    
    print("=" * 70)
    print("🎧 STEREO ANALYSIS")
    print("=" * 70)
    print(f"Left RMS: {left_rms:.6f}")
    print(f"Right RMS: {right_rms:.6f}")
    print(f"Balance: {abs(left_rms - right_rms) / max(left_rms, right_rms) * 100:.1f}%")
    print(f"Correlation: {correlation:.3f}")
    print()

# Frequency analysis
print("=" * 70)
print("🎵 FREQUENCY ANALYSIS")
print("=" * 70)

# Use GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
audio_tensor = torch.from_numpy(audio_mono).to(device)

# FFT analysis
fft = torch.fft.rfft(audio_tensor)
magnitude = torch.abs(fft)
freqs = torch.fft.rfftfreq(len(audio_tensor), 1/sr)

# Move to CPU for numpy operations
magnitude_np = magnitude.cpu().numpy()
freqs_np = freqs.cpu().numpy()

# Calculate energy in frequency bands
def get_band_energy(freqs, magnitude, f_low, f_high):
    mask = (freqs >= f_low) & (freqs <= f_high)
    return np.sum(magnitude[mask]**2)

total_energy = np.sum(magnitude_np**2)

bands = {
    'Sub-Bass (20-60Hz)': (20, 60),
    'Bass (60-250Hz)': (60, 250),
    'Low-Mid (250-500Hz)': (250, 500),
    'Mid (500-2000Hz)': (500, 2000),
    'High-Mid (2-6kHz)': (2000, 6000),
    'High (6-20kHz)': (6000, 20000),
}

print("\nFrequency Balance (% of total energy):")
bass_energy = 0
mid_high_energy = 0

for band_name, (f_low, f_high) in bands.items():
    energy = get_band_energy(freqs_np, magnitude_np, f_low, f_high)
    percentage = (energy / total_energy) * 100
    print(f"{band_name:25s} {percentage:6.1f}%")
    
    if f_high <= 250:
        bass_energy += energy
    else:
        mid_high_energy += energy

bass_ratio = bass_energy / mid_high_energy
print(f"\nBass vs Mids/Highs Ratio: {bass_ratio:.2f}")
if bass_ratio > 0.8:
    print(f"STATUS: BASS-HEAVY (> 0.8)")
elif bass_ratio < 0.3:
    print(f"STATUS: BRIGHT/THIN (< 0.3)")
else:
    print(f"STATUS: BALANCED (0.3-0.8)")

# Spectral characteristics
spectral_centroid = np.sum(freqs_np * magnitude_np) / np.sum(magnitude_np)
print(f"\nSpectral Centroid: {spectral_centroid:.0f} Hz")
if spectral_centroid < 1000:
    print("Character: DARK/WARM")
elif spectral_centroid < 2000:
    print("Character: BALANCED")
else:
    print("Character: BRIGHT/AIRY")

# High frequency rolloff analysis
high_freq_mask = freqs_np > 10000
high_freq_energy = np.sum(magnitude_np[high_freq_mask]**2)
high_freq_percentage = (high_freq_energy / total_energy) * 100
print(f"\nHigh Frequency Content (>10kHz): {high_freq_percentage:.2f}%")
if high_freq_percentage < 1:
    print("High-end: ROLLED OFF (lo-fi/vintage)")
elif high_freq_percentage < 5:
    print("High-end: MODERATE (natural)")
else:
    print("High-end: EXTENDED (bright/modern)")

print("\n" + "=" * 70)
print("✅ ANALYSIS COMPLETE!")
print("=" * 70)
