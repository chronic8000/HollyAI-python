"""
Lip Sync - Advanced lip synchronization system for Holly's speech
Real-time phoneme detection and mouth animation
"""

import re
import math
import time
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class Phoneme(Enum):
    """Phonetic sounds for lip sync"""
    # Vowels
    A = "a"  # Open mouth (like "cat")
    E = "e"  # Semi-open (like "bet") 
    I = "i"  # Small opening (like "bit")
    O = "o"  # Round mouth (like "pot")
    U = "u"  # Small round (like "put")
    
    # Consonants
    B_P_M = "bpm"      # Closed lips (like "bat", "pat", "mat")
    F_V = "fv"         # Lower lip to teeth (like "fat", "vat")
    TH = "th"          # Tongue between teeth (like "that")
    T_D_N_L = "tdnl"   # Tongue to roof (like "top", "dog", "not", "lot")
    K_G = "kg"         # Back of tongue (like "cat", "go")
    S_Z = "sz"         # Teeth together (like "sit", "zip")
    SH_ZH = "shzh"     # Pursed lips (like "ship", "measure")
    R = "r"            # Slight pucker (like "red")
    W = "w"            # Round lips (like "wet")
    Y = "y"            # Slight smile (like "yes")
    
    # Special
    SILENCE = "silence"
    PAUSE = "pause"

@dataclass
class LipSyncFrame:
    """A single frame of lip sync data"""
    timestamp: float
    phoneme: Phoneme
    intensity: float = 1.0
    duration: float = 0.1

@dataclass
class MouthShape:
    """Mouth shape parameters for a phoneme"""
    width: float      # -1.0 to 1.0 (narrow to wide)
    height: float     # 0.0 to 1.0 (closed to open)
    pucker: float     # 0.0 to 1.0 (spread to pursed)
    tongue: float     # 0.0 to 1.0 (down to up)

