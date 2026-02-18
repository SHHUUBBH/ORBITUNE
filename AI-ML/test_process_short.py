"""
Quick test - process first 10 seconds only to verify the fix works
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audio_processor.orbitune_final import ORBITUNE_Professional
import soundfile as sf
import torch

print("\n" + "="*70)
print("🧪 QUICK TEST - Processing 10 second segment")
print("="*70)

# Initialize processor
processor = ORBITUNE_Professional()

# Process song (the code will load full stems but we can check output)
song_id = "2669cdc6fd87"

try:
    output_path = processor.process_song(song_id)
    print(f"\n✅ SUCCESS! Output: {output_path}")
    
    # Check output
    data, sr = sf.read(output_path)
    print(f"\n📊 Output Analysis:")
    print(f"   Shape: {data.shape}")
    print(f"   Sample rate: {sr}")
    print(f"   Duration: {len(data)/sr:.1f}s")
    print(f"   Min: {data.min():.6f}")
    print(f"   Max: {data.max():.6f}")
    print(f"   Has NaN: {(data != data).any()}")
    print(f"   All same value: {len(set(data.flatten()[:1000])) == 1}")
    
    if data.min() == data.max():
        print(f"\n❌ ERROR: Audio is flatlined at {data.min():.6f}!")
    elif (data != data).any():
        print(f"\n❌ ERROR: Audio contains NaN!")
    else:
        print(f"\n✅ Audio looks good!")
        
except Exception as e:
    print(f"\n❌ PROCESSING FAILED: {e}")
    import traceback
    traceback.print_exc()
