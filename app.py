#!/usr/bin/env python3
"""
AI Gaming Assistant - Main Flask Application
Provides a web interface for an AI-powered gaming assistant
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
from datetime import datetime
from assistant import GamingAssistant
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Initialize the gaming assistant
assistant = GamingAssistant()

# Store conversation history
conversations = {}


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests from the frontend"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        game_context = data.get('game', 'general')
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Initialize conversation history for new sessions
        if session_id not in conversations:
            conversations[session_id] = []
        
        # Get response from AI assistant (with memory)
        response = assistant.get_response(
            user_message, 
            game_context=game_context,
            conversation_history=conversations[session_id],
            session_id=session_id
        )
        
        # Store conversation
        conversations[session_id].append({
            'user': user_message,
            'assistant': response,
            'timestamp': datetime.now().isoformat(),
            'game': game_context
        })
        
        # Keep only last 20 messages to avoid memory issues
        if len(conversations[session_id]) > 20:
            conversations[session_id] = conversations[session_id][-20:]
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'success': True
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history for a session"""
    session_id = request.args.get('session_id', 'default')
    history = conversations.get(session_id, [])
    return jsonify({'history': history, 'success': True})


@app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history for a session"""
    data = request.json
    session_id = data.get('session_id', 'default')
    
    if session_id in conversations:
        conversations[session_id] = []
    
    return jsonify({'success': True, 'message': 'History cleared'})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    session_id = request.args.get('session_id', 'default')
    history = conversations.get(session_id, [])
    
    stats = {
        'total_messages': len(history),
        'session_id': session_id,
        'games_discussed': list(set([msg.get('game', 'general') for msg in history]))
    }
    
    return jsonify({'stats': stats, 'success': True})


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'assistant_ready': assistant.is_ready()
    })


# Memory API Endpoints

@app.route('/api/memory', methods=['GET'])
def get_memory():
    """Get memory for a session"""
    session_id = request.args.get('session_id', 'default')
    memory = assistant.load_memory(session_id)
    return jsonify({'memory': memory, 'success': True})


@app.route('/api/memory', methods=['POST'])
def save_memory_data():
    """Save or update memory for a session"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        key = data.get('key')
        value = data.get('value')
        
        if not key:
            return jsonify({'error': 'Key is required'}), 400
        
        success = assistant.update_memory(session_id, key, value)
        
        return jsonify({
            'success': success,
            'message': 'Memory updated successfully' if success else 'Failed to update memory'
        })
    except Exception as e:
        print(f"Error saving memory: {e}")
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500


@app.route('/api/memory', methods=['DELETE'])
def delete_memory():
    """Delete memory for a session"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        key = data.get('key')  # Optional: specific key to delete
        
        success = assistant.forget_memory(session_id, key)
        
        return jsonify({
            'success': success,
            'message': 'Memory deleted successfully' if success else 'Failed to delete memory'
        })
    except Exception as e:
        print(f"Error deleting memory: {e}")
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'success': False
        }), 500


if __name__ == '__main__':
    print("🎮 Starting Verse - Your AI Sidekick...")
    print("🌐 Open your browser and navigate to http://localhost:5000")
    print("💡 Ask me anything about gaming, work, study, or life!")
    app.run(host='0.0.0.0', port=5000, debug=True)
