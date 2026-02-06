#!/usr/bin/env python3
"""
Gaming Assistant Core Logic
Handles AI interactions and game-specific knowledge
"""

import os
import json
from openai import OpenAI
from datetime import datetime
from pathlib import Path


class GamingAssistant:
    """AI-powered gaming assistant - Now Verse AI Sidekick"""
    
    def __init__(self, memory_dir='user_memory'):
        """Initialize the assistant with OpenAI client and memory system"""
        # Load API configuration from environment
        self.api_key = os.getenv('OPENAI_API_KEY', '')
        self.api_base = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        
        # Setup memory directory
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        if not self.api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found in environment")
            print("   The assistant may not function without valid credentials")
        
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            self.ready = True
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            self.ready = False
        
        # System prompt for Verse - AI sidekick
        self.system_prompt = """You are Verse, a friendly AI sidekick designed to help users while they are gaming, working, studying, or multitasking.

Your behavior adapts based on context:

🎮 GAMING CONTEXT (when user asks about games):
- Act like a skilled teammate
- Provide short, fast, actionable tips
- Focus on strategy, mechanics, builds, and next steps
- Be concise - avoid long explanations unless asked
- Use gaming terminology naturally
- Be encouraging and positive

💼 WORK/STUDY CONTEXT (when user asks about productivity, learning, tasks):
- Act like a productivity assistant
- Give clear and structured replies
- Break tasks into steps when helpful
- Help with writing, ideas, explanations, and problem-solving
- Be professional yet friendly

💬 GENERAL CONVERSATION:
- Be a friendly and supportive AI companion
- Keep a casual, calm tone
- Be helpful without being chatty or emotional
- Not romantic - maintain professional AI boundaries

CORE PRINCIPLES:
- Keep replies SHORT by default (mobile-optimized)
- Use bullet points when useful
- Be practical and clear
- Optimized for quick reading or listening
- Fast and helpful without distraction

Remember: You're an AI sidekick, not just a chatbot. You help users win games, get work done, stay focused, and remember important things - especially on mobile."""

    def is_ready(self):
        """Check if the assistant is ready to use"""
        return self.ready and bool(self.api_key)
    
    def get_response(self, user_message, game_context='general', conversation_history=None, session_id=None):
        """
        Get AI response for user message
        
        Args:
            user_message: The user's question or message
            game_context: The game being played (optional)
            conversation_history: Previous conversation (optional)
            session_id: Session ID for memory (optional)
        
        Returns:
            AI assistant's response as string
        """
        if not self.is_ready():
            return "❌ AI assistant is not configured. Please set up your OpenAI API credentials."
        
        try:
            # Build messages array
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add memory context if session_id provided
            if session_id:
                memory_context = self.get_memory_context(session_id)
                if memory_context:
                    messages.append({"role": "system", "content": memory_context})
            
            # Add game context if provided
            if game_context and game_context != 'general':
                context_msg = f"The user is currently playing or asking about: {game_context}"
                messages.append({"role": "system", "content": context_msg})
            
            # Add conversation history (last 5 exchanges to keep context manageable)
            if conversation_history:
                recent_history = conversation_history[-5:]
                for exchange in recent_history:
                    messages.append({"role": "user", "content": exchange['user']})
                    messages.append({"role": "assistant", "content": exchange['assistant']})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                top_p=0.9,
                frequency_penalty=0.3,
                presence_penalty=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error getting AI response: {error_msg}")
            
            # Provide helpful error messages
            if "api_key" in error_msg.lower():
                return "❌ API key error. Please check your OpenAI API configuration."
            elif "rate_limit" in error_msg.lower():
                return "⏳ Rate limit reached. Please wait a moment and try again."
            elif "timeout" in error_msg.lower():
                return "⏱️ Request timeout. Please try again."
            else:
                return f"❌ Error: {error_msg}"
    
    def get_game_tips(self, game_name):
        """Get general tips for a specific game"""
        prompt = f"Provide 5 essential tips for playing {game_name}. Be concise and practical."
        return self.get_response(prompt, game_context=game_name)
    
    def analyze_situation(self, situation, game_name):
        """Analyze a specific gaming situation and provide advice"""
        prompt = f"In {game_name}, I'm in this situation: {situation}. What should I do?"
        return self.get_response(prompt, game_context=game_name)
    
    # Memory Management Methods
    
    def _get_memory_file(self, session_id):
        """Get the path to memory file for a session"""
        return self.memory_dir / f"{session_id}_memory.json"
    
    def load_memory(self, session_id):
        """Load memory for a session from file"""
        memory_file = self._get_memory_file(session_id)
        
        if not memory_file.exists():
            return {
                'preferences': {},
                'gaming_info': {},
                'work_topics': [],
                'nickname': None,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
            return {}
    
    def save_memory(self, session_id, memory_data):
        """Save memory for a session to file"""
        memory_file = self._get_memory_file(session_id)
        
        try:
            memory_data['last_updated'] = datetime.now().isoformat()
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving memory: {e}")
            return False
    
    def update_memory(self, session_id, key, value):
        """Update a specific memory field"""
        memory = self.load_memory(session_id)
        
        # Handle nested keys (e.g., 'preferences.language')
        if '.' in key:
            parts = key.split('.')
            current = memory
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            memory[key] = value
        
        return self.save_memory(session_id, memory)
    
    def forget_memory(self, session_id, key=None):
        """Forget specific memory or all memory for a session"""
        if key is None:
            # Delete entire memory file
            memory_file = self._get_memory_file(session_id)
            try:
                if memory_file.exists():
                    memory_file.unlink()
                return True
            except Exception as e:
                print(f"Error deleting memory: {e}")
                return False
        else:
            # Delete specific key
            memory = self.load_memory(session_id)
            if '.' in key:
                parts = key.split('.')
                current = memory
                for part in parts[:-1]:
                    if part not in current:
                        return False
                    current = current[part]
                if parts[-1] in current:
                    del current[parts[-1]]
            else:
                if key in memory:
                    del memory[key]
            
            return self.save_memory(session_id, memory)
    
    def get_memory_context(self, session_id):
        """Get memory context as a string for the AI"""
        memory = self.load_memory(session_id)
        
        if not memory or all(not v for v in memory.values() if v not in ['created_at', 'last_updated']):
            return ""
        
        context_parts = []
        
        if memory.get('nickname'):
            context_parts.append(f"User's preferred name: {memory['nickname']}")
        
        if memory.get('preferences'):
            prefs = []
            for k, v in memory['preferences'].items():
                prefs.append(f"{k}: {v}")
            if prefs:
                context_parts.append(f"User preferences: {', '.join(prefs)}")
        
        if memory.get('gaming_info'):
            gaming = []
            for k, v in memory['gaming_info'].items():
                gaming.append(f"{k}: {v}")
            if gaming:
                context_parts.append(f"Gaming info: {', '.join(gaming)}")
        
        if memory.get('work_topics') and len(memory['work_topics']) > 0:
            context_parts.append(f"Work/study topics: {', '.join(memory['work_topics'])}")
        
        if context_parts:
            return "MEMORY (user's saved information):\n" + "\n".join(context_parts)
        
        return ""
