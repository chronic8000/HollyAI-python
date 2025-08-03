"""
Audio Manager - Text-to-speech with Holly's voice characteristics
Real-time audio processing and lip-sync coordination
"""

import asyncio
import threading
import logging
import time
import tempfile
import os
from typing import Optional, Dict, Any
from queue import Queue, Empty

try:
    import pyttsx3
    import pygame
except ImportError as e:
    logging.error(f"Missing audio dependencies: {e}")
    logging.error("Please install: pyttsx3 pygame")

logger = logging.getLogger(__name__)

class AudioManager:
    """Manages text-to-speech and audio output for Holly"""
    
    def __init__(self, response_queue: asyncio.Queue, animation_queue: asyncio.Queue):
        """Initialize audio manager"""
        self.response_queue = response_queue
        self.animation_queue = animation_queue
        self.is_running = False
        self.is_speaking = False
        
        # Initialize TTS engine
        self.tts_engine = None
        self.voice_config = {
            'rate': 160,      # Words per minute (slower for Holly's delivery)
            'volume': 0.9,    # Volume level
            'voice_index': 0  # Voice selection
        }
        
        # Audio processing
        self.audio_queue = Queue()
        self.current_audio_file = None
        
        self._initialize_tts()
        
    def _initialize_tts(self):
        """Initialize text-to-speech engine with fallback for headless environments"""
        try:
            # Set environment variable to prevent audio system errors
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
            
            self.tts_engine = pyttsx3.init()
            
            # Configure voice for Holly (Norman Lovett style)
            voices = self.tts_engine.getProperty('voices')
            
            if voices:
                # Try to find a suitable British male voice
                british_voice = None
                for i, voice in enumerate(voices):
                    voice_name = voice.name.lower()
                    if any(keyword in voice_name for keyword in ['british', 'english', 'uk', 'male']):
                        british_voice = i
                        break
                
                # Configure voice properties
                if british_voice is not None:
                    self.tts_engine.setProperty('voice', voices[british_voice].id)
                
                self.tts_engine.setProperty('rate', self.voice_config['rate'])
                self.tts_engine.setProperty('volume', self.voice_config['volume'])
                
                logger.info("TTS engine initialized successfully")
            else:
                logger.warning("No TTS voices available - running in silent mode")
                self.tts_engine = None
            
        except Exception as e:
            logger.warning(f"TTS engine initialization failed: {e}")
            logger.info("Running in silent mode - visual-only Holly")
            self.tts_engine = None
    
    def start(self):
        """Start audio manager processing"""
        self.is_running = True
        logger.info("Audio manager started")
        
        # Main processing loop
        while self.is_running:
            try:
                # Check for new responses to speak
                if not self.response_queue.empty():
                    try:
                        response_text = self.response_queue.get_nowait()
                        self._speak_text(response_text)
                    except:
                        pass
                
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                logger.error(f"Error in audio manager loop: {e}")
                time.sleep(0.1)
    
    def _speak_text(self, text: str):
        """Convert text to speech and play audio"""
        if not self.tts_engine or not text.strip():
            return
        
        try:
            self.is_speaking = True
            
            # Notify animation engine that speaking started
            try:
                self.animation_queue.put_nowait({
                    'speaking': True,
                    'text': text
                })
            except:
                pass
            
            logger.info(f"Speaking: {text[:50]}...")
            
            # Generate and play speech
            if hasattr(self.tts_engine, 'say') and hasattr(self.tts_engine, 'runAndWait'):
                # Process text through Holly's speech patterns
                processed_text = self._process_text_for_speech(text)
                
                # Generate speech
                self.tts_engine.say(processed_text)
                self.tts_engine.runAndWait()
            
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
        finally:
            self.is_speaking = False
            
            # Notify animation engine that speaking stopped
            try:
                self.animation_queue.put_nowait({
                    'speaking': False
                })
            except:
                pass
    
    def _process_text_for_speech(self, text: str) -> str:
        """Process text for better speech synthesis"""
        # Add pauses for better delivery timing
        processed = text.replace('...', ', pause, ')
        processed = processed.replace('..', ', pause, ')
        
        # Emphasize certain Holly characteristics
        processed = processed.replace('Right,', 'Right, pause, ')
        processed = processed.replace('Oh,', 'Oh, pause, ')
        processed = processed.replace('Well,', 'Well, pause, ')
        
        # Slow down for dramatic effect on certain phrases
        if 'IQ' in text:
            processed = processed.replace('IQ', 'I, Q,')
        
        if '6000' in text or '6,000' in text:
            processed = processed.replace('6000', 'six thousand')
            processed = processed.replace('6,000', 'six thousand')
        
        return processed
    
    def adjust_voice_settings(self, rate: Optional[int] = None, volume: Optional[float] = None):
        """Adjust voice settings"""
        if not self.tts_engine:
            return
        
        try:
            if rate is not None:
                self.voice_config['rate'] = rate
                self.tts_engine.setProperty('rate', rate)
                logger.info(f"Voice rate set to: {rate}")
            
            if volume is not None:
                self.voice_config['volume'] = volume
                self.tts_engine.setProperty('volume', volume)
                logger.info(f"Voice volume set to: {volume}")
                
        except Exception as e:
            logger.error(f"Error adjusting voice settings: {e}")
    
    def stop_speaking(self):
        """Stop current speech"""
        if self.tts_engine and self.is_speaking:
            try:
                self.tts_engine.stop()
                self.is_speaking = False
                
                # Notify animation engine
                try:
                    self.animation_queue.put_nowait({
                        'speaking': False
                    })
                except:
                    pass
                
                logger.info("Speech stopped")
                
            except Exception as e:
                logger.error(f"Error stopping speech: {e}")
    
    def is_currently_speaking(self) -> bool:
        """Check if currently speaking"""
        return self.is_speaking
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get current voice configuration"""
        if not self.tts_engine:
            return {}
        
        try:
            voices = self.tts_engine.getProperty('voices')
            current_voice = self.tts_engine.getProperty('voice')
            
            voice_info = {
                'rate': self.voice_config['rate'],
                'volume': self.voice_config['volume'],
                'current_voice': current_voice,
                'available_voices': [voice.name for voice in voices] if voices else []
            }
            
            return voice_info
            
        except Exception as e:
            logger.error(f"Error getting voice info: {e}")
            return {}
    
    def set_voice_by_name(self, voice_name: str) -> bool:
        """Set voice by name"""
        if not self.tts_engine:
            return False
        
        try:
            voices = self.tts_engine.getProperty('voices')
            
            for voice in voices:
                if voice_name.lower() in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    logger.info(f"Voice set to: {voice.name}")
                    return True
            
            logger.warning(f"Voice '{voice_name}' not found")
            return False
            
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def stop(self):
        """Stop audio manager"""
        logger.info("Stopping audio manager...")
        self.is_running = False
        
        if self.is_speaking:
            self.stop_speaking()
        
        logger.info("Audio manager stopped")