class LipSyncEngine:
    """Advanced lip synchronization engine for Holly"""
    
    def __init__(self):
        """Initialize lip sync engine"""
        self.mouth_shapes = self._define_mouth_shapes()
        self.phoneme_rules = self._define_phoneme_rules()
        
        # Current state
        self.current_frame = None
        self.is_speaking = False
        self.speech_intensity = 1.0
        
        # Timing
        self.frame_rate = 30.0  # 30 FPS for smooth animation
        self.frame_duration = 1.0 / self.frame_rate
        
        # Smoothing
        self.smoothing_factor = 0.7
        self.previous_shape = MouthShape(0.0, 0.0, 0.0, 0.0)
        
        logger.info("Lip sync engine initialized")
    
    def _define_mouth_shapes(self) -> Dict[Phoneme, MouthShape]:
        """Define mouth shapes for each phoneme"""
        return {
            # Vowels - generally more open
            Phoneme.A: MouthShape(width=0.8, height=0.9, pucker=0.0, tongue=0.0),
            Phoneme.E: MouthShape(width=0.6, height=0.6, pucker=0.0, tongue=0.2),
            Phoneme.I: MouthShape(width=0.2, height=0.3, pucker=0.0, tongue=0.4),
            Phoneme.O: MouthShape(width=0.4, height=0.8, pucker=0.7, tongue=0.0),
            Phoneme.U: MouthShape(width=0.2, height=0.4, pucker=0.8, tongue=0.0),
            
            # Consonants - various lip positions
            Phoneme.B_P_M: MouthShape(width=0.0, height=0.0, pucker=0.0, tongue=0.0),
            Phoneme.F_V: MouthShape(width=0.3, height=0.2, pucker=0.0, tongue=0.0),
            Phoneme.TH: MouthShape(width=0.4, height=0.3, pucker=0.0, tongue=0.8),
            Phoneme.T_D_N_L: MouthShape(width=0.3, height=0.2, pucker=0.0, tongue=0.6),
            Phoneme.K_G: MouthShape(width=0.2, height=0.3, pucker=0.0, tongue=0.3),
            Phoneme.S_Z: MouthShape(width=0.1, height=0.1, pucker=0.0, tongue=0.5),
            Phoneme.SH_ZH: MouthShape(width=0.2, height=0.3, pucker=0.5, tongue=0.3),
            Phoneme.R: MouthShape(width=0.3, height=0.4, pucker=0.3, tongue=0.4),
            Phoneme.W: MouthShape(width=0.2, height=0.4, pucker=0.7, tongue=0.0),
            Phoneme.Y: MouthShape(width=0.6, height=0.2, pucker=0.0, tongue=0.3),
            
            # Special cases
            Phoneme.SILENCE: MouthShape(width=0.0, height=0.0, pucker=0.0, tongue=0.0),
            Phoneme.PAUSE: MouthShape(width=0.1, height=0.0, pucker=0.0, tongue=0.0),
        }
    
    def _define_phoneme_rules(self) -> Dict[str, Phoneme]:
        """Define rules for mapping text to phonemes"""
        return {
            # Vowels
            'a': Phoneme.A, 'ah': Phoneme.A, 'aa': Phoneme.A,
            'e': Phoneme.E, 'eh': Phoneme.E, 'ea': Phoneme.E,
            'i': Phoneme.I, 'ih': Phoneme.I, 'ee': Phoneme.I,
            'o': Phoneme.O, 'oh': Phoneme.O, 'oo': Phoneme.O,
            'u': Phoneme.U, 'uh': Phoneme.U, 'ou': Phoneme.U,
            
            # Consonants
            'b': Phoneme.B_P_M, 'p': Phoneme.B_P_M, 'm': Phoneme.B_P_M,
            'f': Phoneme.F_V, 'v': Phoneme.F_V,
            'th': Phoneme.TH,
            't': Phoneme.T_D_N_L, 'd': Phoneme.T_D_N_L, 
            'n': Phoneme.T_D_N_L, 'l': Phoneme.T_D_N_L,
            'k': Phoneme.K_G, 'g': Phoneme.K_G, 'c': Phoneme.K_G,
            's': Phoneme.S_Z, 'z': Phoneme.S_Z,
            'sh': Phoneme.SH_ZH, 'zh': Phoneme.SH_ZH, 'ch': Phoneme.SH_ZH,
            'r': Phoneme.R,
            'w': Phoneme.W,
            'y': Phoneme.Y, 'j': Phoneme.Y,
            
            # Special
            ' ': Phoneme.PAUSE,
            '.': Phoneme.PAUSE, ',': Phoneme.PAUSE, '!': Phoneme.PAUSE,
            '?': Phoneme.PAUSE, ';': Phoneme.PAUSE, ':': Phoneme.PAUSE,
        }
    
    def generate_lip_sync_data(self, text: str, speech_rate: float = 160) -> List[LipSyncFrame]:
        """Generate lip sync data from text"""
        # Convert words per minute to characters per second
        char_per_second = (speech_rate * 5) / 60  # Assume 5 chars per word
        
        # Clean and prepare text
        text = text.lower().strip()
        text = re.sub(r'[^\w\s.,!?;:]', '', text)  # Remove special chars
        
        frames = []
        current_time = 0.0
        
        # Process text character by character with some intelligence
        i = 0
        while i < len(text):
            char = text[i]
            
            # Look ahead for multi-character phonemes
            if i < len(text) - 1:
                two_char = text[i:i+2]
                if two_char in self.phoneme_rules:
                    phoneme = self.phoneme_rules[two_char]
                    duration = 2.0 / char_per_second
                    i += 2
                else:
                    phoneme = self.phoneme_rules.get(char, Phoneme.SILENCE)
                    duration = 1.0 / char_per_second
                    i += 1
            else:
                phoneme = self.phoneme_rules.get(char, Phoneme.SILENCE)
                duration = 1.0 / char_per_second
                i += 1
            
            # Adjust duration based on phoneme type
            if phoneme in [Phoneme.A, Phoneme.E, Phoneme.I, Phoneme.O, Phoneme.U]:
                duration *= 1.2  # Vowels are held longer
            elif phoneme == Phoneme.PAUSE:
                duration *= 0.5  # Pauses are shorter
            
            # Add some randomness for natural feel (Holly's senility)
            duration *= np.random.uniform(0.8, 1.2)
            
            frame = LipSyncFrame(
                timestamp=current_time,
                phoneme=phoneme,
                intensity=self._calculate_intensity(phoneme),
                duration=duration
            )
            
            frames.append(frame)
            current_time += duration
        
        logger.debug(f"Generated {len(frames)} lip sync frames for text: {text[:30]}...")
        return frames
    
    def _calculate_intensity(self, phoneme: Phoneme) -> float:
        """Calculate speaking intensity based on phoneme"""
        vowel_phonemes = [Phoneme.A, Phoneme.E, Phoneme.I, Phoneme.O, Phoneme.U]
        
        if phoneme in vowel_phonemes:
            return np.random.uniform(0.8, 1.0)  # Vowels are more intense
        elif phoneme in [Phoneme.SILENCE, Phoneme.PAUSE]:
            return 0.0
        else:
            return np.random.uniform(0.4, 0.7)  # Consonants are less intense
    
    def get_mouth_shape_at_time(self, frames: List[LipSyncFrame], 
                               timestamp: float) -> MouthShape:
        """Get mouth shape at specific timestamp"""
        if not frames:
            return self.mouth_shapes[Phoneme.SILENCE]
        
        # Find the appropriate frame
        current_frame = None
        for frame in frames:
            if frame.timestamp <= timestamp < frame.timestamp + frame.duration:
                current_frame = frame
                break
        
        if not current_frame:
            # Use the last frame or silence
            if timestamp >= frames[-1].timestamp + frames[-1].duration:
                return self.mouth_shapes[Phoneme.SILENCE]
            else:
                current_frame = frames[0]
        
        # Get base mouth shape
        base_shape = self.mouth_shapes[current_frame.phoneme]
        
        # Apply intensity scaling
        intensity = current_frame.intensity * self.speech_intensity
        
        # Scale the mouth shape
        scaled_shape = MouthShape(
            width=base_shape.width * intensity,
            height=base_shape.height * intensity,
            pucker=base_shape.pucker * intensity,
            tongue=base_shape.tongue * intensity
        )
        
        # Apply smoothing
        smoothed_shape = self._smooth_mouth_shape(scaled_shape)
        
        return smoothed_shape
    
    def _smooth_mouth_shape(self, target_shape: MouthShape) -> MouthShape:
        """Apply smoothing to mouth shape transitions"""
        if not hasattr(self, 'previous_shape'):
            self.previous_shape = target_shape
            return target_shape
        
        # Linear interpolation for smoothing
        smoothed = MouthShape(
            width=self._lerp(self.previous_shape.width, target_shape.width, self.smoothing_factor),
            height=self._lerp(self.previous_shape.height, target_shape.height, self.smoothing_factor),
            pucker=self._lerp(self.previous_shape.pucker, target_shape.pucker, self.smoothing_factor),
            tongue=self._lerp(self.previous_shape.tongue, target_shape.tongue, self.smoothing_factor)
        )
        
        self.previous_shape = smoothed
        return smoothed
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolation between two values"""
        return a + (b - a) * t
    
    def analyze_text_for_emphasis(self, text: str) -> List[Tuple[int, int, float]]:
        """Analyze text for emphasis points (Holly's dramatic moments)"""
        emphasis_patterns = [
            (r'\b(brilliant|smeg|gordon bennett)\b', 1.5),  # Holly's exclamations
            (r'\b(IQ|6000|six thousand)\b', 1.3),          # IQ mentions
            (r'[!]{1,}', 1.4),                             # Exclamation marks
            (r'[?]{1,}', 1.2),                             # Questions
            (r'\b(right|oh|well)\b', 0.8),                 # Holly's speech patterns
        ]
        
        emphasis_regions = []
        
        for pattern, intensity in emphasis_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start, end = match.span()
                emphasis_regions.append((start, end, intensity))
        
        return emphasis_regions
    
    def apply_holly_speech_characteristics(self, frames: List[LipSyncFrame], 
                                         text: str) -> List[LipSyncFrame]:
        """Apply Holly's specific speech characteristics"""
        # Find emphasis regions
        emphasis_regions = self.analyze_text_for_emphasis(text)
        
        # Apply Holly's senile speech patterns
        for i, frame in enumerate(frames):
            # Check if frame is in emphasis region
            char_pos = int(frame.timestamp * 10)  # Rough character position
            
            for start, end, intensity_mult in emphasis_regions:
                if start <= char_pos <= end:
                    frame.intensity *= intensity_mult
                    break
            
            # Add occasional pauses (Holly's senior moments)
            if frame.phoneme != Phoneme.PAUSE and np.random.random() < 0.05:
                # Insert a small pause
                pause_frame = LipSyncFrame(
                    timestamp=frame.timestamp + frame.duration * 0.5,
                    phoneme=Phoneme.PAUSE,
                    intensity=0.0,
                    duration=0.1
                )
                frames.insert(i + 1, pause_frame)
        
        return frames
    
    def start_speaking(self, text: str, speech_rate: float = 160):
        """Start speaking with lip sync"""
        self.is_speaking = True
        frames = self.generate_lip_sync_data(text, speech_rate)
        frames = self.apply_holly_speech_characteristics(frames, text)
        
        logger.info(f"Started lip sync for: {text[:30]}...")
        return frames
    
    def stop_speaking(self):
        """Stop speaking"""
        self.is_speaking = False
        self.current_frame = None
        logger.debug("Stopped lip sync")
    
    def set_speech_intensity(self, intensity: float):
        """Set overall speech intensity"""
        self.speech_intensity = max(0.0, min(1.0, intensity))
    
    def get_debug_info(self) -> Dict:
        """Get debug information"""
        return {
            'is_speaking': self.is_speaking,
            'speech_intensity': self.speech_intensity,
            'frame_rate': self.frame_rate,
            'smoothing_factor': self.smoothing_factor,
            'current_frame': str(self.current_frame) if self.current_frame else None
        }
