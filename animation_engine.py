"""
Animation Engine - Enhanced Holly facial animations, expressions, and movement
Real-time facial animation with advanced lip-sync, eye tracking, and emotional expressions
"""

import math
import time
import random
import logging
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np

# Import the new utility modules
from utils.face_animator import FaceAnimator, FacialFeature
from utils.lip_sync import LipSyncEngine, LipSyncFrame
from utils.eye_tracker import EyeTracker, GazeTarget, BlinkType

logger = logging.getLogger(__name__)

class Expression(Enum):
    """Holly's enhanced facial expressions"""
    NEUTRAL = "neutral"
    THINKING = "thinking"
    AMUSED = "amused"
    CONFUSED = "confused"
    SMUG = "smug"
    BORED = "bored"
    SENILE = "senile"
    MISCHIEVOUS = "mischievous"
    DEFENSIVE = "defensive"
    PLEASED = "pleased"

@dataclass
class FaceState:
    """Enhanced state of Holly's face with more detailed parameters"""
    expression: Expression = Expression.NEUTRAL
    mouth_open: float = 0.0  # 0.0 to 1.0
    mouth_width: float = 0.0  # -1.0 to 1.0 (narrow to wide)
    mouth_pucker: float = 0.0  # 0.0 to 1.0 (spread to pursed)
    eye_position: Tuple[float, float] = (0.0, 0.0)  # -1.0 to 1.0
    left_blink: float = 1.0  # 0.0 closed, 1.0 open
    right_blink: float = 1.0  # 0.0 closed, 1.0 open
    pupil_dilation: float = 0.5  # 0.0 to 1.0
    head_rotation: float = 0.0  # degrees
    head_position: Tuple[float, float] = (0.0, 0.0)
    eyebrow_left: float = 0.0  # -1.0 to 1.0
    eyebrow_right: float = 0.0  # -1.0 to 1.0
    emotion_intensity: float = 0.5  # 0.0 to 1.0
    senility_factor: float = 0.7  # Holly's current senility level

