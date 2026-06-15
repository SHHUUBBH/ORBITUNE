"""
Detailed HRTF diagnostic - find exact source of NaN
"""
import torch
import soundfile as sf
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import *

def check(tensor, name):
    """Quick check"""
    has_nan = torch.isnan(tensor).any().item()
    has_inf = torch.isinf(tensor).any().item()
    status = "❌" if (has_nan or has_inf) else "✅"
    print(f"{status} {name:40s}: min={tensor.min():.4f}, max={tensor.max():.4f}, nan={has_nan}, inf={has_inf}")
    return not (has_nan or has_inf)

# Load test audio (short segment for speed)
song_id = "2669cdc6fd87"
vocals_path = f"{STORAGE_BASE}\\processed\\{song_id}\\vocals.wav"
audio_np, sr = sf.read(vocals_path, dtype='float32')

# Convert to mono and take first 1 second only
if len(audio_np.shape) > 1:
    audio_np = audio_np.mean(axis=1)
audio_np = audio_np[:48000]  # 1 second at 48kHz

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
audio = torch.from_numpy(audio_np).to(device)

print("="*70)
print("🔍 DETAILED HRTF DIAGNOSTIC")
print("="*70)
check(audio, "Input audio")

# Create curves
length = len(audio)
t = torch.linspace(0, 1, length, device=device)
azimuth = t * 2.0 * 2 * np.pi  # 2 rotations
distance = torch.full((length,), 2.0, device=device)
elevation = torch.zeros(length, device=device)

check(azimuth, "Azimuth")
check(distance, "Distance")
check(elevation, "Elevation")

print("\n--- Distance Effects ---")
# Distance attenuation
distance_clamped = torch.clamp(distance, min=0.3, max=50.0)
attenuation = 1.0 / distance_clamped
attenuation = attenuation / 0.5
attenuation = torch.clamp(attenuation, 0.0, 3.0)
check(attenuation, "Attenuation")

audio_att = audio * attenuation
check(audio_att, "After attenuation")

# Air absorption
avg_distance = distance.mean().item()
absorption_factor = min(avg_distance / 10.0, 1.0)
print(f"   Absorption factor: {absorption_factor:.4f}")

if absorption_factor >= 0.1:
    cutoff = 12000 * (1.0 - absorption_factor * 0.6)
    print(f"   Cutoff freq: {cutoff:.1f} Hz")
    
    freqs = torch.fft.rfftfreq(len(audio_att), 1/48000, device=device)
    check(freqs, "Frequencies")
    
    H = 1.0 / torch.sqrt(1.0 + (freqs / cutoff) ** 4)
    check(H, "Filter H")
    
    audio_fft = torch.fft.rfft(audio_att)
    check(torch.abs(audio_fft), "FFT magnitude")
    
    filtered_fft = audio_fft * H
    check(torch.abs(filtered_fft), "Filtered FFT magnitude")
    
    audio_abs = torch.fft.irfft(filtered_fft, n=len(audio_att))
    check(audio_abs, "After air absorption")
else:
    audio_abs = audio_att
    print("   Skipping air absorption (distance too close)")

print("\n--- ITD Calculation ---")
azimuth_horizontal = azimuth * torch.cos(elevation)
check(azimuth_horizontal, "Azimuth horizontal")

theta = azimuth_horizontal - np.pi/2
check(theta, "Theta")

head_radius = 0.0875
speed_of_sound = 343.0
itd_seconds = (head_radius / speed_of_sound) * (torch.sin(theta) + theta)
check(itd_seconds, "ITD seconds")

itd_samples = itd_seconds * 48000 * 2.0  # 2x multiplier
check(itd_samples, "ITD samples")

itd_samples = torch.clamp(itd_samples, -60, 60)
check(itd_samples, "ITD clamped")

print("\n--- ILD Calculation ---")
pan = torch.sin(azimuth)
check(pan, "Pan")

pan_angle = (pan + 1.0) * np.pi / 4
check(pan_angle, "Pan angle")

left_gain = torch.clamp(torch.cos(pan_angle), min=0.0) ** 0.7
right_gain = torch.clamp(torch.sin(pan_angle), min=0.0) ** 0.7
check(left_gain, "Left gain (before power)")
check(right_gain, "Right gain (before power)")

left_gain = left_gain ** 0.8
right_gain = right_gain ** 0.8
check(left_gain, "Left gain (after power)")
check(right_gain, "Right gain (after power)")

left_gain = torch.clamp(left_gain, 0.05, 1.0)
right_gain = torch.clamp(right_gain, 0.05, 1.0)
check(left_gain, "Left gain (clamped)")
check(right_gain, "Right gain (clamped)")

total = torch.sqrt(left_gain**2 + right_gain**2)
check(total, "Total (before normalize)")

left_gain = left_gain / total
right_gain = right_gain / total
check(left_gain, "Left gain (normalized)")
check(right_gain, "Right gain (normalized)")

print("\n--- Time Varying Delay ---")
# Test delay application
indices = torch.arange(len(audio_abs), device=device, dtype=torch.float32)
check(indices, "Indices")

read_pos = indices - itd_samples
check(read_pos, "Read positions")

read_pos = torch.clamp(read_pos, 0, len(audio_abs) - 1.001)
check(read_pos, "Read positions (clamped)")

pos_int = read_pos.long()
pos_frac = read_pos - pos_int.float()
check(pos_int.float(), "Position integer part")
check(pos_frac, "Position fractional part")

pos_int = torch.clamp(pos_int, 0, len(audio_abs) - 2)
pos_int_next = pos_int + 1

samples = audio_abs[pos_int] * (1 - pos_frac) + audio_abs[pos_int_next] * pos_frac
check(samples, "Interpolated samples")

left_delayed = samples * left_gain
check(left_delayed, "Left with delay and gain")

print("\n" + "="*70)
print("✅ Diagnostic complete!")
print("="*70)
