#!/usr/bin/env python3
"""
Holly AI Avatar - Main Application Entry Point
Real-time AI avatar of Holly from Red Dwarf with voice interaction and facial animation
Enhanced version with improved real-time performance and authentic Holly personality
"""

import sys
import asyncio
import threading
import time
import logging
from pathlib import Path
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import pygame
    import cv2
    import numpy as np
except ImportError as e:
    logger.error(f"Missing required dependencies: {e}")
    logger.error("Please install: pygame opencv-python numpy")
    sys.exit(1)

from holly_ai import HollyAI
from voice_processor import VoiceProcessor
from animation_engine import AnimationEngine
from ui_renderer import UIRenderer
from audio_manager import AudioManager
from config import Config

class HollyAvatarApp:
    """Main application class for Holly AI Avatar"""
    
    def __init__(self):
        """Initialize the Holly Avatar application"""
        self.config = Config()
        self.running = False
        self.clock = None
        
        # Initialize core components
        self.holly_ai = None
        self.voice_processor = None
        self.animation_engine = None
        self.ui_renderer = None
        self.audio_manager = None
        
        # Threading and event loop
        self.loop = None
        self.voice_thread = None
        self.ai_thread = None
        self.audio_thread = None
        
        # Communication queues (thread-safe)
        self.speech_queue = None
        self.response_queue = None
        self.animation_queue = None
        
        # Performance monitoring
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0
        
        # Spontaneous comment system for Holly
        self.last_spontaneous_comment = time.time()
        self.spontaneous_interval = 30.0  # 30 seconds between spontaneous comments
        
    def initialize(self):
        """Initialize all components with enhanced error handling"""
        try:
            logger.info("Initializing Holly AI Avatar...")
            
            # Initialize Pygame with optimized settings
            pygame.init()
            
            # Initialize audio with fallback for containerized environments
            try:
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                logger.info("Audio system initialized successfully")
            except pygame.error as e:
                logger.warning(f"Audio initialization failed: {e}")
                logger.info("Running in silent mode - visual-only Holly")
            
            # Set up display with proper flags
            display_flags = self.config.get_display_mode()
            if self.config.FULLSCREEN:
                self.screen = pygame.display.set_mode((0, 0), display_flags)
            else:
                self.screen = pygame.display.set_mode(
                    (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), 
                    display_flags
                )
            
            pygame.display.set_caption("Holly - Red Dwarf AI Avatar")
            self.clock = pygame.time.Clock()
            
            # Initialize async event loop and queues
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            self.speech_queue = asyncio.Queue(maxsize=10)
            self.response_queue = asyncio.Queue(maxsize=5)
            self.animation_queue = asyncio.Queue(maxsize=20)
            
            # Initialize components with enhanced configurations
            self.holly_ai = HollyAI()
            self.voice_processor = VoiceProcessor(self.speech_queue)
            self.animation_engine = AnimationEngine(self.screen.get_size())
            self.ui_renderer = UIRenderer(self.screen)
            self.audio_manager = AudioManager(self.response_queue, self.animation_queue)
            
            logger.info("All components initialized successfully")
            
            # Test Holly's initial state
            self._test_holly_initialization()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            return False
    
    def _test_holly_initialization(self):
        """Test Holly's systems with a quick initialization check"""
        try:
            # Test animation system
            from animation_engine import Expression
            self.animation_engine.set_expression(Expression.NEUTRAL, immediate=True)
            
            # Test Holly AI with a simple response
            asyncio.create_task(self._initialize_holly_greeting())
            
            logger.info("Holly systems test passed")
            
        except Exception as e:
            logger.warning(f"Holly systems test failed: {e}")
    
    async def _initialize_holly_greeting(self):
        """Initialize Holly with a greeting"""
        try:
            greeting = await self.holly_ai.get_response("System initialization complete")
            if greeting:
                await self.response_queue.put(greeting)
        except Exception as e:
            logger.error(f"Failed to initialize Holly greeting: {e}")
    
    def start_background_threads(self):
        """Start optimized background threads for real-time performance"""
        try:
            # Start voice processing thread with high priority
            self.voice_thread = threading.Thread(
                target=self._run_voice_processor, 
                daemon=True, 
                name="VoiceProcessor"
            )
            self.voice_thread.start()
            
            # Start AI processing thread
            self.ai_thread = threading.Thread(
                target=self._run_ai_processor, 
                daemon=True, 
                name="AIProcessor"
            )
            self.ai_thread.start()
            
            # Start audio manager thread
            self.audio_thread = threading.Thread(
                target=self._run_audio_manager, 
                daemon=True, 
                name="AudioManager"
            )
            self.audio_thread.start()
            
            logger.info("Background threads started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start background threads: {e}")
    
    def _run_voice_processor(self):
        """Run voice processor in dedicated thread"""
        try:
            self.voice_processor.start_listening()
        except Exception as e:
            logger.error(f"Voice processor error: {e}")
    
    def _run_ai_processor(self):
        """Run AI processor with optimized async loop"""
        try:
            # Create new event loop for this thread
            ai_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(ai_loop)
            
            ai_loop.run_until_complete(self._ai_processing_loop())
        except Exception as e:
            logger.error(f"AI processor error: {e}")
    
    def _run_audio_manager(self):
        """Run audio manager in dedicated thread"""
        try:
            self.audio_manager.start()
        except Exception as e:
            logger.error(f"Audio manager error: {e}")
    
    async def _ai_processing_loop(self):
        """Optimized AI processing loop for minimal latency"""
        logger.info("AI processing loop started")
        
        while self.running:
            try:
                # Process speech input with timeout to prevent blocking
                try:
                    user_input = await asyncio.wait_for(self.speech_queue.get(), timeout=0.1)
                    
                    if user_input:
                        logger.info(f"Processing user input: {user_input}")
                        
                        # Update Holly's state based on input
                        await self._update_holly_state_from_input(user_input)
                        
                        # Get Holly's response with timeout
                        start_time = time.time()
                        holly_response = await asyncio.wait_for(
                            self.holly_ai.get_response(user_input), 
                            timeout=self.config.RESPONSE_TIMEOUT
                        )
                        
                        response_time = time.time() - start_time
                        logger.info(f"Response generated in {response_time:.2f}s")
                        
                        if holly_response:
                            # Queue response for audio output
                            await self.response_queue.put(holly_response)
                            
                            # Update animation based on response
                            await self._update_animation_from_response(holly_response)
                            
                            logger.info(f"Holly response queued: {holly_response[:50]}...")
                
                except asyncio.TimeoutError:
                    # No input received, continue
                    pass
                
                # Handle spontaneous comments (Holly's personality quirk)
                await self._handle_spontaneous_comments()
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in AI processing loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _update_holly_state_from_input(self, user_input: str):
        """Update Holly's emotional state based on user input"""
        try:
            # Analyze input for emotional triggers
            input_lower = user_input.lower()
            
            if any(word in input_lower for word in ['confused', 'what', 'huh', '?']):
                await self.animation_queue.put({'expression': 'confused'})
            elif any(word in input_lower for word in ['funny', 'joke', 'laugh']):
                await self.animation_queue.put({'expression': 'amused'})
            elif any(word in input_lower for word in ['think', 'calculate', 'process']):
                await self.animation_queue.put({'expression': 'thinking'})
            elif any(word in input_lower for word in ['brilliant', 'great', 'good']):
                await self.animation_queue.put({'expression': 'smug'})
            
        except Exception as e:
            logger.error(f"Error updating Holly state: {e}")
    
    async def _update_animation_from_response(self, response: str):
        """Update animation based on Holly's response"""
        try:
            # Analyze response for animation cues
            response_lower = response.lower()
            
            # Check for specific Holly phrases
            if 'brilliant' in response_lower or 'smeg' in response_lower:
                await self.animation_queue.put({'expression': 'smug', 'intensity': 1.2})
            elif any(phrase in response_lower for phrase in ['toasted teacake', 'cup of tea']):
                await self.animation_queue.put({'expression': 'senile'})
            elif '?' in response:
                await self.animation_queue.put({'expression': 'confused'})
            elif any(phrase in response_lower for phrase in ['right,', 'oh,', 'well,']):
                await self.animation_queue.put({'expression': 'thinking'})
            
        except Exception as e:
            logger.error(f"Error updating animation: {e}")
    
    async def _handle_spontaneous_comments(self):
        """Handle Holly's spontaneous comments during idle periods"""
        try:
            current_time = time.time()
            
            if (current_time - self.last_spontaneous_comment) > self.spontaneous_interval:
                # Check if Holly should make a spontaneous comment
                if (not self.audio_manager.is_currently_speaking() and 
                    not self.voice_processor.is_listening() and
                    self.speech_queue.empty()):
                    
                    # Generate spontaneous comment
                    comment = self.holly_ai.trigger_spontaneous_comment()
                    if comment:
                        await self.response_queue.put(comment)
                        await self.animation_queue.put({'expression': 'senile'})
                        logger.info(f"Holly spontaneous comment: {comment[:30]}...")
                    
                    self.last_spontaneous_comment = current_time
        
        except Exception as e:
            logger.error(f"Error handling spontaneous comments: {e}")
    
    def handle_events(self):
        """Handle pygame events with enhanced functionality"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Manual speech trigger
                    self.voice_processor.manual_trigger()
                    logger.info("Manual speech trigger activated")
                elif event.key == pygame.K_t:
                    # Test Holly AI response
                    test_input = "Hello Holly, how are you feeling today?"
                    asyncio.run_coroutine_threadsafe(
                        self.speech_queue.put(test_input),
                        self.loop
                    )
                    logger.info(f"Test AI interaction triggered: {test_input}")
                elif event.key == pygame.K_r:
                    # Reset Holly to neutral state
                    from animation_engine import Expression
                    self.animation_engine.set_expression(Expression.NEUTRAL, immediate=True)
                    logger.info("Holly reset to neutral state")
                elif event.key == pygame.K_d:
                    # Toggle debug mode
                    self.config.DEBUG_MODE = not self.config.DEBUG_MODE
                    logger.info(f"Debug mode: {self.config.DEBUG_MODE}")
    
    def update(self):
        """Update application state with performance optimization"""
        try:
            # Calculate delta time for smooth animations
            current_time = time.time()
            if hasattr(self, '_last_update_time'):
                delta_time = current_time - self._last_update_time
            else:
                delta_time = 1.0 / self.config.FPS
            self._last_update_time = current_time
            
            # Update animation engine
            self.animation_engine.update()
            
            # Process animation commands from queue (non-blocking)
            while True:
                try:
                    anim_data = self.animation_queue.get_nowait()
                    self.animation_engine.process_animation_data(anim_data)
                except:
                    break
            
            # Update performance counters
            self._update_performance_stats()
            
        except Exception as e:
            import traceback
            logger.error(f"Error updating application: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _update_performance_stats(self):
        """Update performance statistics"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
            
            # Log performance warning if FPS is too low
            if self.fps < self.config.FPS * 0.8:
                logger.warning(f"Low FPS detected: {self.fps}")
    
    def render(self):
        """Render the application with enhanced visual quality"""
        try:
            # Clear screen with fade effect for smoother transitions
            fade_surface = pygame.Surface(self.screen.get_size())
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(10)
            self.screen.blit(fade_surface, (0, 0))
            
            # Render UI background
            self.ui_renderer.render_background()
            
            # Render Holly's animated face
            face_state = self.animation_engine.get_face_state()
            self.ui_renderer.render_holly_face(face_state)
            
            # Render UI elements with real-time status
            self.ui_renderer.render_ui_elements(
                voice_active=self.voice_processor.is_listening(),
                ai_thinking=not self.response_queue.empty() or not self.speech_queue.empty()
            )
            
            # Render debug information if enabled
            if self.config.DEBUG_MODE:
                debug_info = self._get_debug_info()
                self.ui_renderer.render_debug_info(debug_info)
            
            # Update display
            pygame.display.flip()
            
        except Exception as e:
            logger.error(f"Error rendering: {e}")
    
    def _get_debug_info(self) -> dict:
        """Get comprehensive debug information"""
        return {
            'FPS': self.fps,
            'Voice Active': self.voice_processor.is_listening(),
            'AI Speaking': self.audio_manager.is_currently_speaking(),
            'Speech Queue': self.speech_queue.qsize(),
            'Response Queue': self.response_queue.qsize(),
            'Animation Queue': self.animation_queue.qsize(),
            'Holly State': self.holly_ai.get_current_state() if self.holly_ai else {},
            'Animation Debug': self.animation_engine.get_debug_info(),
        }
    
    def run(self):
        """Main application loop with enhanced error handling"""
        if not self.initialize():
            logger.error("Failed to initialize application")
            return
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
        logger.info("Starting Holly AI Avatar application...")
        
        # Start background threads
        self.start_background_threads()
        
        # Show startup message
        self._show_startup_message()
        
        # Initial Holly greeting
        try:
            greeting = "Hello there. I'm Holly, the ship's computer. I've got an IQ of 6,000... well, I had. It's probably a bit less now."
            asyncio.run_coroutine_threadsafe(
                self.response_queue.put(greeting),
                self.loop
            )
        except Exception as e:
            logger.error(f"Failed to queue initial greeting: {e}")
        
        # Main game loop with exception handling
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(self.config.FPS)
                
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.cleanup()
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def _show_startup_message(self):
        """Show startup message in console"""
        print("\n" + "="*60)
        print("HOLLY AI AVATAR - RED DWARF SHIP'S COMPUTER")
        print("="*60)
        print("Enhanced Real-Time Version with Authentic Personality")
        print("")
        print("Controls:")
        print("  SPACE    - Manual speech trigger")
        print("  T        - Test Holly response")
        print("  R        - Reset Holly to neutral")
        print("  D        - Toggle debug mode")
        print("  ESC      - Exit application")
        print("="*60)
        print("Holly is online and listening... Start talking!")
        print("(Holly may make spontaneous comments when idle)")
        print("")
    
    def cleanup(self):
        """Enhanced cleanup with proper resource management"""
        logger.info("Cleaning up resources...")
        self.running = False
        
        try:
            # Stop voice processor
            if self.voice_processor:
                self.voice_processor.stop()
            
            # Stop audio manager
            if self.audio_manager:
                self.audio_manager.stop()
            
            # Wait for threads to finish (with timeout)
            threads_to_join = [self.voice_thread, self.ai_thread, self.audio_thread]
            for thread in threads_to_join:
                if thread and thread.is_alive():
                    thread.join(timeout=2.0)
                    if thread.is_alive():
                        logger.warning(f"Thread {thread.name} did not stop gracefully")
            
            # Close event loop
            if self.loop and not self.loop.is_closed():
                self.loop.close()
            
            # Quit pygame
            pygame.quit()
            
            logger.info("Cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def main():
    """Main entry point with error handling"""
    try:
        app = HollyAvatarApp()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
