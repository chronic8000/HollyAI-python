"""
Configuration settings for Holly AI Avatar application
"""

import os
from pathlib import Path

class Config:
    """Application configuration"""
    
    # Display settings
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    FULLSCREEN = True
    FPS = 60
    
    # Audio settings
    AUDIO_SAMPLE_RATE = 22050
    AUDIO_CHUNK_SIZE = 1024
    VOICE_RATE = 160  # Words per minute
    VOICE_VOLUME = 0.9
    
    # Voice recognition settings
    ENERGY_THRESHOLD = 4000
    PAUSE_THRESHOLD = 0.8
    PHRASE_THRESHOLD = 0.3
    ALWAYS_LISTENING = True
    
    # Holly personality settings
    SENILITY_LEVEL = 0.7
    HUMOR_FREQUENCY = 0.3
    NON_SEQUITUR_CHANCE = 0.3
    
    # AI settings
    GEMINI_MODEL = "gemini-2.5-flash"
    MAX_CONVERSATION_HISTORY = 10
    RESPONSE_TIMEOUT = 10.0
    
    # Animation settings
    FACE_SCALE_FACTOR = 1.0
    ANIMATION_SMOOTHNESS = 0.05
    BLINK_FREQUENCY = 3.0  # seconds
    EYE_MOVEMENT_FREQUENCY = 4.0  # seconds
    
    # File paths
    BASE_DIR = Path(__file__).parent
    ASSETS_DIR = BASE_DIR / "assets"
    TEMPLATES_DIR = BASE_DIR / "templates"
    
    # Environment variables
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "default_key")
    
    # Debug settings
    DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = "INFO" if not DEBUG_MODE else "DEBUG"
    
    @classmethod
    def get_display_mode(cls):
        """Get display mode flags"""
        import pygame
        
        flags = 0
        if cls.FULLSCREEN:
            flags |= pygame.FULLSCREEN
        
        return flags
    
    @classmethod
    def get_voice_config(cls):
        """Get voice configuration dictionary"""
        return {
            'rate': cls.VOICE_RATE,
            'volume': cls.VOICE_VOLUME,
            'sample_rate': cls.AUDIO_SAMPLE_RATE
        }
    
    @classmethod
    def get_animation_config(cls):
        """Get animation configuration dictionary"""
        return {
            'scale_factor': cls.FACE_SCALE_FACTOR,
            'smoothness': cls.ANIMATION_SMOOTHNESS,
            'blink_frequency': cls.BLINK_FREQUENCY,
            'eye_movement_frequency': cls.EYE_MOVEMENT_FREQUENCY
        }
