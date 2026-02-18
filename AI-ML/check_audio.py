import soundfile as sf
import numpy as np
import os

# Check stems
print("=== CHECKING SOURCE STEMS ===")
stems_dir = r'D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\STORAGE\stems\2669cdc6fd87'
for stem in ['vocals', 'drums', 'bass', 'other']:
    path = os.path.join(stems_dir, f'{stem}.wav')
    if os.path.exists(path):
        data, sr = sf.read(path)
        if len(data.shape) > 1:
            data = data.mean(axis=1)
        print(f"{stem:10s}: max={np.abs(data).max():.6f}, rms={np.sqrt(np.mean(data**2)):.6f}, duration={len(data)/sr:.1f}s")
    else:
        print(f'{stem}: NOT FOUND')

# Check output
print("\n=== CHECKING OUTPUT FILE ===")
output_path = r'D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\STORAGE\spatial\2669cdc6fd87\orbitune_3d_professional.wav'
data, sr = sf.read(output_path)
print(f"Shape: {data.shape}")
print(f"Sample rate: {sr}")
print(f"Duration: {len(data)/sr:.1f}s")
print(f"Min: {data.min():.6f}")
print(f"Max: {data.max():.6f}")
print(f"Mean: {data.mean():.6f}")
print(f"Std: {data.std():.6f}")
print(f"Unique values: {len(np.unique(data))}")
print(f"First 10 samples: {data[:10, 0]}")