class AnimationEngine:
    """Enhanced animation engine managing Holly's complex facial animations"""
    
    def __init__(self, screen_size: Tuple[int, int]):
        """Initialize enhanced animation engine"""
        self.screen_width, self.screen_height = screen_size
        self.face_state = FaceState()
        
        # Initialize animation subsystems
        self.face_animator = FaceAnimator()
        self.lip_sync_engine = LipSyncEngine()
        self.eye_tracker = EyeTracker()
        
        # Animation timing
        self.time_offset = time.time()
        self.last_update_time = 0
        self.frame_count = 0
        
        # Current animation state
        self.current_lip_sync_frames = []
        self.lip_sync_start_time = 0
        self.is_speaking = False
        
        # Idle behavior parameters
        self.idle_behaviors = {
            'breathing': {'frequency': 0.02, 'amplitude': 0.1},
            'micro_movements': {'frequency': 0.001, 'amplitude': 0.02},
            'spontaneous_expressions': {'frequency': 0.0001, 'duration': 2.0}
        }
        
        # Expression blending
        self.expression_blend_weights = {}
        self.target_expression = Expression.NEUTRAL
        self.expression_transition_speed = 0.05
        
        # Holly-specific animation characteristics
        self.senility_effects = {
            'eye_dart_frequency': 0.002,
            'confused_blink_chance': 0.001,
            'expression_drift': 0.0005
        }
        
        logger.info("Enhanced animation engine initialized")
    
    def update(self):
        """Enhanced update loop with all animation subsystems"""
        current_time = time.time() - self.time_offset
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        self.frame_count += 1
        
        # Update all animation subsystems
        facial_features = self.face_animator.update(delta_time)
        eye_state = self.eye_tracker.update(delta_time)
        
        # Update lip sync if speaking
        if self.is_speaking and self.current_lip_sync_frames:
            mouth_shape = self.lip_sync_engine.get_mouth_shape_at_time(
                self.current_lip_sync_frames,
                current_time - self.lip_sync_start_time
            )
            
            # Apply lip sync to face state
            self.face_state.mouth_open = mouth_shape.height
            self.face_state.mouth_width = mouth_shape.width
            self.face_state.mouth_pucker = mouth_shape.pucker
        
        # Apply facial features to face state
        self._apply_facial_features_to_state(facial_features)
        
        # Apply eye state to face state
        self.face_state.eye_position = (eye_state.left_eye_x, eye_state.left_eye_y)
        self.face_state.left_blink = eye_state.left_blink
        self.face_state.right_blink = eye_state.right_blink
        self.face_state.pupil_dilation = eye_state.pupil_dilation
        
        # Update idle behaviors
        self._update_idle_behaviors(current_time)
        
        # Apply Holly's senility effects
        self._apply_senility_effects(current_time)
        
        # Update head floating animation
        self._update_head_floating(current_time)
        
        # Blend expressions
        self._update_expression_blending()
    
    def _apply_facial_features_to_state(self, facial_features: Dict[FacialFeature, float]):
        """Apply facial animator output to face state"""
        if FacialFeature.LEFT_EYEBROW in facial_features:
            self.face_state.eyebrow_left = facial_features[FacialFeature.LEFT_EYEBROW]
        
        if FacialFeature.RIGHT_EYEBROW in facial_features:
            self.face_state.eyebrow_right = facial_features[FacialFeature.RIGHT_EYEBROW]
        
        # Apply mouth features if not overridden by lip sync
        if not self.is_speaking:
            if FacialFeature.MOUTH in facial_features:
                mouth_value = facial_features[FacialFeature.MOUTH]
                self.face_state.mouth_open = max(0.0, mouth_value)
                self.face_state.mouth_width = mouth_value * 0.5
    
    def _update_idle_behaviors(self, current_time: float):
        """Update Holly's idle behaviors"""
        # Breathing animation
        breathing = self.idle_behaviors['breathing']
        breathing_offset = math.sin(current_time * breathing['frequency']) * breathing['amplitude']
        
        # Apply breathing to head position
        head_x, head_y = self.face_state.head_position
        self.face_state.head_position = (head_x, head_y + breathing_offset * 0.02)
        
        # Micro-movements
        if random.random() < self.idle_behaviors['micro_movements']['frequency']:
            micro_amplitude = self.idle_behaviors['micro_movements']['amplitude']
            micro_x = random.uniform(-micro_amplitude, micro_amplitude)
            micro_y = random.uniform(-micro_amplitude, micro_amplitude)
            
            current_x, current_y = self.face_state.head_position
            self.face_state.head_position = (
                current_x + micro_x,
                current_y + micro_y
            )
        
        # Spontaneous micro-expressions
        if random.random() < self.idle_behaviors['spontaneous_expressions']['frequency']:
            self._trigger_micro_expression()
    
    def _apply_senility_effects(self, current_time: float):
        """Apply Holly's senility effects to animations"""
        senility = self.face_state.senility_factor
        
        # Random eye darts (senile confusion)
        if random.random() < self.senility_effects['eye_dart_frequency'] * senility:
            random_targets = [GazeTarget.LEFT, GazeTarget.RIGHT, GazeTarget.UP, GazeTarget.RANDOM]
            self.eye_tracker.look_at(random.choice(random_targets), duration=0.2)
        
        # Confused blinking
        if random.random() < self.senility_effects['confused_blink_chance'] * senility:
            self.eye_tracker.blink(BlinkType.SENILE)
        
        # Expression drift (senile expression changes)
        if random.random() < self.senility_effects['expression_drift'] * senility:
            senile_expressions = [Expression.CONFUSED, Expression.SENILE, Expression.BORED]
            if self.face_state.expression not in senile_expressions:
                self.set_expression(random.choice(senile_expressions), intensity=0.3)
    
    def _update_head_floating(self, current_time: float):
        """Update Holly's characteristic floating head movement"""
        # Enhanced floating motion with multiple frequency components
        float_x = (math.sin(current_time * 0.3) * 0.03 + 
                  math.sin(current_time * 0.7) * 0.01)
        float_y = (math.cos(current_time * 0.2) * 0.025 + 
                  math.cos(current_time * 0.8) * 0.008)
        
        # Occasional larger movements (Holly looking around)
        if random.random() < 0.0001:  # Very rare
            float_x += random.uniform(-0.1, 0.1)
            float_y += random.uniform(-0.05, 0.05)
        
        # Apply floating motion
        self.face_state.head_position = (float_x, float_y)
        
        # Subtle head rotation
        rotation_cycle = math.sin(current_time * 0.15) * 2.0  # ±2 degrees
        self.face_state.head_rotation = rotation_cycle
    
    def _update_expression_blending(self):
        """Update expression blending and transitions"""
        # Smooth transition to target expression
        if self.face_state.expression != self.target_expression:
            # Fade out current expression
            self.face_state.emotion_intensity = max(0.0, 
                self.face_state.emotion_intensity - self.expression_transition_speed)
            
            # Switch to target when intensity is low
            if self.face_state.emotion_intensity <= 0.1:
                self.face_state.expression = self.target_expression
        else:
            # Fade in target expression
            self.face_state.emotion_intensity = min(1.0,
                self.face_state.emotion_intensity + self.expression_transition_speed)
    
    def _trigger_micro_expression(self):
        """Trigger a brief micro-expression"""
        micro_expressions = [
            Expression.CONFUSED, Expression.THINKING, Expression.AMUSED,
            Expression.SENILE, Expression.MISCHIEVOUS
        ]
        
        micro_expr = random.choice(micro_expressions)
        self.face_animator.trigger_micro_expression(micro_expr.value, duration=0.3)
        
        logger.debug(f"Triggered micro-expression: {micro_expr.value}")
    
    def set_expression(self, expression: Expression, intensity: float = 1.0, 
                      immediate: bool = False):
        """Set Holly's facial expression with enhanced control"""
        self.target_expression = expression
        
        # Update face animator
        self.face_animator.set_expression(expression.value, intensity, immediate)
        
        # Update eye tracker based on expression
        if expression == Expression.THINKING:
            self.eye_tracker.start_thinking_mode()
        elif expression == Expression.CONFUSED:
            self.eye_tracker.set_confusion_level(0.8)
            self.eye_tracker.look_at(GazeTarget.RANDOM)
        elif expression == Expression.SENILE:
            self.eye_tracker.set_confusion_level(1.0)
            self.eye_tracker.blink(BlinkType.SENILE)
        elif expression == Expression.AMUSED:
            self.eye_tracker.look_at(GazeTarget.USER)
        else:
            self.eye_tracker.stop_thinking_mode()
            self.eye_tracker.set_confusion_level(0.0)
        
        if immediate:
            self.face_state.expression = expression
            self.face_state.emotion_intensity = intensity
        
        logger.debug(f"Set expression to: {expression.value} (intensity: {intensity})")
    
    def start_speaking(self, text: str, speech_rate: float = 160):
        """Start speaking animation with enhanced lip sync"""
        self.is_speaking = True
        
        # Generate lip sync data
        self.current_lip_sync_frames = self.lip_sync_engine.start_speaking(text, speech_rate)
        self.lip_sync_start_time = time.time() - self.time_offset
        
        # Notify face animator
        self.face_animator.start_speaking(text)
        
        # Update eye behavior for speaking
        self.eye_tracker.look_at(GazeTarget.USER, duration=0.5)
        
        logger.debug(f"Started speaking: {text[:30]}...")
    
    def stop_speaking(self):
        """Stop speaking animation"""
        self.is_speaking = False
        self.current_lip_sync_frames = []
        
        # Notify subsystems
        self.face_animator.stop_speaking()
        self.lip_sync_engine.stop_speaking()
        
        # Return to neutral mouth position
        self.face_state.mouth_open = 0.0
        self.face_state.mouth_width = 0.0
        self.face_state.mouth_pucker = 0.0
        
        logger.debug("Stopped speaking")
    
    def process_animation_data(self, anim_data: Dict[str, Any]):
        """Process animation data from external sources with enhanced handling"""
        try:
            # Handle expression changes
            if 'expression' in anim_data:
                expression_name = anim_data['expression']
                intensity = anim_data.get('intensity', 1.0)
                immediate = anim_data.get('immediate', False)
                
                if hasattr(Expression, expression_name.upper()):
                    expression = Expression(expression_name.lower())
                    self.set_expression(expression, intensity, immediate)
            
            # Handle speaking state
            if 'speaking' in anim_data:
                if anim_data['speaking']:
                    text = anim_data.get('text', '')
                    speech_rate = anim_data.get('speech_rate', 160)
                    self.start_speaking(text, speech_rate)
                else:
                    self.stop_speaking()
            
            # Handle mood changes (map to expressions)
            if 'mood' in anim_data:
                mood = anim_data['mood']
                mood_expressions = {
                    'normal': Expression.NEUTRAL,
                    'thinking': Expression.THINKING,
                    'amused': Expression.AMUSED,
                    'confused': Expression.CONFUSED,
                    'pleased': Expression.PLEASED,
                    'defensive': Expression.DEFENSIVE,
                    'smug': Expression.SMUG,
                    'senile': Expression.SENILE
                }
                
                if mood in mood_expressions:
                    self.set_expression(mood_expressions[mood])
            
            # Handle eye movements
            if 'look_at' in anim_data:
                target = anim_data['look_at']
                if hasattr(GazeTarget, target.upper()):
                    gaze_target = GazeTarget(target.upper())
                    duration = anim_data.get('duration', 0.3)
                    self.eye_tracker.look_at(gaze_target, duration)
            
            # Handle blinks
            if 'blink' in anim_data:
                blink_type = anim_data.get('blink_type', 'normal')
                if hasattr(BlinkType, blink_type.upper()):
                    blink = BlinkType(blink_type.upper())
                    self.eye_tracker.blink(blink)
            
            # Handle senility level updates
            if 'senility_level' in anim_data:
                senility = max(0.0, min(1.0, anim_data['senility_level']))
                self.face_state.senility_factor = senility
                self.eye_tracker.senility_factor = senility
                self.face_animator.senility_factor = senility
            
        except Exception as e:
            logger.error(f"Error processing animation data: {e}")
    
    def get_face_state(self) -> FaceState:
        """Get current enhanced face state for rendering"""
        return self.face_state
    
    def trigger_reaction(self, reaction_type: str):
        """Trigger a specific reaction animation with enhanced behaviors"""
        reactions = {
            'surprise': {
                'expression': Expression.CONFUSED,
                'eye_action': lambda: self.eye_tracker.look_at(GazeTarget.RANDOM),
                'blink': BlinkType.QUICK
            },
            'amusement': {
                'expression': Expression.AMUSED,
                'eye_action': lambda: self.eye_tracker.look_at(GazeTarget.USER),
                'blink': BlinkType.NORMAL
            },
            'thinking': {
                'expression': Expression.THINKING,
                'eye_action': lambda: self.eye_tracker.start_thinking_mode(),
                'blink': BlinkType.SLOW
            },
            'boredom': {
                'expression': Expression.BORED,
                'eye_action': lambda: self.eye_tracker.look_at(GazeTarget.DOWN),
                'blink': BlinkType.SLOW
            },
            'mischief': {
                'expression': Expression.MISCHIEVOUS,
                'eye_action': lambda: self.eye_tracker.blink(BlinkType.WINK_RIGHT),
                'blink': None
            },
            'senility': {
                'expression': Expression.SENILE,
                'eye_action': lambda: self.eye_tracker.set_confusion_level(1.0),
                'blink': BlinkType.SENILE
            }
        }
        
        if reaction_type in reactions:
            reaction = reactions[reaction_type]
            
            # Set expression
            self.set_expression(reaction['expression'])
            
            # Perform eye action
            if reaction['eye_action']:
                reaction['eye_action']()
            
            # Trigger blink
            if reaction['blink']:
                self.eye_tracker.blink(reaction['blink'])
            
            logger.debug(f"Triggered reaction: {reaction_type}")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get comprehensive debug information"""
        return {
            'frame_count': self.frame_count,
            'current_expression': self.face_state.expression.value,
            'target_expression': self.target_expression.value,
            'emotion_intensity': round(self.face_state.emotion_intensity, 2),
            'is_speaking': self.is_speaking,
            'lip_sync_frames': len(self.current_lip_sync_frames),
            'senility_factor': round(self.face_state.senility_factor, 2),
            'head_position': (round(self.face_state.head_position[0], 3), 
                            round(self.face_state.head_position[1], 3)),
            'eye_position': (round(self.face_state.eye_position[0], 3),
                           round(self.face_state.eye_position[1], 3)),
            'mouth_state': {
                'open': round(self.face_state.mouth_open, 2),
                'width': round(self.face_state.mouth_width, 2),
                'pucker': round(self.face_state.mouth_pucker, 2)
            },
            'face_animator': self.face_animator.get_debug_info(),
            'eye_tracker': self.eye_tracker.get_debug_info(),
            'lip_sync': self.lip_sync_engine.get_debug_info()
        }
