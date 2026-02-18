"""
Comprehensive audio quality analysis - Current state check
"""
import soundfile as sf
import numpy as np
import sys

output_path = r'D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\STORAGE\spatial\24d402f63318\orbitune_3d_professional.wav'

print("\n" + "="*80)
print("🔍 ORBITUNE - CURRENT QUALITY STATE ANALYSIS")
print("="*80)

try:
    # Load audio
    data, sr = sf.read(output_path)
    print(f"\n📊 Basic Info:")
    print(f"   Sample Rate: {sr} Hz")
    print(f"   Duration: {len(data)/sr:.1f} seconds")
    print(f"   Channels: {data.shape[1]}")
    
    # Amplitude analysis
    peak = np.abs(data).max()
    rms = np.sqrt(np.mean(data**2))
    peak_db = 20*np.log10(peak) if peak > 0 else -np.inf
    rms_db = 20*np.log10(rms) if rms > 0 else -np.inf
    
    print(f"\n📈 Amplitude Analysis:")
    print(f"   Peak: {peak:.6f} ({peak_db:.2f} dB)")
    print(f"   RMS: {rms:.6f} ({rms_db:.2f} dB)")
    print(f"   Dynamic Range: {peak_db - rms_db:.2f} dB")
    
    # Stereo analysis
    left = data[:, 0]
    right = data[:, 1]
    correlation = np.corrcoef(left, right)[0,1]
    
    print(f"\n🎧 Stereo Analysis:")
    print(f"   Left RMS: {np.sqrt(np.mean(left**2)):.6f}")
    print(f"   Right RMS: {np.sqrt(np.mean(right**2)):.6f}")
    print(f"   Correlation: {correlation:.3f}")
    
    # Status checks
    if correlation < 0.05:
        print(f"   ⚠️ VERY LOW correlation - might indicate phase issues")
    elif correlation < 0.15:
        print(f"   ⚠️ Low correlation - check stereo width")
    elif correlation < 0.50:
        print(f"   ✅ Good spatial width")
    else:
        print(f"   ℹ️  Narrow stereo image")
    
    # Frequency analysis (10-second segment from middle)
    segment_start = len(data) // 2
    segment_len = min(sr*10, len(data) - segment_start)
    segment = data[segment_start:segment_start + segment_len].mean(axis=1)
    
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
    
    # Calculate percentages
    sub_bass_pct = 100*sub_bass/total_energy
    bass_pct = 100*bass/total_energy
    low_mid_pct = 100*low_mid/total_energy
    mid_pct = 100*mid/total_energy
    high_mid_pct = 100*high_mid/total_energy
    high_pct = 100*high/total_energy
    
    print(f"\n🎵 Frequency Balance (% of total energy):")
    print(f"   Sub-Bass (20-60Hz):   {sub_bass_pct:5.1f}%  [Target: 5-8%]   {'✅' if 5 <= sub_bass_pct <= 8 else '⚠️'}")
    print(f"   Bass (60-250Hz):      {bass_pct:5.1f}%  [Target: 15-20%] {'✅' if 15 <= bass_pct <= 20 else '⚠️'}")
    print(f"   Low-Mid (250-500Hz):  {low_mid_pct:5.1f}%  [Target: 18-22%] {'✅' if 18 <= low_mid_pct <= 22 else '⚠️'}")
    print(f"   Mid (500-2000Hz):     {mid_pct:5.1f}%  [Target: 25-30%] {'✅' if 25 <= mid_pct <= 30 else '⚠️'}")
    print(f"   High-Mid (2-6kHz):    {high_mid_pct:5.1f}%  [Target: 20-25%] {'✅' if 20 <= high_mid_pct <= 25 else '⚠️'}")
    print(f"   High (6-20kHz):       {high_pct:5.1f}%  [Target: 15-20%] {'✅' if 15 <= high_pct <= 20 else '⚠️'}")
    
    # Bass assessment
    bass_total = sub_bass + bass
    mids_highs = mid + high_mid + high
    bass_ratio = bass_total / (mids_highs + 1e-10)
    
    print(f"\n🔊 Mix Balance:")
    print(f"   Combined Bass (sub+bass): {100*(sub_bass + bass)/total_energy:.1f}%")
    print(f"   Bass-to-Mids/Highs Ratio: {bass_ratio:.2f}  [Target: 0.5-0.7]")
    
    if bass_ratio > 0.8:
        print(f"   ❌ CATASTROPHIC - Bass too high!")
    elif bass_ratio > 0.7:
        print(f"   ⚠️  Bass slightly high")
    elif bass_ratio < 0.4:
        print(f"   ⚠️  Bass too thin")
    elif bass_ratio < 0.5:
        print(f"   ⚠️  Bass slightly thin")
    else:
        print(f"   ✅ Well-balanced!")
    
    # Loudness assessment
    print(f"\n📢 Loudness Assessment:")
    print(f"   RMS Level: {rms_db:.2f} dB  [Target: -15 to -14 dB]")
    
    if rms_db < -19:
        print(f"   ❌ TOO QUIET - needs boost!")
    elif rms_db < -16:
        print(f"   ⚠️  Slightly quiet")
    elif rms_db > -13:
        print(f"   ⚠️  Slightly loud")
    else:
        print(f"   ✅ Good level!")
    
    # High-frequency energy check
    hf_energy_pct = 100 * (high_mid + high) / total_energy
    print(f"\n✨ High-Frequency Energy:")
    print(f"   Total HF (2kHz+): {hf_energy_pct:.1f}%  [Target: 35-45%]")
    
    if hf_energy_pct < 30:
        print(f"   ❌ TOO LOW - lacks air and presence!")
    elif hf_energy_pct < 35:
        print(f"   ⚠️  Slightly dull")
    elif hf_energy_pct > 50:
        print(f"   ⚠️  Slightly bright/harsh")
    else:
        print(f"   ✅ Good sparkle!")
    
    # Overall assessment
    print(f"\n" + "="*80)
    print(f"📋 OVERALL ASSESSMENT")
    print(f"="*80)
    
    issues = []
    
    if bass_ratio > 0.8:
        issues.append("❌ CRITICAL: Bass catastrophe - needs major reduction")
    elif bass_ratio > 0.7:
        issues.append("⚠️  Bass slightly high - minor adjustments needed")
    
    if rms_db < -19:
        issues.append("❌ CRITICAL: Too quiet - loudness normalization not working")
    elif rms_db < -16:
        issues.append("⚠️  Slightly quiet - could boost more")
    
    if hf_energy_pct < 30:
        issues.append("❌ CRITICAL: Lacks air/presence - needs HF boost")
    elif hf_energy_pct < 35:
        issues.append("⚠️  Slightly dull - minor HF boost needed")
    
    if correlation < 0.05:
        issues.append("❌ CRITICAL: Stereo correlation too low - phase issues")
    elif correlation < 0.15:
        issues.append("⚠️  Stereo correlation low - check width")
    
    if not issues:
        print("✅ ALL PARAMETERS WITHIN TARGET RANGES!")
        print("🎉 Audio quality is EXCELLENT!")
    else:
        print("Issues found:")
        for issue in issues:
            print(f"   {issue}")
    
    # Determine phase
    print(f"\n" + "="*80)
    print(f"🎯 CURRENT PHASE DETERMINATION")
    print(f"="*80)
    
    critical_issues = [i for i in issues if i.startswith("❌")]
    
    if bass_ratio > 1.5:
        print("📍 Status: Phase 1 - Bass reduction NOT IMPLEMENTED")
        print("   Next: Implement aggressive bass control")
    elif rms_db < -19 and bass_ratio > 0.7:
        print("📍 Status: Phase 1 - Bass reduction PARTIAL")
        print("   Next: Complete Phase 1, then move to Phase 2/3")
    elif hf_energy_pct < 30:
        print("📍 Status: Phase 2 - High-frequency restoration needed")
        print("   Next: Add presence and air boosts")
    elif rms_db < -16:
        print("📍 Status: Phase 3 - Loudness normalization needs fixing")
        print("   Next: Enable proper boost in normalization")
    elif critical_issues:
        print("📍 Status: Multiple critical issues - systematic overhaul needed")
        print("   Next: Work through phases 1-3 systematically")
    else:
        print("📍 Status: Fine-tuning phase - minor adjustments")
        print("   Next: Optimize and polish")
    
    print(f"\n" + "="*80)
    
except FileNotFoundError:
    print(f"\n❌ File not found: {output_path}")
    print(f"   Please process a song first using orbitune_final.py")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error analyzing audio: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
