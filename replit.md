# Holly AI Avatar

## Overview

Holly AI Avatar is a real-time interactive AI system that brings the iconic ship's computer Holly from the BBC series Red Dwarf to life. The application combines advanced AI conversation capabilities with animated facial expressions, voice recognition, and text-to-speech functionality. Built using Python with Pygame for rendering, the system creates an immersive experience where users can have natural conversations with Holly, complete with his characteristic humor, senility, and quirky personality traits.

The application features real-time facial animation with lip-sync, eye tracking, emotional expressions, and a Red Dwarf-themed interface. Holly's personality is implemented using Google's Gemini AI with carefully crafted prompts that capture his dry wit, computer senility, and tendency for practical jokes and non-sequiturs.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Application Structure
The application follows a modular architecture with clear separation of concerns:

- **Main Application Controller** (`main.py`): Central orchestrator managing the event loop and coordinating between all subsystems
- **AI Processing Layer** (`holly_ai.py`, `holly_personality.py`): Handles conversation logic and personality implementation
- **Audio Processing** (`audio_manager.py`, `voice_processor.py`): Manages speech recognition and text-to-speech
- **Visual Rendering** (`ui_renderer.py`, `animation_engine.py`): Handles all visual aspects including facial animation
- **Utility Modules** (`utils/`): Specialized components for facial features, lip-sync, and eye tracking

### AI and Personality System
The AI system is built around Google's Gemini model with a sophisticated personality layer:

- **Personality Engine**: Implements Holly's character traits including his IQ of 6,000, computer senility, humor patterns, and specific quirks like the "blind spot for number 7"
- **Conversation Management**: Maintains context windows and conversation history with mood tracking
- **Response Generation**: Uses system instructions and few-shot examples to ensure authentic Holly-style responses

### Real-time Audio Processing
Audio capabilities are implemented with emphasis on low-latency interaction:

- **Speech Recognition**: Continuous listening with wake word detection using SpeechRecognition library
- **Text-to-Speech**: PyTTSx3 engine configured for Holly's voice characteristics
- **Audio Coordination**: Synchronized audio output with visual lip-sync animations

### Advanced Animation System
The visual system provides realistic facial animations:

- **Facial Animation Engine**: Keyframe-based system supporting multiple expressions and micro-expressions
- **Lip Sync Engine**: Phoneme-based mouth animation synchronized with speech output
- **Eye Tracking System**: Realistic eye movements, gaze tracking, and various blink types
- **Expression Management**: Smooth transitions between emotional states and expressions

### UI and Rendering
Visual presentation uses Pygame with Red Dwarf theming:

- **Real-time Rendering**: 60 FPS display with smooth animations
- **Themed Interface**: Dark space aesthetic with computer grid overlays
- **Responsive Layout**: Scalable interface supporting different screen sizes
- **CSS Styling**: Web-inspired styling system for UI elements

### Configuration Management
Centralized configuration system allows easy customization:

- **Display Settings**: Window size, framerate, and visual quality options
- **Audio Parameters**: Sample rates, voice characteristics, and recognition thresholds
- **Personality Tuning**: Senility levels, humor frequency, and behavioral parameters
- **Performance Options**: Animation smoothness and resource usage controls

## External Dependencies

### AI and Machine Learning
- **Google Gemini AI**: Core conversational AI using the Gemini 2.5 Flash model for natural language processing and response generation
- **NumPy**: Mathematical operations for animation calculations and audio processing

### Audio Processing
- **SpeechRecognition**: Real-time speech-to-text conversion with multiple engine support
- **PyAudio**: Low-level audio input/output for microphone access and audio streaming
- **PyTTSx3**: Text-to-speech synthesis with voice customization capabilities
- **Pygame**: Audio playback and mixing for synchronized speech output

### Graphics and UI
- **Pygame**: Primary graphics rendering engine for real-time visual display and event handling
- **OpenCV (cv2)**: Computer vision utilities for potential face tracking and visual processing

### System Integration
- **Threading/Asyncio**: Concurrent processing for audio, AI, and animation systems
- **Logging**: Comprehensive logging system for debugging and monitoring
- **Pathlib/OS**: File system operations and environment variable management

### Development and Configuration
- **Environment Variables**: Secure API key management for Gemini AI access
- **CSS/HTML Templates**: Web-style templating for UI component styling
- **Configuration Files**: Centralized settings management for all system parameters