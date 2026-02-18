"""
Comprehensive audio quality analysis
"""
import soundfile as sf
import numpy as np

output_path = r'D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\STORAGE\spatial\2669cdc6fd87\orbitune_3d_professional.wav'

print("\n" + "="*70)
print("🔍 COMPREHENSIVE AUDIO QUALITY ANALYSIS")
print("="*70)

# Load audio
data, sr = sf.read(output_path)
print(f"\n📊 Basic Info:")
print(f"   Sample Rate: {sr} Hz")
print(f"   Duration: {len(data)/sr:.1f} seconds")
print(f"   Channels: {data.shape[1]}")
print(f"   Shape: {data.shape}")

# Amplitude analysis
print(f"\n📈 Amplitude Analysis:")
print(f"   Peak: {np.abs(data).max():.6f} ({20*np.log10(np.abs(data).max()):.2f} dB)")
print(f"   RMS: {np.sqrt(np.mean(data**2)):.6f} ({20*np.log10(np.sqrt(np.mean(data**2))):.2f} dB)")
print(f"   Dynamic Range: {20*np.log10(np.abs(data).max() / (np.sqrt(np.mean(data**2)) + 1e-10)):.2f} dB")
print(f"   Crest Factor: {np.abs(data).max() / (np.sqrt(np.mean(data**2)) + 1e-10):.2f}")

# Stereo analysis
left = data[:, 0]
right = data[:, 1]
print(f"\n🎧 Stereo Analysis:")
print(f"   Left RMS: {np.sqrt(np.mean(left**2)):.6f}")
print(f"   Right RMS: {np.sqrt(np.mean(right**2)):.6f}")
print(f"   Balance: {100 * (np.sqrt(np.mean(left**2)) / (np.sqrt(np.mean(right**2)) + 1e-10) - 1):.1f}%")
print(f"   Correlation: {np.corrcoef(left, right)[0,1]:.3f}")

# Frequency analysis (take 10-second segment from middle)
segment_start = len(data) // 2
segment = data[segment_start:segment_start + sr*10].mean(axis=1)

fft = np.fft.rfft(segment)
freqs = np.fft.rfftfreq(len(segment), 1/sr)
magnitude = np.abs(fft)

# Analyze frequency bands
def band_energy(freqs, magnitude, low, high):
    mask = (freqs >= low) & (freqs <= high)
    return np.sqrt(np.mean(magnitude[mask]**2)) if mask.any() else 0

sub_bass = band_energy(freqs, magnitude, 20, 60)
bass = band_energy(freqs, magnitude, 60, 250)
low_mid = band_energy(freqs, magnitude, 250, 500)
mid = band_energy(freqs, magnitude, 500, 2000)
high_mid = band_energy(freqs, magnitude, 2000, 6000)
high = band_energy(freqs, magnitude, 6000, 20000)

total_energy = np.sqrt(np.mean(magnitude**2))

print(f"\n🎵 Frequency Balance (% of total energy):")
print(f"   Sub-Bass (20-60Hz):   {100*sub_bass/total_energy:5.1f}% {'⚠️ TOO HIGH' if sub_bass/total_energy > 0.15 else '✅'}")
print(f"   Bass (60-250Hz):      {100*bass/total_energy:5.1f}% {'⚠️ TOO HIGH' if bass/total_energy > 0.25 else '✅'}")
print(f"   Low-Mid (250-500Hz):  {100*low_mid/total_energy:5.1f}% {'✅' if low_mid/total_energy > 0.10 else '⚠️ TOO LOW'}")
print(f"   Mid (500-2000Hz):     {100*mid/total_energy:5.1f}% {'✅' if mid/total_energy > 0.15 else '⚠️ TOO LOW'}")
print(f"   High-Mid (2-6kHz):    {100*high_mid/total_energy:5.1f}% {'✅' if high_mid/total_energy > 0.15 else '⚠️ TOO LOW'}")
print(f"   High (6-20kHz):       {100*high/total_energy:5.1f}% {'✅' if high/total_energy > 0.10 else '⚠️ TOO LOW'}")

# Bass assessment
bass_total = sub_bass + bass
mids_highs = mid + high_mid + high
bass_ratio = bass_total / (mids_highs + 1e-10)

print(f"\n🔊 Mix Balance:")
print(f"   Bass vs Mids/Highs Ratio: {bass_ratio:.2f}")
if bass_ratio > 0.8:
    print(f"   ⚠️ MIX IS BASS-HEAVY! (should be < 0.8)")
elif bass_ratio < 0.4:
    print(f"   ⚠️ Mix is too thin (should be > 0.4)")
else:
    print(f"   ✅ Well-balanced mix!")

# Clipping check
clipping = (np.abs(data) >= 0.99).sum()
print(f"\n⚠️  Clipping Analysis:")
print(f"   Samples at/near clipping (>0.99): {clipping}")
if clipping > 0:
    print(f"   ⚠️ CLIPPING DETECTED!")
else:
    print(f"   ✅ No clipping")

# Check for DC offset
dc_offset_l = np.mean(left)
dc_offset_r = np.mean(right)
print(f"\n📍 DC Offset:")
print(f"   Left: {dc_offset_l:.6f}")
print(f"   Right: {dc_offset_r:.6f}")
if abs(dc_offset_l) > 0.001 or abs(dc_offset_r) > 0.001:
    print(f"   ⚠️ Significant DC offset detected")
else:
    print(f"   ✅ Minimal DC offset")

print("\n" + "="*70)
print("✅ Analysis Complete!")
print("="*70 + "\n")
