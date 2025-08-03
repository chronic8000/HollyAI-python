"""
Face Animator - Advanced facial animation system for Holly
Handles complex facial expressions, micro-expressions, and emotional states
"""

import math
import time
import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class FacialFeature(Enum):
    """Individual facial features that can be animated"""
    LEFT_EYE = "left_eye"
    RIGHT_EYE = "right_eye"
    LEFT_EYEBROW = "left_eyebrow"
    RIGHT_EYEBROW = "right_eyebrow"
    MOUTH = "mouth"
    NOSE = "nose"
    CHEEKS = "cheeks"
    FOREHEAD = "forehead"

@dataclass
class FacialKeyframe:
    """A keyframe for facial animation"""
    timestamp: float
    feature: FacialFeature
    value: float
    easing: str = "linear"  # linear, ease_in, ease_out, ease_in_out

@dataclass
class ExpressionBlend:
    """Blend between multiple expressions"""
    base_expression: str
    overlay_expressions: Dict[str, float]  # expression_name: weight
    transition_time: float

class FaceAnimator:
    """Advanced facial animation system for Holly"""
    
    def __init__(self):
        """Initialize the face animator"""
        self.current_time = 0.0
        self.animation_queue = []
        self.active_animations = {}
        self.expression_cache = {}
        
        # Expression definitions based on Holly's character
        self.expressions = self._define_expressions()
        
        # Animation parameters
        self.default_transition_time = 0.3
        self.micro_expression_probability = 0.1
        self.senility_factor = 0.7
        
        logger.info("Face animator initialized with Holly expressions")
    
    def _define_expressions(self) -> Dict[str, Dict[FacialFeature, float]]:
        """Define Holly's facial expressions based on his character"""
        return {
            'neutral': {
                FacialFeature.LEFT_EYE: 0.0,
                FacialFeature.RIGHT_EYE: 0.0,
                FacialFeature.LEFT_EYEBROW: 0.0,
                FacialFeature.RIGHT_EYEBROW: 0.0,
                FacialFeature.MOUTH: 0.0,
                FacialFeature.CHEEKS: 0.0,
                FacialFeature.FOREHEAD: 0.0
            },
            'thinking': {
                FacialFeature.LEFT_EYE: -0.3,  # Slightly squinted
                FacialFeature.RIGHT_EYE: -0.3,
                FacialFeature.LEFT_EYEBROW: 0.4,  # Raised
                FacialFeature.RIGHT_EYEBROW: 0.2,  # Asymmetrical (Holly's quirk)
                FacialFeature.MOUTH: -0.2,  # Slight frown
                FacialFeature.FOREHEAD: 0.3  # Wrinkled
            },
            'amused': {
                FacialFeature.LEFT_EYE: 0.3,  # Slightly wider
                FacialFeature.RIGHT_EYE: 0.3,
                FacialFeature.LEFT_EYEBROW: 0.1,
                FacialFeature.RIGHT_EYEBROW: 0.1,
                FacialFeature.MOUTH: 0.6,  # Smile
                FacialFeature.CHEEKS: 0.4  # Raised cheeks
            },
            'confused': {
                FacialFeature.LEFT_EYE: 0.1,
                FacialFeature.RIGHT_EYE: 0.1,
                FacialFeature.LEFT_EYEBROW: 0.6,  # Very raised
                FacialFeature.RIGHT_EYEBROW: -0.2,  # One down (confusion)
                FacialFeature.MOUTH: -0.1,
                FacialFeature.FOREHEAD: 0.5
            },
            'smug': {
                FacialFeature.LEFT_EYE: -0.2,  # Half-closed
                FacialFeature.RIGHT_EYE: -0.2,
                FacialFeature.LEFT_EYEBROW: 0.2,
                FacialFeature.RIGHT_EYEBROW: 0.4,  # Asymmetrical smugness
                FacialFeature.MOUTH: 0.4,  # Slight smile
                FacialFeature.CHEEKS: 0.2
            },
            'bored': {
                FacialFeature.LEFT_EYE: -0.5,  # Half-closed
                FacialFeature.RIGHT_EYE: -0.5,
                FacialFeature.LEFT_EYEBROW: -0.3,  # Drooped
                FacialFeature.RIGHT_EYEBROW: -0.3,
                FacialFeature.MOUTH: -0.3,  # Slight frown
                FacialFeature.CHEEKS: -0.2
            },
            'senile': {
                FacialFeature.LEFT_EYE: 0.2,  # Wider, vacant
                FacialFeature.RIGHT_EYE: 0.1,  # Asymmetrical
                FacialFeature.LEFT_EYEBROW: 0.3,
                FacialFeature.RIGHT_EYEBROW: 0.1,
                FacialFeature.MOUTH: 0.1,  # Slight open
                FacialFeature.FOREHEAD: 0.2
            },
            'mischievous': {
                FacialFeature.LEFT_EYE: -0.1,  # Slightly narrowed
                FacialFeature.RIGHT_EYE: 0.1,  # Wink-like asymmetry
                FacialFeature.LEFT_EYEBROW: 0.4,
                FacialFeature.RIGHT_EYEBROW: 0.2,
                FacialFeature.MOUTH: 0.5,  # Grin
                FacialFeature.CHEEKS: 0.3
            },
            'speaking_a': {  # Vowel mouth positions
                FacialFeature.MOUTH: 0.8
            },
            'speaking_e': {
                FacialFeature.MOUTH: 0.6
            },
            'speaking_i': {
                FacialFeature.MOUTH: 0.3
            },
            'speaking_o': {
                FacialFeature.MOUTH: 0.9
            },
            'speaking_u': {
                FacialFeature.MOUTH: 0.4
            },
            'speaking_consonant': {
                FacialFeature.MOUTH: 0.2
            },
            'speaking_neutral': {
                FacialFeature.LEFT_EYE: 0.0,
                FacialFeature.RIGHT_EYE: 0.0,
                FacialFeature.LEFT_EYEBROW: 0.1,  # Slightly raised when speaking
                FacialFeature.RIGHT_EYEBROW: 0.1,
                FacialFeature.MOUTH: 0.2,  # Slightly open for speech
                FacialFeature.CHEEKS: 0.0,
                FacialFeature.FOREHEAD: 0.0
            }
        }
    
    def update(self, delta_time: float) -> Dict[FacialFeature, float]:
        """Update animation state and return current facial feature values"""
        self.current_time += delta_time
        
        # Process animation queue
        self._process_animation_queue()
        
        # Update active animations
        current_values = self._update_active_animations()
        
        # Add micro-expressions for Holly's senility
        current_values = self._apply_senility_effects(current_values)
        
        # Add subtle idle animations
        current_values = self._apply_idle_animations(current_values)
        
        return current_values
    
    def set_expression(self, expression_name: str, intensity: float = 1.0, 
                      transition_time: Optional[float] = None, immediate: bool = False):
        """Set facial expression with optional transition"""
        if expression_name not in self.expressions:
            logger.warning(f"Unknown expression: {expression_name}")
            return
        
        transition_time = transition_time or self.default_transition_time
        
        if immediate:
            # Set immediately without transition
            self.active_animations[expression_name] = {
                'start_time': self.current_time,
                'end_time': self.current_time,
                'start_values': self.expressions[expression_name].copy(),
                'end_values': self.expressions[expression_name].copy(),
                'intensity': intensity
            }
        else:
            # Add to animation queue for smooth transition
            self.animation_queue.append({
                'type': 'expression',
                'expression': expression_name,
                'intensity': intensity,
                'transition_time': transition_time,
                'start_time': self.current_time
            })
        
        logger.debug(f"Set expression: {expression_name} (intensity: {intensity})")
    
    def blend_expressions(self, base_expression: str, overlays: Dict[str, float]):
        """Blend multiple expressions together"""
        if base_expression not in self.expressions:
            logger.warning(f"Unknown base expression: {base_expression}")
            return
        
        # Start with base expression
        blended_values = self.expressions[base_expression].copy()
        
        # Apply overlays
        for overlay_name, weight in overlays.items():
            if overlay_name in self.expressions:
                overlay_values = self.expressions[overlay_name]
                for feature, value in overlay_values.items():
                    if feature in blended_values:
                        blended_values[feature] += value * weight
        
        # Clamp values to valid range
        for feature in blended_values:
            blended_values[feature] = max(-1.0, min(1.0, blended_values[feature]))
        
        # Apply blended expression
        self.active_animations['blend'] = {
            'start_time': self.current_time,
            'end_time': self.current_time,
            'start_values': blended_values,
            'end_values': blended_values,
            'intensity': 1.0
        }
    
    def animate_speaking(self, phoneme: str, intensity: float = 1.0):
        """Animate mouth for specific phoneme"""
        phoneme_expressions = {
            'a': 'speaking_a', 'e': 'speaking_e', 'i': 'speaking_i',
            'o': 'speaking_o', 'u': 'speaking_u'
        }
        
        expression = phoneme_expressions.get(phoneme.lower(), 'speaking_consonant')
        
        # Quick mouth animation for speech
        self.animation_queue.append({
            'type': 'speaking',
            'expression': expression,
            'intensity': intensity,
            'transition_time': 0.1,  # Very fast for speech
            'start_time': self.current_time
        })
    
    def trigger_micro_expression(self, expression_name: str, duration: float = 0.5):
        """Trigger a brief micro-expression (Holly's senile moments)"""
        self.animation_queue.append({
            'type': 'micro',
            'expression': expression_name,
            'intensity': 0.6,
            'duration': duration,
            'start_time': self.current_time
        })
        
        logger.debug(f"Triggered micro-expression: {expression_name}")
    
    def add_custom_animation(self, feature: FacialFeature, keyframes: List[FacialKeyframe]):
        """Add custom keyframe animation for a specific feature"""
        self.animation_queue.append({
            'type': 'custom',
            'feature': feature,
            'keyframes': keyframes,
            'start_time': self.current_time
        })
    
    def _process_animation_queue(self):
        """Process queued animations"""
        processed_animations = []
        
        for animation in self.animation_queue:
            if animation['start_time'] <= self.current_time:
                self._start_animation(animation)
                processed_animations.append(animation)
        
        # Remove processed animations
        for animation in processed_animations:
            self.animation_queue.remove(animation)
    
    def _start_animation(self, animation: Dict):
        """Start a specific animation"""
        anim_type = animation['type']
        
        if anim_type in ['expression', 'speaking', 'micro']:
            expression_name = animation['expression']
            if expression_name in self.expressions:
                target_values = self.expressions[expression_name].copy()
                
                # Scale by intensity
                intensity = animation['intensity']
                for feature in target_values:
                    target_values[feature] *= intensity
                
                # Get current values as start
                current_values = self._get_current_values()
                
                # Get transition time with fallback
                transition_time = animation.get('transition_time', self.default_transition_time)
                if anim_type == 'micro':
                    transition_time = animation.get('duration', 0.5)
                
                end_time = self.current_time + transition_time
                
                self.active_animations[f"{anim_type}_{expression_name}"] = {
                    'start_time': self.current_time,
                    'end_time': end_time,
                    'start_values': current_values,
                    'end_values': target_values,
                    'intensity': intensity
                }
    
    def _update_active_animations(self) -> Dict[FacialFeature, float]:
        """Update all active animations and return combined values"""
        final_values = {feature: 0.0 for feature in FacialFeature}
        completed_animations = []
        
        for anim_name, animation in self.active_animations.items():
            if self.current_time >= animation['end_time']:
                # Animation completed
                completed_animations.append(anim_name)
                continue
            
            # Calculate progress
            total_time = animation['end_time'] - animation['start_time']
            if total_time <= 0:
                progress = 1.0
            else:
                progress = (self.current_time - animation['start_time']) / total_time
            
            # Apply easing
            eased_progress = self._apply_easing(progress, 'ease_out')
            
            # Interpolate values
            start_values = animation['start_values']
            end_values = animation['end_values']
            
            for feature in FacialFeature:
                if feature in start_values and feature in end_values:
                    start_val = start_values[feature]
                    end_val = end_values[feature]
                    current_val = start_val + (end_val - start_val) * eased_progress
                    
                    # Add to final values (blend multiple animations)
                    final_values[feature] += current_val
        
        # Remove completed animations
        for anim_name in completed_animations:
            del self.active_animations[anim_name]
        
        # Clamp final values
        for feature in final_values:
            final_values[feature] = max(-1.0, min(1.0, final_values[feature]))
        
        return final_values
    
    def _apply_senility_effects(self, values: Dict[FacialFeature, float]) -> Dict[FacialFeature, float]:
        """Apply Holly's senility effects (random micro-expressions)"""
        if random.random() < self.micro_expression_probability * self.senility_factor:
            # Random senile moment
            senile_effects = {
                FacialFeature.LEFT_EYEBROW: random.uniform(-0.1, 0.2),
                FacialFeature.RIGHT_EYEBROW: random.uniform(-0.1, 0.2),
                FacialFeature.LEFT_EYE: random.uniform(-0.1, 0.1),
                FacialFeature.RIGHT_EYE: random.uniform(-0.1, 0.1)
            }
            
            for feature, effect in senile_effects.items():
                values[feature] += effect * 0.3  # Subtle effect
        
        return values
    
    def _apply_idle_animations(self, values: Dict[FacialFeature, float]) -> Dict[FacialFeature, float]:
        """Apply subtle idle animations"""
        # Breathing effect on cheeks
        breathing = math.sin(self.current_time * 0.5) * 0.02
        values[FacialFeature.CHEEKS] += breathing
        
        # Occasional eye darts (Holly looking around)
        if random.random() < 0.001:  # Very rare
            eye_dart = random.uniform(-0.1, 0.1)
            values[FacialFeature.LEFT_EYE] += eye_dart
            values[FacialFeature.RIGHT_EYE] += eye_dart
        
        return values
    
    def _get_current_values(self) -> Dict[FacialFeature, float]:
        """Get current facial feature values"""
        if not self.active_animations:
            return {feature: 0.0 for feature in FacialFeature}
        
        # Get the most recent animation's end values
        latest_animation = max(self.active_animations.values(), 
                             key=lambda a: a['start_time'])
        return latest_animation['end_values'].copy()
    
    def _apply_easing(self, progress: float, easing_type: str) -> float:
        """Apply easing function to animation progress"""
        if easing_type == 'linear':
            return progress
        elif easing_type == 'ease_in':
            return progress * progress
        elif easing_type == 'ease_out':
            return 1 - (1 - progress) * (1 - progress)
        elif easing_type == 'ease_in_out':
            if progress < 0.5:
                return 2 * progress * progress
            else:
                return 1 - 2 * (1 - progress) * (1 - progress)
        else:
            return progress
    
    def get_expression_intensity(self, expression_name: str) -> float:
        """Get current intensity of a specific expression"""
        for anim_name, animation in self.active_animations.items():
            if expression_name in anim_name:
                return animation.get('intensity', 0.0)
        return 0.0
    
    def stop_all_animations(self):
        """Stop all current animations"""
        self.active_animations.clear()
        self.animation_queue.clear()
        logger.debug("All animations stopped")
    
    def start_speaking(self, text: str):
        """Start speaking animation mode"""
        # Add subtle mouth animation for speaking
        self.set_expression('speaking_neutral', intensity=0.3, transition_time=0.1)
        logger.debug(f"Started speaking animation for: {text[:30]}...")
    
    def stop_speaking(self):
        """Stop speaking animation mode"""
        # Return to neutral mouth position
        self.set_expression('neutral', intensity=1.0, transition_time=0.2)
        logger.debug("Stopped speaking animation")
    
    def get_debug_info(self) -> Dict:
        """Get debug information about current animations"""
        return {
            'active_animations': len(self.active_animations),
            'queued_animations': len(self.animation_queue),
            'current_time': self.current_time,
            'senility_factor': self.senility_factor,
            'animations': list(self.active_animations.keys())
        }
