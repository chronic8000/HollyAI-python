"""
Eye Tracker - Advanced eye movement and gaze system for Holly
Realistic eye movements, gaze tracking, and expression integration
"""

import math
import time
import random
import numpy as np
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class GazeTarget(Enum):
    """Different gaze targets for Holly"""
    CENTER = "center"
    USER = "user"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    UPPER_LEFT = "upper_left"
    UPPER_RIGHT = "upper_right"
    LOWER_LEFT = "lower_left"
    LOWER_RIGHT = "lower_right"
    RANDOM = "random"

class BlinkType(Enum):
    """Types of blinks"""
    NORMAL = "normal"
    SLOW = "slow"
    QUICK = "quick"
    WINK_LEFT = "wink_left"
    WINK_RIGHT = "wink_right"
    SENILE = "senile"  # Holly's confused blinks

@dataclass
class EyeState:
    """Current state of eyes"""
    left_eye_x: float = 0.0    # -1.0 to 1.0 (left to right)
    left_eye_y: float = 0.0    # -1.0 to 1.0 (up to down)
    right_eye_x: float = 0.0   # -1.0 to 1.0 (left to right)
    right_eye_y: float = 0.0   # -1.0 to 1.0 (up to down)
    left_blink: float = 1.0    # 0.0 closed, 1.0 open
    right_blink: float = 1.0   # 0.0 closed, 1.0 open
    pupil_dilation: float = 0.5  # 0.0 to 1.0 (constricted to dilated)

@dataclass
class SaccadeMovement:
    """A rapid eye movement (saccade)"""
    start_time: float
    duration: float
    start_pos: Tuple[float, float]
    end_pos: Tuple[float, float]
    easing: str = "ease_out"

@dataclass
class BlinkAction:
    """A blink action"""
    start_time: float
    duration: float
    blink_type: BlinkType
    intensity: float = 1.0

