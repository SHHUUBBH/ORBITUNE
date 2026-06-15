import soundfile as sf
import numpy as np

output_path = r'D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\STORAGE\spatial\2669cdc6fd87\orbitune_3d_professional.wav'
data, sr = sf.read(output_path)

# Frequency analysis
segment_start = len(data) // 2
segment = data[segment_start:segment_start + sr*10].mean(axis=1)

fft = np.fft.rfft(segment)
freqs = np.fft.rfftfreq(len(segment), 1/sr)
magnitude = np.abs(fft)

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

print("\nFrequency Balance:")
print(f"Sub-Bass (20-60Hz):  {100*sub_bass/total_energy:5.1f}%")
print(f"Bass (60-250Hz):     {100*bass/total_energy:5.1f}%")
print(f"Low-Mid (250-500Hz): {100*low_mid/total_energy:5.1f}%")
print(f"Mid (500-2000Hz):    {100*mid/total_energy:5.1f}%")
print(f"High-Mid (2-6kHz):   {100*high_mid/total_energy:5.1f}%")
print(f"High (6-20kHz):      {100*high/total_energy:5.1f}%")

bass_total = sub_bass + bass
mids_highs = mid + high_mid + high
bass_ratio = bass_total / (mids_highs + 1e-10)

print(f"\nBass vs Mids/Highs Ratio: {bass_ratio:.2f}")
if bass_ratio > 0.8:
    print("STATUS: BASS-HEAVY (should be < 0.8)")
elif bass_ratio < 0.4:
    print("STATUS: Too thin (should be > 0.4)")
else:
    print("STATUS: Well-balanced!")

print(f"\nRMS: {np.sqrt(np.mean(data**2)):.4f}")
print(f"Peak: {np.abs(data).max():.4f}")
