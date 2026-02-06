// Verse AI Sidekick - Frontend JavaScript with Voice Support

let sessionId = generateSessionId();
let isLoading = false;
let isSpeechEnabled = false;
let recognition = null;
let synthesis = window.speechSynthesis;
let isListening = false;

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// DOM Elements
const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const clearBtn = document.getElementById('clear-btn');
const voiceBtn = document.getElementById('voice-btn');
const speakBtn = document.getElementById('speak-btn');
const statusElement = document.getElementById('status');
const statusText = document.getElementById('status-text');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
    setupVoiceRecognition();
    userInput.focus();
});

// Setup event listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    clearBtn.addEventListener('click', clearChat);
    voiceBtn.addEventListener('click', toggleVoiceInput);
    speakBtn.addEventListener('click', toggleSpeechOutput);
    
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
    });
}

// Voice Recognition Setup
function setupVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            userInput.style.height = 'auto';
            userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
            sendMessage();
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            stopVoiceInput();
            if (event.error !== 'no-speech' && event.error !== 'aborted') {
                addSystemMessage('Voice input error. Please try again or type your message.');
            }
        };
        
        recognition.onend = () => {
            stopVoiceInput();
        };
    } else {
        console.log('Speech recognition not supported');
        voiceBtn.style.opacity = '0.5';
        voiceBtn.title = 'Voice input not supported in your browser';
    }
}

// Toggle Voice Input
function toggleVoiceInput() {
    if (!recognition) {
        addSystemMessage('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
        return;
    }
    
    if (isListening) {
        stopVoiceInput();
    } else {
        startVoiceInput();
    }
}

// Start Voice Input
function startVoiceInput() {
    try {
        recognition.start();
        isListening = true;
        voiceBtn.classList.add('recording');
        document.getElementById('voice-icon').textContent = '🔴';
        userInput.placeholder = 'Listening...';
    } catch (error) {
        console.error('Error starting voice recognition:', error);
        addSystemMessage('Could not start voice input. Please try again.');
    }
}

// Stop Voice Input
function stopVoiceInput() {
    if (recognition && isListening) {
        try {
            recognition.stop();
        } catch (error) {
            console.error('Error stopping recognition:', error);
        }
    }
    isListening = false;
    voiceBtn.classList.remove('recording');
    document.getElementById('voice-icon').textContent = '🎤';
    userInput.placeholder = 'Ask me anything...';
}

// Toggle Speech Output
function toggleSpeechOutput() {
    isSpeechEnabled = !isSpeechEnabled;
    
    if (isSpeechEnabled) {
        speakBtn.classList.add('active');
        document.getElementById('speak-icon').textContent = '🔊';
        addSystemMessage('Speech output enabled. I\'ll read my responses to you.');
    } else {
        speakBtn.classList.remove('active');
        document.getElementById('speak-icon').textContent = '🔇';
        if (synthesis.speaking) {
            synthesis.cancel();
        }
    }
}

// Speak Text
function speakText(text) {
    if (!isSpeechEnabled || !synthesis) return;
    
    // Cancel any ongoing speech
    if (synthesis.speaking) {
        synthesis.cancel();
    }
    
    // Clean text for speech (remove emojis and special formatting)
    const cleanText = text.replace(/[🎮💼🎙️🧠✨🔥💡⚡🎯❌⚠️⏳⏱️]/g, '').trim();
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    synthesis.speak(utterance);
}

// Check API health
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy' && data.assistant_ready) {
            updateStatus('online', 'Verse Ready');
        } else {
            updateStatus('error', 'AI Not Configured');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatus('error', 'Connection Error');
    }
}

// Update status indicator
function updateStatus(status, message) {
    statusElement.className = `status ${status}`;
    statusText.textContent = message;
}

// Send message to AI
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message || isLoading) return;
    
    // Stop any voice input
    if (isListening) {
        stopVoiceInput();
    }
    
    // Add user message to chat
    addMessage('user', message);
    
    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';
    
    // Show loading
    isLoading = true;
    sendBtn.disabled = true;
    const loadingElement = addLoadingMessage();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                game: 'general',
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        // Remove loading message
        loadingElement.remove();
        
        if (data.success) {
            addMessage('assistant', data.response);
            
            // Speak the response if enabled
            speakText(data.response);
        } else {
            addMessage('assistant', `Error: ${data.error || 'Unknown error occurred'}`);
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        loadingElement.remove();
        addMessage('assistant', '❌ Connection error. Please check your connection and try again.');
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// Add message to chat
function addMessage(role, content) {
    // Remove welcome message if it exists
    const welcomeMessage = chatContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

// Add system message
function addSystemMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.style.opacity = '0.8';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = '💡 ' + content;
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

// Add loading message
function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.textContent = 'Thinking';
    
    messageDiv.appendChild(loadingDiv);
    chatContainer.appendChild(messageDiv);
    
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

// Clear chat history
async function clearChat() {
    if (!confirm('Clear chat history?')) {
        return;
    }
    
    // Stop any ongoing speech
    if (synthesis.speaking) {
        synthesis.cancel();
    }
    
    try {
        await fetch('/api/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        // Clear chat container
        chatContainer.innerHTML = `
            <div class="welcome-message">
                <h2>👋 Chat cleared!</h2>
                <p>Ready for new questions!</p>
            </div>
        `;
        
        // Generate new session ID
        sessionId = generateSessionId();
        
    } catch (error) {
        console.error('Error clearing chat:', error);
        addSystemMessage('Failed to clear chat. Please try again.');
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Escape to stop voice input
    if (e.key === 'Escape' && isListening) {
        e.preventDefault();
        stopVoiceInput();
    }
    
    // Ctrl/Cmd + K to focus input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        userInput.focus();
    }
});

console.log('🤖 Verse AI Sidekick loaded!');
console.log('💡 Features:');
console.log('   🎤 Voice input - Click microphone button');
console.log('   🔊 Speech output - Click speaker button');
console.log('   ⌨️  Text chat - Type and press Enter');
console.log('   🗑️  Clear - Clear conversation history');