class EyeTracker:
    """Advanced eye movement system for Holly"""
    
    def __init__(self):
        """Initialize eye tracker"""
        self.current_time = 0.0
        self.eye_state = EyeState()
        
        # Movement parameters
        self.gaze_targets = self._define_gaze_targets()
        self.current_target = GazeTarget.CENTER
        self.target_position = (0.0, 0.0)
        
        # Saccade (rapid eye movement) system
        self.active_saccades = []
        self.saccade_speed = 0.1  # seconds for typical saccade
        
        # Blink system
        self.active_blinks = []
        self.last_blink_time = 0.0
        self.blink_frequency = 3.0  # average seconds between blinks
        self.blink_variation = 2.0  # random variation
        
        # Smooth pursuit (tracking moving objects)
        self.pursuit_target = None
        self.pursuit_smoothness = 0.05
        
        # Holly-specific parameters
        self.senility_factor = 0.7
        self.confusion_level = 0.0
        self.thinking_mode = False
        
        # Micro-movements for realism
        self.microsaccade_frequency = 0.5  # per second
        self.drift_amplitude = 0.02
        
        logger.info("Eye tracker initialized")
    
    def _define_gaze_targets(self) -> Dict[GazeTarget, Tuple[float, float]]:
        """Define standard gaze target positions"""
        return {
            GazeTarget.CENTER: (0.0, 0.0),
            GazeTarget.USER: (0.0, -0.1),  # Slightly down (camera position)
            GazeTarget.LEFT: (-0.6, 0.0),
            GazeTarget.RIGHT: (0.6, 0.0),
            GazeTarget.UP: (0.0, -0.5),
            GazeTarget.DOWN: (0.0, 0.5),
            GazeTarget.UPPER_LEFT: (-0.4, -0.4),
            GazeTarget.UPPER_RIGHT: (0.4, -0.4),
            GazeTarget.LOWER_LEFT: (-0.4, 0.4),
            GazeTarget.LOWER_RIGHT: (0.4, 0.4),
        }
    
    def update(self, delta_time: float) -> EyeState:
        """Update eye state and return current values"""
        self.current_time += delta_time
        
        # Update saccades
        self._update_saccades()
        
        # Update blinks
        self._update_blinks()
        
        # Update smooth pursuit
        self._update_pursuit()
        
        # Apply micro-movements
        self._apply_micro_movements()
        
        # Apply Holly's senile effects
        self._apply_senile_effects()
        
        # Trigger automatic blinks
        self._check_automatic_blinks()
        
        # Apply thinking mode effects
        if self.thinking_mode:
            self._apply_thinking_effects()
        
        return self.eye_state
    
    def look_at(self, target: GazeTarget, duration: float = 0.2, immediate: bool = False):
        """Look at a specific target"""
        if target == GazeTarget.RANDOM:
            # Choose random position
            target_pos = (
                random.uniform(-0.6, 0.6),
                random.uniform(-0.4, 0.4)
            )
        else:
            target_pos = self.gaze_targets.get(target, (0.0, 0.0))
        
        self.current_target = target
        self.target_position = target_pos
        
        if immediate:
            # Set immediately without saccade
            self.eye_state.left_eye_x = target_pos[0]
            self.eye_state.left_eye_y = target_pos[1]
            self.eye_state.right_eye_x = target_pos[0]
            self.eye_state.right_eye_y = target_pos[1]
        else:
            # Create saccade movement
            current_pos = (self.eye_state.left_eye_x, self.eye_state.left_eye_y)
            
            saccade = SaccadeMovement(
                start_time=self.current_time,
                duration=duration,
                start_pos=current_pos,
                end_pos=target_pos,
                easing="ease_out"
            )
            
            self.active_saccades.append(saccade)
        
        logger.debug(f"Looking at {target} at position {target_pos}")
    
    def look_at_position(self, x: float, y: float, duration: float = 0.2):
        """Look at specific coordinates"""
        # Clamp to valid range
        x = max(-1.0, min(1.0, x))
        y = max(-1.0, min(1.0, y))
        
        target_pos = (x, y)
        current_pos = (self.eye_state.left_eye_x, self.eye_state.left_eye_y)
        
        saccade = SaccadeMovement(
            start_time=self.current_time,
            duration=duration,
            start_pos=current_pos,
            end_pos=target_pos
        )
        
        self.active_saccades.append(saccade)
        
        logger.debug(f"Looking at position ({x:.2f}, {y:.2f})")
    
    def blink(self, blink_type: BlinkType = BlinkType.NORMAL, intensity: float = 1.0):
        """Trigger a blink"""
        duration_map = {
            BlinkType.NORMAL: 0.15,
            BlinkType.SLOW: 0.3,
            BlinkType.QUICK: 0.08,
            BlinkType.WINK_LEFT: 0.2,
            BlinkType.WINK_RIGHT: 0.2,
            BlinkType.SENILE: 0.4  # Longer, confused blinks
        }
        
        duration = duration_map.get(blink_type, 0.15)
        
        blink_action = BlinkAction(
            start_time=self.current_time,
            duration=duration,
            blink_type=blink_type,
            intensity=intensity
        )
        
        self.active_blinks.append(blink_action)
        self.last_blink_time = self.current_time
        
        logger.debug(f"Triggered {blink_type} blink")
    
    def start_thinking_mode(self):
        """Enter thinking mode (different eye behavior)"""
        self.thinking_mode = True
        # Look slightly up and to the side when thinking
        self.look_at(GazeTarget.UPPER_RIGHT)
        logger.debug("Entered thinking mode")
    
    def stop_thinking_mode(self):
        """Exit thinking mode"""
        self.thinking_mode = False
        # Return to center/user
        self.look_at(GazeTarget.USER)
        logger.debug("Exited thinking mode")
    
    def set_confusion_level(self, level: float):
        """Set confusion level (affects eye movements)"""
        self.confusion_level = max(0.0, min(1.0, level))
        
        if level > 0.5:
            # High confusion - more erratic movements
            self.blink(BlinkType.SENILE)
            if random.random() < 0.3:
                self.look_at(GazeTarget.RANDOM)
    
    def set_pupil_dilation(self, dilation: float):
        """Set pupil dilation (0.0 to 1.0)"""
        self.eye_state.pupil_dilation = max(0.0, min(1.0, dilation))
    
    def _update_saccades(self):
        """Update active saccade movements"""
        completed_saccades = []
        
        for saccade in self.active_saccades:
            elapsed = self.current_time - saccade.start_time
            
            if elapsed >= saccade.duration:
                # Saccade completed
                self.eye_state.left_eye_x = saccade.end_pos[0]
                self.eye_state.left_eye_y = saccade.end_pos[1]
                self.eye_state.right_eye_x = saccade.end_pos[0]
                self.eye_state.right_eye_y = saccade.end_pos[1]
                completed_saccades.append(saccade)
            else:
                # Interpolate position
                progress = elapsed / saccade.duration
                eased_progress = self._apply_easing(progress, saccade.easing)
                
                start_x, start_y = saccade.start_pos
                end_x, end_y = saccade.end_pos
                
                current_x = start_x + (end_x - start_x) * eased_progress
                current_y = start_y + (end_y - start_y) * eased_progress
                
                self.eye_state.left_eye_x = current_x
                self.eye_state.left_eye_y = current_y
                self.eye_state.right_eye_x = current_x
                self.eye_state.right_eye_y = current_y
        
        # Remove completed saccades
        for saccade in completed_saccades:
            self.active_saccades.remove(saccade)
    
    def _update_blinks(self):
        """Update active blinks"""
        completed_blinks = []
        
        for blink in self.active_blinks:
            elapsed = self.current_time - blink.start_time
            
            if elapsed >= blink.duration:
                # Blink completed - eyes open
                if blink.blink_type in [BlinkType.WINK_LEFT]:
                    self.eye_state.left_blink = 1.0
                elif blink.blink_type in [BlinkType.WINK_RIGHT]:
                    self.eye_state.right_blink = 1.0
                else:
                    self.eye_state.left_blink = 1.0
                    self.eye_state.right_blink = 1.0
                
                completed_blinks.append(blink)
            else:
                # Calculate blink progress
                progress = elapsed / blink.duration
                
                # Blink curve (quick close, slower open)
                if progress < 0.3:
                    # Closing phase
                    blink_value = 1.0 - (progress / 0.3) * blink.intensity
                else:
                    # Opening phase
                    blink_value = ((progress - 0.3) / 0.7) * blink.intensity
                
                blink_value = max(0.0, min(1.0, blink_value))
                
                # Apply to appropriate eyes
                if blink.blink_type == BlinkType.WINK_LEFT:
                    self.eye_state.left_blink = blink_value
                elif blink.blink_type == BlinkType.WINK_RIGHT:
                    self.eye_state.right_blink = blink_value
                else:
                    self.eye_state.left_blink = blink_value
                    self.eye_state.right_blink = blink_value
        
        # Remove completed blinks
        for blink in completed_blinks:
            self.active_blinks.remove(blink)
    
    def _update_pursuit(self):
        """Update smooth pursuit movements"""
        if self.pursuit_target:
            # Smooth tracking towards target
            target_x, target_y = self.pursuit_target
            
            # Smooth interpolation
            current_x = self.eye_state.left_eye_x
            current_y = self.eye_state.left_eye_y
            
            new_x = current_x + (target_x - current_x) * self.pursuit_smoothness
            new_y = current_y + (target_y - current_y) * self.pursuit_smoothness
            
            self.eye_state.left_eye_x = new_x
            self.eye_state.left_eye_y = new_y
            self.eye_state.right_eye_x = new_x
            self.eye_state.right_eye_y = new_y
    
    def _apply_micro_movements(self):
        """Apply realistic micro-movements"""
        # Microsaccades (tiny random movements)
        if random.random() < self.microsaccade_frequency * 0.016:  # 60 FPS assumption
            drift_x = random.uniform(-self.drift_amplitude, self.drift_amplitude)
            drift_y = random.uniform(-self.drift_amplitude, self.drift_amplitude)
            
            self.eye_state.left_eye_x += drift_x
            self.eye_state.left_eye_y += drift_y
            self.eye_state.right_eye_x += drift_x
            self.eye_state.right_eye_y += drift_y
            
            # Clamp to valid range
            self.eye_state.left_eye_x = max(-1.0, min(1.0, self.eye_state.left_eye_x))
            self.eye_state.left_eye_y = max(-1.0, min(1.0, self.eye_state.left_eye_y))
            self.eye_state.right_eye_x = max(-1.0, min(1.0, self.eye_state.right_eye_x))
            self.eye_state.right_eye_y = max(-1.0, min(1.0, self.eye_state.right_eye_y))
    
    def _apply_senile_effects(self):
        """Apply Holly's senile eye movement effects"""
        if random.random() < self.senility_factor * 0.001:  # Very occasional
            # Random senile moment
            senile_actions = [
                lambda: self.blink(BlinkType.SENILE),
                lambda: self.look_at(GazeTarget.RANDOM, duration=0.5),
                lambda: self.set_confusion_level(0.8),
                lambda: self._trigger_eye_dart()
            ]
            
            random.choice(senile_actions)()
    
    def _apply_thinking_effects(self):
        """Apply effects when Holly is thinking"""
        # Occasional upward glances when thinking
        if random.random() < 0.002:  # Rare
            thinking_targets = [GazeTarget.UP, GazeTarget.UPPER_LEFT, GazeTarget.UPPER_RIGHT]
            self.look_at(random.choice(thinking_targets), duration=0.3)
        
        # Slower blinking when concentrating
        if random.random() < 0.001:
            self.blink(BlinkType.SLOW)
    
    def _trigger_eye_dart(self):
        """Trigger a quick eye dart (Holly looking around)"""
        # Quick glance to side and back
        side_target = random.choice([GazeTarget.LEFT, GazeTarget.RIGHT])
        self.look_at(side_target, duration=0.1)
        
        # Return to previous target after brief delay
        def return_to_center():
            self.look_at(GazeTarget.CENTER, duration=0.1)
        
        # Would need to implement delayed callback in main system
        logger.debug("Triggered eye dart")
    
    def _check_automatic_blinks(self):
        """Check if it's time for an automatic blink"""
        time_since_blink = self.current_time - self.last_blink_time
        
        # Calculate next blink time with variation
        next_blink_time = self.blink_frequency + random.uniform(-self.blink_variation, self.blink_variation)
        
        if time_since_blink >= next_blink_time:
            # Time for automatic blink
            blink_types = [BlinkType.NORMAL] * 5 + [BlinkType.SLOW] * 1  # Weighted selection
            if self.senility_factor > 0.5:
                blink_types.append(BlinkType.SENILE)
            
            self.blink(random.choice(blink_types))
    
    def _apply_easing(self, progress: float, easing_type: str) -> float:
        """Apply easing function for smooth movements"""
        if easing_type == "linear":
            return progress
        elif easing_type == "ease_out":
            return 1 - (1 - progress) ** 2
        elif easing_type == "ease_in":
            return progress ** 2
        elif easing_type == "ease_in_out":
            if progress < 0.5:
                return 2 * progress ** 2
            else:
                return 1 - 2 * (1 - progress) ** 2
        else:
            return progress
    
    def get_debug_info(self) -> Dict:
        """Get debug information"""
        return {
            'current_target': self.current_target.value if self.current_target else None,
            'target_position': self.target_position,
            'active_saccades': len(self.active_saccades),
            'active_blinks': len(self.active_blinks),
            'thinking_mode': self.thinking_mode,
            'confusion_level': self.confusion_level,
            'senility_factor': self.senility_factor,
            'eye_position': (self.eye_state.left_eye_x, self.eye_state.left_eye_y),
            'blink_state': (self.eye_state.left_blink, self.eye_state.right_blink)
        }
