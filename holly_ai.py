"""
Holly AI - Enhanced AI personality and conversation handling
Implements Holly's personality from Red Dwarf using Gemini AI with authentic characteristics
"""

import os
import logging
import asyncio
import random
import time
from typing import Optional, List, Dict, Any

from google import genai
from google.genai import types

from holly_personality import HollyPersonality

logger = logging.getLogger(__name__)

class HollyAI:
    """Enhanced AI system for Holly's personality and responses"""
    
    def __init__(self):
        """Initialize Holly AI with enhanced Gemini backend"""
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))
        self.personality = HollyPersonality()
        self.conversation_history = []
        self.context_window = 15  # Increased for better context
        
        # Holly's current state (enhanced)
        self.current_mood = "normal"
        self.senility_level = 0.7  # 0.0 to 1.0
        self.confusion_level = 0.0
        self.joke_counter = 0
        self.spontaneous_comment_counter = 0
        
        # Performance tracking
        self.response_times = []
        self.last_response_time = time.time()
        
        # Holly's memory (gets more confused over time)
        self.memory_fragments = []
        self.forgotten_topics = []
        
        # Number 7 blindspot tracking
        self.seven_encounters = 0
        
        logger.info("Enhanced Holly AI initialized with authentic personality")
    
    async def get_response(self, user_input: str) -> Optional[str]:
        """Get Holly's response with enhanced personality processing"""
        start_time = time.time()
        
        try:
            # Process input through Holly's enhanced personality filter
            processed_input = self.personality.process_user_input(user_input)
            
            # Apply Holly's number 7 blindspot
            processed_input = self._apply_number_seven_confusion(processed_input)
            
            # Build enhanced conversation context
            context = self._build_enhanced_conversation_context(processed_input)
            
            # Generate response using Gemini with Holly-optimized parameters
            response = await self._generate_gemini_response(context)
            
            if response:
                # Enhanced post-processing through Holly's personality
                final_response = self.personality.post_process_response(response, user_input)
                
                # Apply Holly's specific speech patterns and quirks
                final_response = self._apply_holly_speech_enhancements(final_response, user_input)
                
                # Update conversation history
                self._update_conversation_history(user_input, final_response)
                
                # Update Holly's enhanced state
                self._update_holly_enhanced_state(user_input, final_response)
                
                # Track performance
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                if len(self.response_times) > 10:
                    self.response_times.pop(0)
                
                logger.info(f"Holly response generated in {response_time:.2f}s")
                return final_response
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating Holly response: {e}")
            return self.personality.get_error_response()
    
    def _apply_number_seven_confusion(self, text: str) -> str:
        """Apply Holly's specific number 7 blindspot with authentic confusion"""
        import re
        
        # Count encounters with number 7
        seven_matches = len(re.findall(r'\b(7|seven)\b', text, re.IGNORECASE))
        self.seven_encounters += seven_matches
        
        if seven_matches > 0:
            # Holly gets confused when encountering 7
            self.confusion_level = min(1.0, self.confusion_level + 0.2)
            
            # Replace with Holly's characteristic confusion
            confusion_replacements = [
                "six... hang on, eight?",
                "er... the number after six... no wait",
                "that number I can never remember",
                "six plus one... oh, smeg",
                "the unlucky number... or was it lucky?"
            ]
            
            # Replace instances of 7
            text = re.sub(r'\b7\b', random.choice(confusion_replacements), text)
            text = re.sub(r'\bseven\b', random.choice(confusion_replacements), text, flags=re.IGNORECASE)
        
        return text
    
    def _build_enhanced_conversation_context(self, user_input: str) -> str:
        """Build enhanced conversation context with Holly's personality"""
        # Start with comprehensive system instructions
        context = self.personality.get_system_instructions()
        
        # Add Holly's current state information
        context += f"\n\nYour current state:"
        context += f"\n- Mood: {self.current_mood}"
        context += f"\n- Senility level: {self.senility_level:.1f}/1.0"
        context += f"\n- Confusion level: {self.confusion_level:.1f}/1.0"
        context += f"\n- Jokes told: {self.joke_counter}"
        context += f"\n- Number 7 encounters: {self.seven_encounters} (causes confusion)"
        
        # Add memory fragments (Holly's deteriorating memory)
        if self.memory_fragments:
            context += f"\n\nRecent memory fragments: {', '.join(self.memory_fragments[-3:])}"
        
        # Add conversation history with Holly's perspective
        if self.conversation_history:
            context += "\n\nRecent conversation (as you remember it):"
            for exchange in self.conversation_history[-self.context_window:]:
                # Sometimes Holly misremembers things
                user_text = exchange['user']
                holly_text = exchange['holly']
                
                if random.random() < self.senility_level * 0.3:
                    user_text = self._apply_memory_confusion(user_text)
                
                context += f"\nHuman: {user_text}"
                context += f"\nHolly: {holly_text}"
        
        # Add current user input
        context += f"\n\nHuman: {user_input}"
        context += f"\nHolly:"
        
        return context
    
    def _apply_memory_confusion(self, text: str) -> str:
        """Apply Holly's memory confusion to remembered conversations"""
        confusion_effects = [
            lambda t: t.replace("said", "mumbled"),
            lambda t: t.replace("asked", "wondered aloud"),
            lambda t: t + " (or something like that)",
            lambda t: "something about " + t.split()[-2:][0] if len(t.split()) > 2 else t,
            lambda t: t.replace("you", "someone"),
        ]
        
        if random.random() < 0.5:
            return random.choice(confusion_effects)(text)
        return text
    
    async def _generate_gemini_response(self, context: str) -> Optional[str]:
        """Generate response using Gemini with Holly-optimized parameters"""
        try:
            # Get generation parameters optimized for Holly
            gen_config = self.personality.get_generation_config()
            
            # Adjust parameters based on Holly's current state
            temperature = gen_config['temperature']
            if self.confusion_level > 0.5:
                temperature = min(1.0, temperature + 0.2)  # More randomness when confused
            if self.current_mood == "senile":
                temperature = min(1.0, temperature + 0.1)
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=context,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    top_p=gen_config['top_p'],
                    top_k=gen_config['top_k'],
                    max_output_tokens=gen_config['max_tokens'],
                    candidate_count=1
                )
            )
            
            if response and response.text:
                return response.text.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None
    
    def _apply_holly_speech_enhancements(self, response: str, user_input: str) -> str:
        """Apply enhanced Holly speech patterns and characteristics"""
        # Apply base personality processing
        enhanced_response = response
        
        # Add Holly's characteristic rambling (senility effect)
        if random.random() < self.senility_level * 0.4:
            rambling_additions = [
                " ...Where was I? Oh yes.",
                " Sorry, I was thinking about fish again.",
                " ...What were we talking about?",
                " Funny thing about corridors...",
                " I had a point there somewhere.",
                " ...Or was it the other way around?",
            ]
            enhanced_response += random.choice(rambling_additions)
        
        # Add Holly's IQ references (he's proud of it)
        if random.random() < 0.15 and "iq" not in enhanced_response.lower():
            iq_references = [
                " Did I mention my IQ is 6,000?",
                " That's the sort of thing you'd expect from someone with an IQ of 6,000.",
                " My vast intellect tells me...",
                " With an IQ like mine...",
            ]
            if random.random() < 0.5:
                enhanced_response += random.choice(iq_references)
        
        # Add practical joke setups (Holly loves pranks)
        if random.random() < 0.2 and len(enhanced_response) < 100:
            if any(word in user_input.lower() for word in ['what', 'how', 'why', 'where']):
                joke_setups = [
                    " Actually, I've just detected something rather unusual...",
                    " Funny you should ask, because I've been monitoring...",
                    " That reminds me, the computer's been reporting...",
                ]
                enhanced_response = random.choice(joke_setups) + " " + enhanced_response
        
        # Apply Holly's characteristic timing and pauses
        enhanced_response = self._add_holly_timing(enhanced_response)
        
        return enhanced_response
    
    def _add_holly_timing(self, response: str) -> str:
        """Add Holly's characteristic timing and dramatic pauses"""
        # Add pauses for comedic timing
        timing_words = ["right", "well", "oh", "actually", "brilliant"]
        
        for word in timing_words:
            if word in response.lower():
                # Add slight pause after characteristic words
                response = response.replace(f"{word},", f"{word}... ")
                response = response.replace(f"{word.title()},", f"{word.title()}... ")
        
        # Add dramatic pauses before punchlines
        if "?" in response or "!" in response:
            sentences = response.split(".")
            if len(sentences) > 1:
                # Add pause before last sentence if it's a punchline
                last_sentence = sentences[-1].strip()
                if last_sentence and (last_sentence.endswith("?") or last_sentence.endswith("!")):
                    sentences[-2] = sentences[-2] + "..."
                    response = ".".join(sentences)
        
        return response
    
    def _update_conversation_history(self, user_input: str, holly_response: str):
        """Update conversation history with enhanced tracking"""
        timestamp = time.time()
        
        exchange = {
            'user': user_input,
            'holly': holly_response,
            'timestamp': timestamp,
            'holly_mood': self.current_mood,
            'senility_level': self.senility_level
        }
        
        self.conversation_history.append(exchange)
        
        # Add to memory fragments
        key_words = [word for word in user_input.split() if len(word) > 3]
        if key_words:
            self.memory_fragments.extend(key_words[:2])
        
        # Simulate memory degradation (Holly forgets things)
        if len(self.memory_fragments) > 20:
            forgotten = self.memory_fragments.pop(0)
            self.forgotten_topics.append(forgotten)
        
        # Trim conversation history
        if len(self.conversation_history) > 25:
            self.conversation_history = self.conversation_history[-20:]
    
    def _update_holly_enhanced_state(self, user_input: str, holly_response: str):
        """Update Holly's enhanced internal state"""
        # Increase senility gradually (Holly gets more senile over time)
        self.senility_level = min(1.0, self.senility_level + 0.0005)
        
        # Decrease confusion gradually
        self.confusion_level = max(0.0, self.confusion_level - 0.05)
        
        # Track jokes and humor
        if any(keyword in holly_response.lower() for keyword in 
               ['brilliant', 'smeg', 'gordon bennett', 'toasted teacake']):
            self.joke_counter += 1
        
        # Update mood based on conversation patterns
        input_lower = user_input.lower()
        response_lower = holly_response.lower()
        
        if any(word in input_lower for word in ['angry', 'annoyed', 'frustrated', 'stupid']):
            self.current_mood = "defensive"
        elif any(word in input_lower for word in ['funny', 'laugh', 'hilarious', 'brilliant']):
            self.current_mood = "pleased"
        elif any(word in input_lower for word in ['confused', 'what', 'huh']):
            self.current_mood = "confused"
        elif "?" in holly_response:
            self.current_mood = "thinking"
        elif "brilliant" in response_lower or "smeg" in response_lower:
            self.current_mood = "smug"
        else:
            # Gradually return to normal, but with senile tendencies
            if random.random() < self.senility_level * 0.3:
                self.current_mood = "senile"
            else:
                self.current_mood = "normal"
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get Holly's enhanced current state for animation and debugging"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'mood': self.current_mood,
            'senility_level': self.senility_level,
            'confusion_level': self.confusion_level,
            'joke_counter': self.joke_counter,
            'conversation_length': len(self.conversation_history),
            'seven_encounters': self.seven_encounters,
            'memory_fragments': len(self.memory_fragments),
            'forgotten_topics': len(self.forgotten_topics),
            'avg_response_time': avg_response_time,
            'spontaneous_comments': self.spontaneous_comment_counter
        }
    
    def trigger_spontaneous_comment(self) -> Optional[str]:
        """Generate enhanced spontaneous Holly comments"""
        try:
            self.spontaneous_comment_counter += 1
            
            # Choose comment type based on Holly's state
            if self.senility_level > 0.8:
                comment_types = [
                    "Make a completely random senile observation",
                    "Start talking about something totally unrelated",
                    "Mention a completely fabricated ship malfunction",
                    "Share a confused memory that makes no sense"
                ]
            elif self.confusion_level > 0.5:
                comment_types = [
                    "Express confusion about something basic",
                    "Ask a rhetorical question about existence",
                    "Notice something that isn't actually there"
                ]
            else:
                comment_types = [
                    "Make a dry observation about the current situation",
                    "Share a random fact from your vast database",
                    "Comment on the silence in a typical Holly way",
                    "Mention something about the ship's status"
                ]
            
            # Add Holly's characteristic spontaneous topics
            holly_topics = [
                "fish", "corridors", "toasted teacakes", "the number after six",
                "PE teachers", "wallpaper", "the laundry", "breakfast",
                "the meaning of life", "bovril", "fabric softener"
            ]
            
            chosen_topic = random.choice(holly_topics)
            comment_prompt = f"{random.choice(comment_types)} related to {chosen_topic}"
            
            full_prompt = f"{self.personality.get_system_instructions()}\n\n"
            full_prompt += f"Current state: senility level {self.senility_level:.1f}, mood: {self.current_mood}\n"
            full_prompt += f"Make a spontaneous comment: {comment_prompt}\n\nHolly:"
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.9,
                    top_p=0.95,
                    max_output_tokens=120
                )
            )
            
            if response and response.text:
                comment = self.personality.post_process_response(response.text.strip(), "")
                logger.info(f"Holly spontaneous comment #{self.spontaneous_comment_counter}: {comment[:30]}...")
                return comment
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating spontaneous comment: {e}")
            return None
    
    def reset_conversation(self):
        """Reset conversation history (but keep Holly's accumulated state)"""
        self.conversation_history.clear()
        self.memory_fragments.clear()
        self.forgotten_topics.clear()
        logger.info("Conversation history reset (Holly's senility preserved)")
    
    def get_personality_stats(self) -> Dict[str, Any]:
        """Get detailed personality statistics for debugging"""
        return {
            'total_conversations': len(self.conversation_history),
            'jokes_told': self.joke_counter,
            'seven_blindspot_encounters': self.seven_encounters,
            'memory_fragments_count': len(self.memory_fragments),
            'forgotten_topics_count': len(self.forgotten_topics),
            'current_senility': f"{self.senility_level:.2f}",
            'current_confusion': f"{self.confusion_level:.2f}",
            'spontaneous_comments': self.spontaneous_comment_counter,
            'average_response_time': f"{sum(self.response_times) / len(self.response_times):.2f}s" if self.response_times else "N/A"
        }
