"""
UI Renderer - Handles all visual rendering including Holly's face and UI elements
Red Dwarf themed interface with animated Holly head
"""

import math
import pygame
import logging
from typing import Tuple, Dict, Any, Optional
from pathlib import Path
import os

from animation_engine import FaceState, Expression

logger = logging.getLogger(__name__)

class UIRenderer:
    """Renders Holly's face and Red Dwarf themed UI"""
    
    def __init__(self, screen: pygame.Surface):
        """Initialize UI renderer"""
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        
        # Colors (Red Dwarf theme)
        self.colors = {
            'background': (10, 15, 30),       # Dark space blue
            'panel_dark': (40, 45, 60),       # Dark panel
            'panel_light': (60, 70, 90),      # Light panel
            'text_primary': (200, 220, 255),  # Light blue text
            'text_secondary': (150, 170, 200), # Dimmer text
            'accent_red': (200, 60, 60),      # Red Dwarf red
            'accent_green': (60, 200, 80),    # Status green
            'accent_yellow': (220, 200, 60),  # Warning yellow
            'holly_face': (220, 200, 180),    # Holly's skin tone
            'holly_outline': (100, 80, 60),   # Face outline
        }
        
        # Fonts
        self.fonts = {}
        self._initialize_fonts()
        
        # Holly face parameters
        self.holly_center = (self.screen_width // 2, self.screen_height // 2)
        self.holly_scale = min(self.screen_width, self.screen_height) // 4
        
        # UI elements
        self.status_bars = {}
        self.interface_panels = []
        
        # Holly image support
        self.holly_image = None
        self.holly_original = None
        self._load_holly_image()
        
        logger.info("UI renderer initialized")
    
    def _initialize_fonts(self):
        """Initialize fonts for UI"""
        try:
            # Try to load custom fonts, fall back to system fonts
            font_sizes = [12, 16, 24, 32, 48]
            
            for size in font_sizes:
                try:
                    # Try to use a monospace font for computer feel
                    self.fonts[size] = pygame.font.Font(None, size)
                except:
                    self.fonts[size] = pygame.font.SysFont('monospace', size)
            
            logger.info("Fonts initialized")
            
        except Exception as e:
            logger.error(f"Error initializing fonts: {e}")
            # Create minimal fallback fonts
            for size in [16, 24, 32]:
                self.fonts[size] = pygame.font.Font(None, size)
    
    def _load_holly_image(self):
        """Load Holly's face image if available"""
        try:
            # Try to load holly.png first, then fall back to other formats
            image_paths = [
                'holly.png',
                'assets/holly.png', 
                'assets/holly_face.png',
                'holly.jpg',
                'assets/holly.jpg'
            ]
            
            for path in image_paths:
                if os.path.exists(path):
                    try:
                        self.holly_original = pygame.image.load(path).convert_alpha()
                        # Scale to appropriate size
                        target_size = (self.holly_scale * 2, self.holly_scale * 2)
                        self.holly_image = pygame.transform.scale(self.holly_original, target_size)
                        logger.info(f"Loaded Holly image: {path}")
                        return
                    except Exception as e:
                        logger.warning(f"Failed to load {path}: {e}")
                        continue
            
            logger.info("No Holly image found, using procedural face rendering")
            
        except Exception as e:
            logger.error(f"Error loading Holly image: {e}")
            self.holly_image = None
    
    def render_background(self):
        """Render Red Dwarf themed background"""
        # Fill with dark space background
        self.screen.fill(self.colors['background'])
        
        # Draw subtle grid pattern (like computer displays)
        self._draw_grid_pattern()
        
        # Draw corner panels
        self._draw_corner_panels()
        
        # Draw status elements
        self._draw_status_elements()
    
    def _draw_grid_pattern(self):
        """Draw subtle grid pattern for computer interface feel"""
        grid_spacing = 40
        grid_color = (20, 25, 40)
        
        # Vertical lines
        for x in range(0, self.screen_width, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.screen_height), 1)
        
        # Horizontal lines
        for y in range(0, self.screen_height, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.screen_width, y), 1)
    
    def _draw_corner_panels(self):
        """Draw corner control panels"""
        panel_size = 120
        panel_margin = 20
        
        # Top-left panel
        panel_rect = pygame.Rect(panel_margin, panel_margin, panel_size, panel_size)
        pygame.draw.rect(self.screen, self.colors['panel_dark'], panel_rect)
        pygame.draw.rect(self.screen, self.colors['panel_light'], panel_rect, 2)
        
        # Add "RED DWARF" text
        if 16 in self.fonts:
            text = self.fonts[16].render("RED DWARF", True, self.colors['text_primary'])
            text_rect = text.get_rect(center=(panel_rect.centerx, panel_rect.centery - 20))
            self.screen.blit(text, text_rect)
            
            # Add system status
            status_text = self.fonts[12].render("SYSTEM ONLINE", True, self.colors['accent_green'])
            status_rect = status_text.get_rect(center=(panel_rect.centerx, panel_rect.centery + 20))
            self.screen.blit(status_text, status_rect)
        
        # Top-right panel (Holly info)
        panel_rect = pygame.Rect(self.screen_width - panel_size - panel_margin, 
                               panel_margin, panel_size, panel_size)
        pygame.draw.rect(self.screen, self.colors['panel_dark'], panel_rect)
        pygame.draw.rect(self.screen, self.colors['panel_light'], panel_rect, 2)
        
        if 16 in self.fonts:
            text = self.fonts[16].render("HOLLY", True, self.colors['text_primary'])
            text_rect = text.get_rect(center=(panel_rect.centerx, panel_rect.centery - 20))
            self.screen.blit(text, text_rect)
            
            iq_text = self.fonts[12].render("IQ: 6000", True, self.colors['accent_yellow'])
            iq_rect = iq_text.get_rect(center=(panel_rect.centerx, panel_rect.centery + 20))
            self.screen.blit(iq_text, iq_rect)
    
    def _draw_status_elements(self):
        """Draw system status elements"""
        # Bottom status bar
        status_height = 40
        status_rect = pygame.Rect(0, self.screen_height - status_height, 
                                self.screen_width, status_height)
        pygame.draw.rect(self.screen, self.colors['panel_dark'], status_rect)
        
        # Status text
        if 16 in self.fonts:
            status_text = "JUPITER MINING CORPORATION - SHIP'S COMPUTER INTERFACE"
            text_surface = self.fonts[16].render(status_text, True, self.colors['text_secondary'])
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, 
                                                    self.screen_height - status_height // 2))
            self.screen.blit(text_surface, text_rect)
    
    def render_holly_face(self, face_state: FaceState):
        """Render Holly's animated face with image support"""
        # Calculate face position with floating animation
        float_x, float_y = face_state.head_position
        face_x = int(self.holly_center[0] + float_x * 50)
        face_y = int(self.holly_center[1] + float_y * 30)
        
        if self.holly_image:
            # Use image-based rendering with animation
            self._render_image_based_face(face_x, face_y, face_state)
        else:
            # Use procedural face rendering
            self._render_procedural_face(face_x, face_y, face_state)
    
    def _render_image_based_face(self, face_x: int, face_y: int, face_state: FaceState):
        """Render Holly's face using image with animated overlay"""
        # Create a copy of the image for animation modifications
        animated_image = self.holly_image.copy()
        
        # Apply facial animation transformations
        if face_state.mouth_open > 0.1:
            # Stretch mouth area for speaking
            self._animate_mouth_on_image(animated_image, face_state)
        
        # Apply blinking by darkening eye areas
        if face_state.left_blink < 0.5 or face_state.right_blink < 0.5:
            self._animate_blink_on_image(animated_image, face_state)
        
        # Calculate image position (centered)
        img_rect = animated_image.get_rect()
        img_rect.center = (face_x, face_y)
        
        # Draw the animated Holly image
        self.screen.blit(animated_image, img_rect)
        
        # Add computer interface overlay
        self._draw_interface_overlay(face_x, face_y)
    
    def _render_procedural_face(self, face_x: int, face_y: int, face_state: FaceState):
        """Render Holly's face using procedural drawing"""
        # Draw face outline (head shape)
        head_radius = self.holly_scale
        pygame.draw.circle(self.screen, self.colors['holly_outline'], 
                         (face_x, face_y), head_radius + 3, 3)
        pygame.draw.circle(self.screen, self.colors['holly_face'], 
                         (face_x, face_y), head_radius)
        
        # Draw eyes
        self._draw_eyes(face_x, face_y, face_state)
        
        # Draw mouth
        self._draw_mouth(face_x, face_y, face_state)
        
        # Draw eyebrows
        self._draw_eyebrows(face_x, face_y, face_state)
        
        # Add expression-specific features
        self._draw_expression_features(face_x, face_y, face_state)
        
        # Add computer interface overlay
        self._draw_interface_overlay(face_x, face_y)
    
    def _draw_eyes(self, face_x: int, face_y: int, face_state: FaceState):
        """Draw Holly's eyes with blinking and movement"""
        eye_offset_x = self.holly_scale // 3
        eye_offset_y = self.holly_scale // 6
        eye_radius = self.holly_scale // 8
        
        # Eye positions with gaze direction
        gaze_x, gaze_y = face_state.eye_position
        left_eye_x = face_x - eye_offset_x + int(gaze_x * 10)
        left_eye_y = face_y - eye_offset_y + int(gaze_y * 8)
        right_eye_x = face_x + eye_offset_x + int(gaze_x * 10)
        right_eye_y = face_y - eye_offset_y + int(gaze_y * 8)
        
        # Draw eye sockets
        socket_radius = eye_radius + 4
        pygame.draw.circle(self.screen, self.colors['holly_outline'], 
                         (left_eye_x, left_eye_y), socket_radius)
        pygame.draw.circle(self.screen, self.colors['holly_outline'], 
                         (right_eye_x, right_eye_y), socket_radius)
        
        # Draw eyes based on blink state
        if face_state.left_blink > 0.1 and face_state.right_blink > 0.1:  # Eyes open
            # White of eyes
            pygame.draw.circle(self.screen, (255, 255, 255), 
                             (left_eye_x, left_eye_y), eye_radius)
            pygame.draw.circle(self.screen, (255, 255, 255), 
                             (right_eye_x, right_eye_y), eye_radius)
            
            # Pupils
            pupil_radius = eye_radius // 2
            pygame.draw.circle(self.screen, (20, 20, 20), 
                             (left_eye_x, left_eye_y), pupil_radius)
            pygame.draw.circle(self.screen, (20, 20, 20), 
                             (right_eye_x, right_eye_y), pupil_radius)
        else:  # Eyes closed (blinking)
            # Draw closed eyes as lines
            pygame.draw.line(self.screen, self.colors['holly_outline'],
                           (left_eye_x - eye_radius, left_eye_y),
                           (left_eye_x + eye_radius, left_eye_y), 3)
            pygame.draw.line(self.screen, self.colors['holly_outline'],
                           (right_eye_x - eye_radius, right_eye_y),
                           (right_eye_x + eye_radius, right_eye_y), 3)
    
    def _draw_mouth(self, face_x: int, face_y: int, face_state: FaceState):
        """Draw Holly's mouth with lip-sync animation"""
        mouth_y = face_y + self.holly_scale // 3
        mouth_width = self.holly_scale // 3
        mouth_height = int(self.holly_scale // 6 * face_state.mouth_open)
        
        if face_state.mouth_open > 0.1:
            # Mouth open (speaking)
            mouth_rect = pygame.Rect(face_x - mouth_width // 2, 
                                   mouth_y - mouth_height // 2,
                                   mouth_width, mouth_height)
            pygame.draw.ellipse(self.screen, (40, 20, 20), mouth_rect)
            pygame.draw.ellipse(self.screen, self.colors['holly_outline'], mouth_rect, 2)
        else:
            # Mouth closed
            pygame.draw.line(self.screen, self.colors['holly_outline'],
                           (face_x - mouth_width // 2, mouth_y),
                           (face_x + mouth_width // 2, mouth_y), 3)
    
    def _draw_eyebrows(self, face_x: int, face_y: int, face_state: FaceState):
        """Draw eyebrows with expression"""
        brow_y = face_y - self.holly_scale // 4
        brow_offset_x = self.holly_scale // 3
        brow_width = self.holly_scale // 6
        
        # Eyebrow raise based on expression
        left_raise_offset = int(face_state.eyebrow_left * 10)
        right_raise_offset = int(face_state.eyebrow_right * 10)
        
        # Left eyebrow
        left_brow_start = (face_x - brow_offset_x - brow_width // 2, brow_y - left_raise_offset)
        left_brow_end = (face_x - brow_offset_x + brow_width // 2, brow_y - left_raise_offset)
        pygame.draw.line(self.screen, self.colors['holly_outline'], 
                       left_brow_start, left_brow_end, 4)
        
        # Right eyebrow
        right_brow_start = (face_x + brow_offset_x - brow_width // 2, brow_y - right_raise_offset)
        right_brow_end = (face_x + brow_offset_x + brow_width // 2, brow_y - right_raise_offset)
        pygame.draw.line(self.screen, self.colors['holly_outline'], 
                       right_brow_start, right_brow_end, 4)
    
    def _draw_expression_features(self, face_x: int, face_y: int, face_state: FaceState):
        """Draw additional features based on expression"""
        intensity = face_state.emotion_intensity
        
        if face_state.expression == Expression.THINKING:
            # Draw thought lines near head
            for i in range(3):
                angle = math.pi / 4 + i * 0.2
                line_x = face_x + int(math.cos(angle) * (self.holly_scale + 20))
                line_y = face_y + int(math.sin(angle) * (self.holly_scale + 20))
                pygame.draw.circle(self.screen, self.colors['text_secondary'], 
                                 (line_x, line_y), int(3 * intensity))
        
        elif face_state.expression == Expression.AMUSED:
            # Draw slight smile lines
            smile_y = face_y + self.holly_scale // 4
            smile_offset = int(20 * intensity)
            pygame.draw.arc(self.screen, self.colors['holly_outline'],
                          (face_x - smile_offset, smile_y - 10, 
                           smile_offset * 2, 20), 0, math.pi, 2)
        
        elif face_state.expression == Expression.CONFUSED:
            # Draw question mark above head
            if intensity > 0.5:
                question_x = face_x + self.holly_scale // 2
                question_y = face_y - self.holly_scale - 20
                if 24 in self.fonts:
                    question_text = self.fonts[24].render("?", True, self.colors['accent_yellow'])
                    self.screen.blit(question_text, (question_x, question_y))
    
    def render_ui_elements(self, voice_active: bool = False, ai_thinking: bool = False):
        """Render UI status elements"""
        # Voice activity indicator
        if voice_active:
            indicator_radius = 15
            indicator_x = 50
            indicator_y = self.screen_height - 60
            
            # Pulsing red circle for voice activity
            pulse = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
            color = (pulse, 50, 50)
            pygame.draw.circle(self.screen, color, (indicator_x, indicator_y), indicator_radius)
            
            if 16 in self.fonts:
                voice_text = self.fonts[16].render("LISTENING", True, self.colors['accent_red'])
                self.screen.blit(voice_text, (indicator_x + 25, indicator_y - 8))
        
        # AI thinking indicator
        if ai_thinking:
            thinking_x = self.screen_width - 150
            thinking_y = self.screen_height - 60
            
            # Animated thinking dots
            dots = "." * (1 + (pygame.time.get_ticks() // 500) % 3)
            
            if 16 in self.fonts:
                thinking_text = self.fonts[16].render(f"PROCESSING{dots}", True, self.colors['accent_yellow'])
                self.screen.blit(thinking_text, (thinking_x, thinking_y))
        
        # Instructions panel (top center)
        self._draw_instructions_panel()
    
    def _draw_instructions_panel(self):
        """Draw instructions panel"""
        panel_width = 400
        panel_height = 80
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = 20
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, self.colors['panel_dark'], panel_rect)
        pygame.draw.rect(self.screen, self.colors['panel_light'], panel_rect, 2)
        
        if 16 in self.fonts:
            instructions = [
                "SPACE - Manual Speech Trigger",
                "T - Test Response  |  ESC - Exit"
            ]
            
            for i, instruction in enumerate(instructions):
                text = self.fonts[12].render(instruction, True, self.colors['text_secondary'])
                text_rect = text.get_rect(center=(panel_rect.centerx, 
                                                panel_rect.centery - 15 + i * 20))
                self.screen.blit(text, text_rect)
    
    def render_debug_info(self, debug_info: Dict[str, Any]):
        """Render debug information"""
        if not debug_info:
            return
        
        debug_y = 150
        debug_x = 20
        
        if 16 in self.fonts:
            for key, value in debug_info.items():
                debug_text = f"{key}: {value}"
                text_surface = self.fonts[12].render(debug_text, True, self.colors['text_secondary'])
                self.screen.blit(text_surface, (debug_x, debug_y))
                debug_y += 20
    
    def _animate_mouth_on_image(self, image: pygame.Surface, face_state: FaceState):
        """Apply mouth animation to Holly's image"""
        # Get image dimensions
        width, height = image.get_size()
        
        # Estimate mouth area (roughly bottom third, center)
        mouth_area = pygame.Rect(
            width // 3, height * 2 // 3,
            width // 3, height // 6
        )
        
        # Create a stretched version for mouth opening
        if face_state.mouth_open > 0.2:
            # Stretch the mouth area vertically
            stretch_factor = 1.0 + (face_state.mouth_open * 0.5)
            mouth_section = image.subsurface(mouth_area)
            stretched_mouth = pygame.transform.scale(
                mouth_section, 
                (mouth_area.width, int(mouth_area.height * stretch_factor))
            )
            
            # Blit the stretched mouth back
            y_offset = int((stretched_mouth.get_height() - mouth_area.height) / 2)
            image.blit(stretched_mouth, (mouth_area.x, mouth_area.y - y_offset))
    
    def _animate_blink_on_image(self, image: pygame.Surface, face_state: FaceState):
        """Apply blink animation to Holly's image"""
        width, height = image.get_size()
        
        # Estimate eye areas (roughly upper third)
        left_eye_area = pygame.Rect(width // 4, height // 4, width // 8, height // 12)
        right_eye_area = pygame.Rect(width * 5 // 8, height // 4, width // 8, height // 12)
        
        # Darken eye areas when blinking
        blink_overlay = pygame.Surface((width // 8, height // 12))
        blink_overlay.fill((0, 0, 0))
        
        if face_state.left_blink < 0.5:
            alpha = int(255 * (1.0 - face_state.left_blink * 2))
            blink_overlay.set_alpha(alpha)
            image.blit(blink_overlay, left_eye_area)
        
        if face_state.right_blink < 0.5:
            alpha = int(255 * (1.0 - face_state.right_blink * 2))
            blink_overlay.set_alpha(alpha)
            image.blit(blink_overlay, right_eye_area)
    
    def _draw_interface_overlay(self, face_x: int, face_y: int):
        """Draw Red Dwarf computer interface elements around Holly"""
        # Corner brackets around Holly
        bracket_size = 30
        bracket_offset = self.holly_scale + 40
        
        # Top-left bracket
        tl_x, tl_y = face_x - bracket_offset, face_y - bracket_offset
        pygame.draw.lines(self.screen, self.colors['accent_red'], False, [
            (tl_x, tl_y + bracket_size), (tl_x, tl_y), (tl_x + bracket_size, tl_y)
        ], 3)
        
        # Top-right bracket
        tr_x, tr_y = face_x + bracket_offset, face_y - bracket_offset
        pygame.draw.lines(self.screen, self.colors['accent_red'], False, [
            (tr_x - bracket_size, tr_y), (tr_x, tr_y), (tr_x, tr_y + bracket_size)
        ], 3)
        
        # Bottom-left bracket
        bl_x, bl_y = face_x - bracket_offset, face_y + bracket_offset
        pygame.draw.lines(self.screen, self.colors['accent_red'], False, [
            (bl_x, bl_y - bracket_size), (bl_x, bl_y), (bl_x + bracket_size, bl_y)
        ], 3)
        
        # Bottom-right bracket
        br_x, br_y = face_x + bracket_offset, face_y + bracket_offset
        pygame.draw.lines(self.screen, self.colors['accent_red'], False, [
            (br_x - bracket_size, br_y), (br_x, br_y), (br_x, br_y - bracket_size)
        ], 3)
        
        # Status indicators
        pygame.draw.circle(self.screen, self.colors['accent_green'], 
                         (face_x - bracket_offset - 20, face_y), 5)
        pygame.draw.circle(self.screen, self.colors['accent_yellow'], 
                         (face_x + bracket_offset + 20, face_y), 5)
        
        # Scan lines effect
        for i in range(0, self.screen_height, 4):
            pygame.draw.line(self.screen, (0, 20, 40), 
                           (0, i), (self.screen_width, i), 1)
