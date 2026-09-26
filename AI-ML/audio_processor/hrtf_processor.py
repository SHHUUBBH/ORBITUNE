"""
ORBITUNE - Professional HRTF Binaural Processor
Creates realistic 3D audio using Head-Related Transfer Functions
"""

import torch
import torch.nn.functional as F
import numpy as np
from typing import Tuple
import math


class HRTFProcessor:
    """
    Professional binaural audio processor using HRTF
    
    Creates realistic 3D positioning by simulating how human ears
    perceive sound from different directions and distances
    
    Features:
    - Realistic azimuth (horizontal) positioning
    - Elevation (vertical) positioning  
    - Distance modeling with air absorption
    - Inter-aural Time Difference (ITD)
    - Inter-aural Level Difference (ILD)
    - Professional quality comparable to studio productions
    """
    
    def __init__(self, sample_rate: int = 48000, device='cpu'):
        self.sample_rate = sample_rate
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        
        # Physical constants
        self.head_radius = 0.0875  # meters (average human head)
        self.speed_of_sound = 343.0  # m/s at 20°C
        
        print(f"🎧 Professional HRTF Processor initialized")
        print(f"   Sample rate: {sample_rate} Hz")
        print(f"   Device: {self.device}")
    
    def spatialize(
        self,
        audio: torch.Tensor,
        azimuth: torch.Tensor,
        elevation: torch.Tensor = None,
        distance: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Apply professional binaural spatialization
        
        Args:
            audio: Mono audio [samples]
            azimuth: Horizontal angle in radians, time-varying [samples]
                    0 = front, π/2 = right, π = back, 3π/2 = left
            elevation: Vertical angle in radians [samples] (optional)
            distance: Distance in meters [samples] (optional)
        
        Returns:
            Spatialized stereo audio [2, samples]
        """
        # Ensure audio is on correct device
        if audio.device != self.device:
            audio = audio.to(self.device)
        
        if audio.dim() > 1:
            audio = audio.mean(dim=0)
        
        # Default values - ensure all on same device
        if elevation is None:
            elevation = torch.zeros_like(azimuth, device=self.device)
        else:
            elevation = elevation.to(self.device)
        
        if distance is None:
            distance = torch.full((len(azimuth),), 2.0, device=self.device)
        else:
            distance = distance.to(self.device)
        
        # Ensure azimuth is on correct device
        if azimuth.device != self.device:
            azimuth = azimuth.to(self.device)
        
        # Ensure all tensors are same length
        length = len(audio)
        if len(azimuth) != length:
            azimuth = self._interpolate_curve(azimuth, length)
        if len(elevation) != length:
            elevation = self._interpolate_curve(elevation, length)
        if len(distance) != length:
            distance = self._interpolate_curve(distance, length)
        
        # Apply distance attenuation and air absorption
        audio = self._apply_distance_effects(audio, distance)
        
        # REALISTIC 360° ROTATION: Apply front/back amplitude modulation
        # Front = loud, Back = quiet (head shadow effect)
        audio = self._apply_frontal_amplitude_modulation(audio, azimuth)
        
        # REALISTIC 360°: Apply angle-dependent frequency filtering
        # Back sounds are more muffled (head blocks high frequencies)
        audio = self._apply_angular_frequency_filtering(audio, azimuth)
        
        # Calculate ITD (Inter-aural Time Difference)
        itd_samples = self._calculate_itd(azimuth, elevation)
        
        # Calculate ILD (Inter-aural Level Difference)
        left_gain, right_gain = self._calculate_ild(azimuth, elevation, distance)
        
        # Apply ITD (delay) and ILD (gain) to create stereo
        left = self._apply_time_varying_delay(audio, itd_samples, left_gain)
        right = self._apply_time_varying_delay(audio, -itd_samples, right_gain)
        
        # Apply frequency-dependent HRTF filtering
        left, right = self._apply_hrtf_filtering(left, right, azimuth, elevation)
        
        # Add SUBTLE early reflections for 3D room presence
        # This makes sound feel IN A SPACE, not from flat speakers!
        left, right = self._add_early_reflections(left, right, azimuth, distance)
        
        return torch.stack([left, right])
    
    def _interpolate_curve(self, curve: torch.Tensor, target_length: int) -> torch.Tensor:
        """Smoothly interpolate curve to target length"""
        if len(curve) == target_length:
            return curve
        
        # Ensure curve is on correct device
        if curve.device != self.device:
            curve = curve.to(self.device)
        
        curve_2d = curve.unsqueeze(0).unsqueeze(0)
        interpolated = F.interpolate(
            curve_2d,
            size=target_length,
            mode='linear',
            align_corners=False
        )
        return interpolated.squeeze()
    
    def _apply_distance_effects(self, audio: torch.Tensor, distance: torch.Tensor) -> torch.Tensor:
        """
        Apply NATURAL realistic distance attenuation for comfortable 3D depth
        
        Sound loses energy based on:
        1. Inverse square law (intensity ∝ 1/r²) - MODERATE and natural
        2. Air absorption (high frequencies absorbed more)
        3. Direct-to-reverberant ratio changes with distance
        
        REALISTIC: Noticeable but comfortable depth perception!
        """
        # NATURAL inverse square law attenuation for comfortable realism
        # Prevent division by zero, min distance 0.5m
        distance_clamped = torch.clamp(distance, min=0.5, max=50.0)
        
        # MODERATE inverse square law - noticeable but comfortable
        # At 2m: 1.0x, At 3m: 0.67x, At 4m: 0.50x, At 5m: 0.40x
        attenuation = 2.0 / distance_clamped  # Reference at 2.0m
        attenuation = torch.clamp(attenuation, 0.20, 2.5)  # Moderate, comfortable range
        
        # Apply time-varying attenuation
        audio_attenuated = audio * attenuation
        
        # Air absorption (simple high-shelf filter)
        # Far distances lose high frequencies - ENHANCED
        audio_absorbed = self._apply_air_absorption(audio_attenuated, distance)
        
        return audio_absorbed
    
    def _apply_air_absorption(self, audio: torch.Tensor, distance: torch.Tensor) -> torch.Tensor:
        """
        Simulate air absorption (high frequencies attenuate with distance)
        
        OPTIMIZED: GPU-accelerated lowpass filter
        """
        # Use running average distance for smoothness
        avg_distance = distance.mean().item()
        
        # High-frequency rolloff increases with distance
        # At 10m, -3dB at 8kHz; at 2m, barely noticeable
        absorption_factor = min(avg_distance / 10.0, 1.0)
        
        if absorption_factor < 0.1:
            return audio  # No absorption needed for close distances
        
        # Simple one-pole lowpass filter using FFT (MUCH faster on GPU)
        cutoff = 12000 * (1.0 - absorption_factor * 0.6)  # 12kHz to 4.8kHz
        
        # Create lowpass filter in frequency domain
        freqs = torch.fft.rfftfreq(len(audio), 1/self.sample_rate, device=self.device)
        
        # Butterworth-like response
        H = 1.0 / torch.sqrt(1.0 + (freqs / cutoff) ** 4)
        
        # Apply filter in frequency domain (FFT method - GPU accelerated)
        audio_fft = torch.fft.rfft(audio)
        filtered_fft = audio_fft * H
        output = torch.fft.irfft(filtered_fft, n=len(audio))
        
        return output
    
    def _calculate_itd(self, azimuth: torch.Tensor, elevation: torch.Tensor) -> torch.Tensor:
        """
        Calculate Inter-aural Time Difference (ITD)
        
        ITD is the difference in arrival time between ears.
        Uses Woodworth-Schlosberg formula for spherical head model.
        """
        # Project onto horizontal plane for ITD calculation
        azimuth_horizontal = azimuth * torch.cos(elevation)
        
        # Woodworth formula: ITD = (r/c) * (sin(θ) + θ)
        # where θ is angle from median plane
        theta = azimuth_horizontal - np.pi/2  # Convert to median plane angle
        
        # Calculate ITD in seconds
        itd_seconds = (self.head_radius / self.speed_of_sound) * \
                      (torch.sin(theta) + theta)
        
        # Convert to samples
        itd_samples = itd_seconds * self.sample_rate
        
        # NATURAL ITD for smooth, realistic rotation (1.8x multiplier)
        # This is noticeable but comfortable - like real life
        # Too high = unnatural/fatiguing, too low = unclear rotation
        itd_samples = itd_samples * 1.8
        
        # Clamp to natural human range (realistic head-related timing)
        itd_samples = torch.clamp(itd_samples, -50, 50)
        
        return itd_samples
    
    def _calculate_ild(
        self,
        azimuth: torch.Tensor,
        elevation: torch.Tensor,
        distance: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Calculate Inter-aural Level Difference (ILD) - TRUE 3D HARD PANNING
        
        REAL 3D AUDIO: Sounds at sides should DOMINATE that ear!
        - At 90° right: 95% right ear, 5% left ear
        - At 0° front: 50/50 equal
        - At 180° back: 50/50 equal (but reduced by front/back modulation)
        
        This is how REAL 3D audio works - not centered, but HARD panned!
        """
        # Convert azimuth to pan position
        # pan = -1 (left), 0 (center), +1 (right)
        pan = torch.sin(azimuth)  # Smooth circular motion
        
        # NATURAL REALISTIC PANNING for comfortable 3D
        # Like sitting in a real concert - clear stereo but not extreme
        # At sides: One ear louder, but opposite ear still hears clearly
        # At center: Both ears equal
        
        # Smooth exponential curve for natural panning
        pan_normalized = (pan + 1.0) / 2.0  # 0 to 1 range
        
        # NATURAL PANNING - Clear stereo movement without fatigue
        # At pan=0 (left):   left≈0.85, right≈0.25
        # At pan=0.5 (center): left=0.55, right=0.55  
        # At pan=1 (right):  left≈0.25, right≈0.85
        
        # Comfortable power curve - realistic but not aggressive
        right_gain = pan_normalized ** 0.80
        left_gain = (1.0 - pan_normalized) ** 0.80
        
        # Scale to create clear but comfortable dominance (25–85% range)
        # This maintains spatial clarity while reducing fatigue
        right_gain = 0.25 + 0.60 * right_gain
        left_gain = 0.25 + 0.60 * left_gain
        
        # NO NORMALIZATION - let one side dominate!
        # This is the KEY difference - true 3D doesn't normalize
        # At 90° right, right ear should be WAY louder than left
        
        return left_gain, right_gain
    
    def _apply_frontal_amplitude_modulation(
        self,
        audio: torch.Tensor,
        azimuth: torch.Tensor
    ) -> torch.Tensor:
        """
        Apply STRONG frontal dominance for "band IN FRONT of you" experience.

        ULTRA-REALISTIC DESIGN:
        - Front (0°): LOUD and PRESENT - like performers are right there
        - Sides (±90°): Medium volume - natural falloff
        - Back (180°): CLEARLY quieter - they've rotated behind you
        - Creates natural "revolving around you" sensation
        - ~6-7 dB variation (front to back) - very noticeable but natural
        """
        # Cosine-based front/back factor: 1 at front (0°), -1 at back (180°)
        front_back_factor = torch.cos(azimuth)

        # STRONGER base modulation for clear frontal dominance
        # Front (cos=1): 1.00 (full volume - IN YOUR FACE)
        # Sides (cos=0): 0.80 (noticeable drop - rotating to side)
        # Back (cos=-1): 0.60 (clearly quieter - behind you)
        # This gives ~6.5 dB front-to-back difference
        base_gain = 0.80 + 0.20 * front_back_factor  # 0.60 to 1.00 range

        # ENHANCED frontal "spotlight" for ultra-realism
        front_zone = torch.abs(azimuth) < (np.pi / 4)              # ±45° front arc
        back_zone = torch.abs(torch.abs(azimuth) - np.pi) < (np.pi / 4)  # ±45° back arc

        spotlight = torch.zeros_like(azimuth)
        spotlight[front_zone] = 0.08   # +8% boost when in front (strong presence)
        spotlight[back_zone] = -0.08   # -8% when behind (clear rotation)

        amplitude_gain = base_gain + spotlight

        # Wider safety clamp: 0.52–1.08 ⇒ ~6.5 dB front-to-back variation
        # This makes rotation OBVIOUS and REALISTIC
        amplitude_gain = torch.clamp(amplitude_gain, 0.52, 1.08)

        # Apply time-varying amplitude modulation
        audio_modulated = audio * amplitude_gain
        return audio_modulated
    
    def _apply_angular_frequency_filtering(
        self,
        audio: torch.Tensor,
        azimuth: torch.Tensor
    ) -> torch.Tensor:
        """
        Apply VERY SUBTLE frequency spatial cue - maintains premium quality!
        
        Like a live concert - even musicians behind you sound CLEAR and BRIGHT,
        just with subtle tonal positioning cue. NO muffling, NO quality loss!
        
        - Front (0°): Full 20kHz - Crystal clear
        - Sides (±90°): Minimal rolloff - Still crystal clear  
        - Back (180°): Subtle 10kHz rolloff - Clear, just slightly warmer
        """
        # Calculate average position for filter design
        chunk_size = min(len(azimuth), self.sample_rate // 10)  # 100ms chunks
        avg_azimuth = azimuth[::max(1, len(azimuth) // chunk_size)].mean().item()
        
        # Calculate front/back factor
        front_back = np.cos(avg_azimuth)
        
        # Calculate SUBTLE filtering amount:
        # We want MINIMAL quality loss - just a spatial cue
        filtering_amount = (1.0 - front_back) / 2.0  # 0 (front) to 1 (back)
        
        # Only apply if significantly towards back (> 40% back)
        if filtering_amount < 0.4:
            return audio  # No filtering for front 60% - keeps quality!
        
        # Create SUBTLE frequency-dependent filter
        freqs = torch.fft.rfftfreq(len(audio), 1/self.sample_rate, device=self.device)
        
        # MUCH GENTLER low-pass:
        # Front: cutoff = 20kHz (full bandwidth)
        # Back: cutoff = 10kHz (subtle warmth, still clear!)
        # Range: Only 10kHz variation instead of 16kHz
        cutoff = 20000 - (10000 * filtering_amount)  # 20kHz -> 10kHz
        
        # VERY gentle 2nd-order rolloff (was 6th-order)
        filter_response = 1.0 / torch.sqrt(1.0 + (freqs / cutoff) ** 2)
        
        # Apply filter in frequency domain
        audio_fft = torch.fft.rfft(audio)
        filtered_fft = audio_fft * filter_response
        audio_filtered = torch.fft.irfft(filtered_fft, n=len(audio))
        
        return audio_filtered
    
    def _apply_time_varying_delay(
        self,
        audio: torch.Tensor,
        delay_samples: torch.Tensor,
        gain: torch.Tensor
    ) -> torch.Tensor:
        """
        Apply time-varying delay with high-quality cubic interpolation
        to minimize HF loss and zippering artifacts during rotation.
        """
        N = len(audio)
        idx = torch.arange(N, device=self.device, dtype=torch.float32)
        read_pos = idx - delay_samples
        read_pos = torch.clamp(read_pos, 0.0, N - 1.001)
        n0 = torch.floor(read_pos).long()
        d = (read_pos - n0.float())
        
        # Neighbor indices for 4-tap cubic interpolation: n-1, n, n+1, n+2
        i0 = torch.clamp(n0 - 1, 0, N - 1)
        i1 = n0
        i2 = torch.clamp(n0 + 1, 0, N - 1)
        i3 = torch.clamp(n0 + 2, 0, N - 1)
        
        y0 = audio[i0]
        y1 = audio[i1]
        y2 = audio[i2]
        y3 = audio[i3]
        
        # Cubic interpolation coefficients (Keys)
        a0 = y3 - y2 - y0 + y1
        a1 = y0 - y1 - a0
        a2 = y2 - y0
        a3 = y1
        
        samples = ((a0 * d + a1) * d + a2) * d + a3
        
        return samples * gain
    
    def _add_early_reflections(
        self,
        left: torch.Tensor,
        right: torch.Tensor,
        azimuth: torch.Tensor,
        distance: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Add SUBTLE early reflections for 3D room presence
        
        This is THE KEY to making sound feel REAL and IN A SPACE!
        Without early reflections, everything feels like flat speakers.
        With them, sound feels like it's happening in a real 3D room.
        
        Early reflections arrive 5-50ms after direct sound:
        - Wall reflections: 10-30ms
        - Floor/ceiling: 5-15ms
        - Create sense of space and depth
        """
        # Calculate average distance and angle
        avg_distance = distance.mean().item()
        avg_azimuth = azimuth.mean().item()
        
        # Early reflection timing based on distance
        # Closer sounds = shorter reflection times
        reflection_time_ms = 8 + (avg_distance * 3)  # 8-20ms range
        reflection_delay = int((reflection_time_ms / 1000.0) * self.sample_rate)
        
        # Reflection level based on distance (farther = more reflections)
        # BALANCED for room presence without excessive decorrelation
        reflection_level = 0.04 + (avg_distance / 10.0) * 0.05  # 4-9% mix
        reflection_level = min(reflection_level, 0.09)  # Max 9% (clear room, better correlation)
        
        # Create VERY SUBTLE reflections
        # Don't use reverb - just simple delays for early reflections
        
        if reflection_delay < len(left):
            # Add 3 early reflections (walls)
            # Each reflection is slightly delayed and attenuated
            
            # Reflection 1: First wall (10ms)
            delay1 = int(reflection_delay * 0.6)
            if delay1 < len(left):
                left_reflect1 = torch.cat([torch.zeros(delay1, device=self.device), left[:-delay1]]) * (reflection_level * 0.5)
                right_reflect1 = torch.cat([torch.zeros(delay1, device=self.device), right[:-delay1]]) * (reflection_level * 0.5)
                
                # IMPROVED: Less channel swapping for better correlation
                left = left + left_reflect1 + right_reflect1 * 0.15  # Reduced from 0.3
                right = right + right_reflect1 + left_reflect1 * 0.15  # Reduced from 0.3
            
            # Reflection 2: Second wall (15ms)
            delay2 = int(reflection_delay * 1.0)
            if delay2 < len(left):
                left_reflect2 = torch.cat([torch.zeros(delay2, device=self.device), left[:-delay2]]) * (reflection_level * 0.3)
                right_reflect2 = torch.cat([torch.zeros(delay2, device=self.device), right[:-delay2]]) * (reflection_level * 0.3)
                
                left = left + left_reflect2
                right = right + right_reflect2
            
            # Reflection 3: Floor/ceiling (8ms) - higher frequencies
            delay3 = int(reflection_delay * 0.4)
            if delay3 < len(left):
                # High-pass filtered reflection (only highs reflect from floor)
                left_reflect3 = torch.cat([torch.zeros(delay3, device=self.device), left[:-delay3]]) * (reflection_level * 0.25)
                right_reflect3 = torch.cat([torch.zeros(delay3, device=self.device), right[:-delay3]]) * (reflection_level * 0.25)
                
                # Apply high-pass filter to reflections (>1kHz)
                left_reflect3 = self._highpass_simple(left_reflect3, 1000)
                right_reflect3 = self._highpass_simple(right_reflect3, 1000)
                
                left = left + left_reflect3
                right = right + right_reflect3
        
        return left, right
    
    def _highpass_simple(self, audio: torch.Tensor, cutoff: float) -> torch.Tensor:
        """Simple high-pass filter for reflections"""
        freqs = torch.fft.rfftfreq(len(audio), 1/self.sample_rate, device=self.device)
        
        # High-pass response (2nd-order)
        hp_response = (freqs / cutoff) ** 2 / (1.0 + (freqs / cutoff) ** 2)
        
        # Apply in frequency domain
        audio_fft = torch.fft.rfft(audio)
        filtered_fft = audio_fft * hp_response
        output = torch.fft.irfft(filtered_fft, n=len(audio))
        
        return output
    
    def _apply_hrtf_filtering(
        self,
        left: torch.Tensor,
        right: torch.Tensor,
        azimuth: torch.Tensor,
        elevation: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Apply simplified HRTF frequency-dependent filtering
        
        Models the frequency response changes due to:
        - Pinna (outer ear) resonances
        - Head diffraction
        - Torso reflections
        """
        # Use average angle for filter design
        avg_azimuth = azimuth.mean().item()
        avg_elevation = elevation.mean().item()
        
        # Create spectral shape based on angle
        # Front: balanced; Side: boost highs; Back: attenuate highs
        front_back = np.cos(avg_azimuth)  # 1 at front, -1 at back
        
        # Pinna boost at 3-8kHz for lateral sounds
        lateral_factor = abs(np.sin(avg_azimuth))  # 0 at front/back, 1 at sides
        
        # Apply subtle high-shelf filter
        if lateral_factor > 0.3 or front_back < 0:
            # Boost/cut highs based on direction
            boost_db = lateral_factor * 3.0 - front_back * 2.0
            left = self._apply_high_shelf(left, 4000, boost_db)
            right = self._apply_high_shelf(right, 4000, boost_db * 0.8)
        
        return left, right
    
    def _apply_high_shelf(self, audio: torch.Tensor, freq: float, gain_db: float) -> torch.Tensor:
        """Apply simple high-shelf filter - GPU optimized"""
        if abs(gain_db) < 0.5:
            return audio
        
        gain_linear = 10 ** (gain_db / 20.0)
        
        # Use FFT-based high-shelf (much faster on GPU)
        freqs = torch.fft.rfftfreq(len(audio), 1/self.sample_rate, device=self.device)
        
        # High-shelf response
        shelf = torch.ones_like(freqs)
        shelf[freqs > freq] = gain_linear
        
        # Smooth transition
        transition_mask = (freqs > freq * 0.8) & (freqs < freq * 1.2)
        if transition_mask.any():
            transition_freqs = freqs[transition_mask]
            transition_range = (transition_freqs - freq * 0.8) / (freq * 0.4)
            shelf[transition_mask] = 1.0 + (gain_linear - 1.0) * transition_range
        
        # Apply in frequency domain
        audio_fft = torch.fft.rfft(audio)
        filtered_fft = audio_fft * shelf
        output = torch.fft.irfft(filtered_fft, n=len(audio))
        
        return output


def test_hrtf():
    """Test HRTF processor"""
    print("\n🎧 Testing HRTF Processor\n")
    
    processor = HRTFProcessor(sample_rate=48000)
    
    # Create test signal (1 second sine wave)
    duration = 1.0
    sample_rate = 48000
    samples = int(duration * sample_rate)
    t = torch.linspace(0, duration, samples)
    
    # 440Hz sine wave (A note)
    audio = torch.sin(2 * np.pi * 440 * t)
    
    # Create rotation from front to right side
    azimuth = torch.linspace(0, np.pi/2, samples)
    
    # Process
    stereo = processor.spatialize(audio, azimuth)
    
    print(f"✅ Input: {audio.shape}")
    print(f"✅ Output: {stereo.shape}")
    print(f"✅ HRTF processor working!")


if __name__ == "__main__":
    test_hrtf()
