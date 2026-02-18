"""
Diagnostic tool to find where audio processing goes wrong
"""
import torch
import soundfile as sf
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import *
from audio_processor.hrtf_processor import HRTFProcessor

def check_tensor(tensor, name):
    """Check if tensor has any issues"""
    has_nan = torch.isnan(tensor).any().item()
    has_inf = torch.isinf(tensor).any().item()
    min_val = tensor.min().item()
    max_val = tensor.max().item()
    mean_val = tensor.mean().item()
    
    status = "✅"
    if has_nan or has_inf or abs(min_val) > 100 or abs(max_val) > 100:
        status = "❌"
    
    print(f"{status} {name:30s}: min={min_val:8.4f}, max={max_val:8.4f}, mean={mean_val:8.4f}, nan={has_nan}, inf={has_inf}")
    return not (has_nan or has_inf)

# Test with actual stems
song_id = "2669cdc6fd87"
stems_dir = f"{STORAGE_BASE}\\processed\\{song_id}"

print("="*70)
print("🔍 DIAGNOSING AUDIO PROCESSING")
print("="*70)

# Load one stem
vocals_path = os.path.join(stems_dir, "vocals.wav")
print(f"\n📥 Loading: {vocals_path}")
audio_np, sr = sf.read(vocals_path, dtype='float32')
print(f"   Shape: {audio_np.shape}, SR: {sr}")

# Convert to mono tensor
if len(audio_np.shape) > 1:
    audio_np = audio_np.mean(axis=1)
audio = torch.from_numpy(audio_np).cuda() if torch.cuda.is_available() else torch.from_numpy(audio_np)

check_tensor(audio, "1. Original audio")

# Test HRTF processing
print("\n🎧 Testing HRTF processing...")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
hrtf = HRTFProcessor(sample_rate=48000, device=device)

# Create simple rotation (like the real code)
length = len(audio)
t = torch.linspace(0, 1, length, device=audio.device)
num_rotations = 2.0
azimuth = t * num_rotations * 2 * np.pi
check_tensor(azimuth, "2. Azimuth curve")

# Create distance
distance = torch.full_like(azimuth, 2.0)
check_tensor(distance, "3. Distance curve")

# Apply HRTF
try:
    print("   Applying HRTF spatialize...")
    spatial = hrtf.spatialize(audio, azimuth, distance=distance)
    check_tensor(spatial, "4. After HRTF")
    
    # Check each channel
    check_tensor(spatial[0], "4a. Left channel")
    check_tensor(spatial[1], "4b. Right channel")
    
except Exception as e:
    print(f"❌ HRTF FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("✅ Diagnostic complete! Check values above for issues.")
print("="*70)
