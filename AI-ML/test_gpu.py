import torch

print("="*60)
print("GPU VERIFICATION TEST")
print("="*60)
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")

if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    print(f"GPU Count: {torch.cuda.device_count()}")
    
    # Test GPU computation
    print("\n" + "="*60)
    print("TESTING GPU COMPUTATION...")
    print("="*60)
    
    # Create tensor on GPU
    x = torch.randn(1000, 1000).cuda()
    y = torch.randn(1000, 1000).cuda()
    
    # Perform computation
    z = torch.matmul(x, y)
    
    print(f"✅ GPU computation successful!")
    print(f"Result tensor shape: {z.shape}")
    print(f"Result tensor device: {z.device}")
    
    print("\n" + "="*60)
    print("🚀 GPU IS READY FOR AUDIO PROCESSING!")
    print("="*60)
else:
    print("❌ CUDA not available. Using CPU only.")
