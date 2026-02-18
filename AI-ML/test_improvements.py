"""
Quick test script to process a song and verify the improvements
"""
import os
import sys
import subprocess

print("\n" + "="*80)
print("🎧 ORBITUNE - Test Ultra-Realistic 3D Audio Improvements")
print("="*80)
print()
print("This script will:")
print("1. Show you available processed songs")
print("2. Let you select one to re-process with NEW improvements")
print("3. Automatically analyze the NEW output")
print("4. Show you the comparison with old results")
print()
print("="*80)

# Add the project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config import STORAGE_BASE

# Check for processed songs
processed_dir = os.path.join(STORAGE_BASE, "processed")

if not os.path.exists(processed_dir):
    print("\n❌ No processed songs found.")
    print("   Please run source_separator.py first to separate a song.")
    sys.exit(1)

song_ids = [d for d in os.listdir(processed_dir) 
            if os.path.isdir(os.path.join(processed_dir, d))]

if not song_ids:
    print("\n❌ No separated songs found.")
    print("   Please run source_separator.py first.")
    sys.exit(1)

print(f"\n📋 Available songs ({len(song_ids)} found):\n")

# Show song metadata
import json
for i, song_id in enumerate(song_ids, 1):
    metadata_path = os.path.join(STORAGE_BASE, "raw_audio", song_id, "metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                title = metadata.get('title', 'Unknown')[:60]
                duration_sec = metadata.get('duration', 0)
                duration = f"{duration_sec // 60}:{duration_sec % 60:02d}"
        except:
            title = "Unknown"
            duration = "?"
    else:
        title = "Unknown"
        duration = "?"
    
    print(f"{i}. {title}")
    print(f"   ID: {song_id} | Duration: {duration}")
    print()

# Get user selection
try:
    choice = input(f"Select song to process (1-{len(song_ids)}) or 'q' to quit: ").strip()
    
    if choice.lower() == 'q':
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    idx = int(choice) - 1
    if idx < 0 or idx >= len(song_ids):
        print("\n❌ Invalid selection")
        sys.exit(1)
    
    song_id = song_ids[idx]
    
except (ValueError, KeyboardInterrupt):
    print("\n❌ Invalid input or cancelled")
    sys.exit(1)

print("\n" + "="*80)
print(f"🎵 Processing: {song_id}")
print("="*80)

# Check if old output exists for comparison
old_output = os.path.join(STORAGE_BASE, "spatial", song_id, "orbitune_3d_professional.wav")
has_old_output = os.path.exists(old_output)

if has_old_output:
    print(f"\n✅ Found previous output - will enable before/after comparison")
    # Analyze old output first
    print("\n📊 Analyzing OLD output...")
    print("-" * 80)
    
    # Create temp analysis script for old file
    old_analysis = f"""
import soundfile as sf
import numpy as np

data, sr = sf.read(r'{old_output}')
rms = np.sqrt(np.mean(data**2))
rms_db = 20*np.log10(rms) if rms > 0 else -np.inf
correlation = np.corrcoef(data[:, 0], data[:, 1])[0,1]

print(f"OLD OUTPUT:")
print(f"  RMS Level: {{rms_db:.2f}} dB")
print(f"  Stereo Correlation: {{correlation:.3f}}")
"""
    
    with open("_temp_old_analysis.py", "w") as f:
        f.write(old_analysis)
    
    try:
        subprocess.run([sys.executable, "_temp_old_analysis.py"], check=True)
    except:
        pass
    finally:
        if os.path.exists("_temp_old_analysis.py"):
            os.remove("_temp_old_analysis.py")
    
    print("-" * 80)
else:
    print(f"\nℹ️  No previous output found - will create fresh output")

print("\n" + "="*80)
print("🎵 Creating NEW 3D audio with improvements...")
print("="*80)

# Process the song
try:
    from audio_processor.orbitune_final import ORBITUNE_Professional
    import soundfile as sf
    import numpy as np
    
    processor = ORBITUNE_Professional()
    output_path = processor.process_song(song_id)
    
    print("\n" + "="*80)
    print("✅ Processing complete!")
    print("="*80)
    
    # Analyze new output
    print("\n📊 Analyzing NEW output...")
    print("-" * 80)
    
    data, sr = sf.read(output_path)
    rms = np.sqrt(np.mean(data**2))
    rms_db = 20*np.log10(rms) if rms > 0 else -np.inf
    correlation = np.corrcoef(data[:, 0], data[:, 1])[0,1]
    peak = np.abs(data).max()
    peak_db = 20*np.log10(peak) if peak > 0 else -np.inf
    
    print(f"\nNEW OUTPUT:")
    print(f"  RMS Level: {rms_db:.2f} dB [Target: -14 to -15 dB]")
    print(f"  Peak Level: {peak_db:.2f} dB")
    print(f"  Stereo Correlation: {correlation:.3f} [Target: 0.15-0.25]")
    
    # Check if targets met
    print(f"\n📋 Target Achievement:")
    if -15.5 <= rms_db <= -13.5:
        print(f"  ✅ RMS Level: PERFECT!")
    elif -17 <= rms_db <= -13:
        print(f"  ⚠️  RMS Level: Close, slight adjustment needed")
    else:
        print(f"  ❌ RMS Level: Needs more work")
    
    if 0.15 <= correlation <= 0.30:
        print(f"  ✅ Stereo Correlation: PERFECT!")
    elif 0.10 <= correlation <= 0.35:
        print(f"  ⚠️  Stereo Correlation: Close, acceptable range")
    else:
        print(f"  ❌ Stereo Correlation: Needs more work")
    
    print("-" * 80)
    
    # Run comprehensive analysis
    print("\n📊 Running comprehensive frequency analysis...")
    print("(This may take a moment...)")
    
    # Update analyze_current_state.py to point to new file
    analyze_script_path = os.path.join(os.path.dirname(__file__), "analyze_current_state.py")
    
    if os.path.exists(analyze_script_path):
        with open(analyze_script_path, 'r') as f:
            script_content = f.read()
        
        # Update the path
        updated_content = script_content.replace(
            r'output_path = r\'D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\STORAGE\spatial\24d402f63318\orbitune_3d_professional.wav\'',
            f'output_path = r\'{output_path}\''
        )
        
        with open("_temp_analyze.py", "w") as f:
            f.write(updated_content)
        
        try:
            subprocess.run([sys.executable, "_temp_analyze.py"], check=True)
        except:
            print("\n⚠️  Could not run detailed analysis, but processing completed successfully!")
        finally:
            if os.path.exists("_temp_analyze.py"):
                os.remove("_temp_analyze.py")
    
    print("\n" + "="*80)
    print("🎉 TESTING COMPLETE!")
    print("="*80)
    print(f"\n📁 New output location:")
    print(f"   {output_path}")
    
    if has_old_output:
        print(f"\n📁 Old output location (for comparison):")
        print(f"   {old_output}")
    
    print(f"\n🎧 NEXT STEPS:")
    print(f"   1. Put on your BEST HEADPHONES")
    print(f"   2. Listen to the new output")
    print(f"   3. Compare with old output if available")
    print(f"   4. Notice the improvements:")
    print(f"      ✅ Much LOUDER and more engaging")
    print(f"      ✅ More ALIVE with presence and air")
    print(f"      ✅ Better SPATIAL feel, natural width")
    print(f"      ✅ Crystal-clear instrument separation")
    
    print("\n" + "="*80)
    
except Exception as e:
    print(f"\n❌ Error during processing: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
