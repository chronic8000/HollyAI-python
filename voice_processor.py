"""
Voice Processor - Real-time speech recognition and audio input handling
Optimized for minimal latency and continuous listening
"""

import asyncio
import threading
import logging
import time
from typing import Optional, Callable

try:
    import speech_recognition as sr
    import pyaudio
except ImportError as e:
    logging.error(f"Missing speech recognition dependencies: {e}")
    logging.error("Please install: SpeechRecognition pyaudio")

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """Handles real-time speech recognition with minimal latency"""
    
    def __init__(self, speech_queue: asyncio.Queue):
        """Initialize voice processor"""
        self.speech_queue = speech_queue
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_running = False
        self.is_active_listening = False
        self.background_listener = None
        
        # Configuration
        self.energy_threshold = 4000
        self.pause_threshold = 0.8
        self.phrase_threshold = 0.3
        self.non_speaking_duration = 0.5
        
        # Wake word detection
        self.wake_words = ["holly", "computer", "ship", "red dwarf"]
        self.always_listening = True
        
        self._setup_microphone()
        
    def _setup_microphone(self):
        """Setup microphone with optimal settings and fallback for containerized environments"""
        try:
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
            # Configure recognizer for better performance
            self.recognizer.energy_threshold = self.energy_threshold
            self.recognizer.pause_threshold = self.pause_threshold
            self.recognizer.phrase_threshold = self.phrase_threshold
            self.recognizer.non_speaking_duration = self.non_speaking_duration
            
            logger.info("Microphone setup complete")
            
        except Exception as e:
            logger.warning(f"Microphone setup failed: {e}")
            logger.info("Running without voice input - use keyboard for interaction")
            self.microphone = None
    
    def start_listening(self):
        """Start continuous listening in background thread"""
        if not self.microphone:
            logger.error("No microphone available")
            return
        
        self.is_running = True
        logger.info("Starting voice recognition...")
        
        try:
            # Start background listening
            self.background_listener = self.recognizer.listen_in_background(
                self.microphone, 
                self._on_audio_received,
                phrase_time_limit=5
            )
            
            # Keep thread alive
            while self.is_running:
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in voice listening: {e}")
        finally:
            if self.background_listener:
                self.background_listener()
    
    def _on_audio_received(self, recognizer, audio):
        """Callback when audio is received"""
        try:
            self.is_active_listening = True
            
            # Use Google Speech Recognition for better accuracy
            text = recognizer.recognize_google(audio, language='en-US')
            
            if text and len(text.strip()) > 0:
                logger.info(f"Recognized speech: {text}")
                
                # Check if should process (wake word or always listening)
                if self.always_listening or self._contains_wake_word(text):
                    # Queue the recognized text
                    asyncio.run_coroutine_threadsafe(
                        self.speech_queue.put(text),
                        asyncio.get_event_loop()
                    )
        
        except sr.UnknownValueError:
            # Speech was unintelligible
            pass
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
        finally:
            self.is_active_listening = False
    
    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains wake word"""
        text_lower = text.lower()
        return any(wake_word in text_lower for wake_word in self.wake_words)
    
    def manual_trigger(self):
        """Manually trigger listening for next speech"""
        try:
            if not self.microphone:
                logger.error("No microphone available for manual trigger")
                return
            
            logger.info("Manual speech trigger activated")
            
            with self.microphone as source:
                logger.info("Listening for speech...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Process in background thread to avoid blocking
            threading.Thread(
                target=self._process_manual_audio,
                args=(audio,),
                daemon=True
            ).start()
            
        except sr.WaitTimeoutError:
            logger.info("Manual trigger timeout - no speech detected")
        except Exception as e:
            logger.error(f"Error in manual trigger: {e}")
    
    def _process_manual_audio(self, audio):
        """Process manually triggered audio"""
        try:
            self.is_active_listening = True
            text = self.recognizer.recognize_google(audio, language='en-US')
            
            if text and len(text.strip()) > 0:
                logger.info(f"Manual recognition: {text}")
                asyncio.run_coroutine_threadsafe(
                    self.speech_queue.put(text),
                    asyncio.get_event_loop()
                )
        
        except sr.UnknownValueError:
            logger.info("Manual trigger: Speech was unintelligible")
        except sr.RequestError as e:
            logger.error(f"Manual trigger: Speech service error: {e}")
        except Exception as e:
            logger.error(f"Error processing manual audio: {e}")
        finally:
            self.is_active_listening = False
    
    def is_listening(self) -> bool:
        """Check if currently actively listening"""
        return self.is_active_listening
    
    def stop(self):
        """Stop voice processing"""
        logger.info("Stopping voice processor...")
        self.is_running = False
        
        if self.background_listener:
            self.background_listener()
        
        logger.info("Voice processor stopped")
    
    def adjust_sensitivity(self, sensitivity: float):
        """Adjust microphone sensitivity (0.0 to 1.0)"""
        if self.recognizer:
            # Higher sensitivity = lower energy threshold
            base_threshold = 4000
            self.recognizer.energy_threshold = base_threshold * (1.0 - sensitivity + 0.1)
            logger.info(f"Adjusted sensitivity to {sensitivity}, threshold: {self.recognizer.energy_threshold}")
    
    def toggle_always_listening(self):
        """Toggle always listening mode"""
        self.always_listening = not self.always_listening
        mode = "always listening" if self.always_listening else "wake word only"
        logger.info(f"Voice mode changed to: {mode}")
        return self.always_listening
