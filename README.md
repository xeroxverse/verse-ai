# 🤖 Verse - Your AI Sidekick

**Verse** is a professional AI sidekick designed to help you excel at gaming, work, study, and multitasking—especially on mobile. Think of Verse as your smart, friendly AI companion that's always ready to assist, not just another chatbot.

## ✨ What Makes Verse Special

Verse automatically adapts to what you need:
- **🎮 Gaming Mode**: Get fast, actionable tips and strategies like a skilled teammate
- **💼 Work & Study Mode**: Receive clear, structured help with tasks, ideas, and problem-solving
- **💬 General Chat**: Enjoy friendly, supportive AI companionship for everyday questions

## 🚀 Key Features

### 🧠 Smart Context Switching
Verse understands what you're asking about and adjusts its personality:
- **Gaming**: Short, tactical advice optimized for quick reading while playing
- **Productivity**: Step-by-step guidance and clear explanations
- **Conversation**: Calm, friendly responses without being chatty

### 🎙️ Voice Interaction (Hands-Free)
- **Speech-to-Text**: Talk to Verse using your microphone
- **Text-to-Speech**: Hear responses while gaming or multitasking
- **Mobile-Optimized**: Perfect for one-handed use on phones
- **Automatic Fallback**: Works with text if voice is unavailable

### 🧠 Local Memory System
Verse can remember important things when you ask:
- User preferences (language, reply style)
- Gaming information (games played, skill level)
- Work/study topics you want to track
- Your preferred nickname

**Privacy-First**: All memory is stored locally on your device (not in the cloud)

### 📱 Mobile-First Design
- Clean, minimal interface
- One-hand usability
- Fast responses
- Touch-friendly controls
- Works while switching apps

## 🎯 Example Use Cases

```
🎮 GAMING
"What's the best early game strategy for Valorant?"
"How do I counter this team comp?"
"Remember that I main support characters"

💼 WORK & STUDY
"Break down this complex topic for me"
"Help me write a professional email"
"What's the best way to organize my study schedule?"

🎙️ VOICE CHAT
Click 🎤 and say: "Give me quick tips for improving aim"
Verse speaks the answer while you keep playing

🧠 MEMORY
"Remember that I prefer short replies"
"What games have I asked you about?"
"Yaad rakhna - I'm learning Python"
```

## 🛠️ Tech Stack

- **Backend**: Python with Flask
- **AI**: OpenAI GPT models (context-aware system prompt)
- **Frontend**: HTML, CSS, JavaScript
- **Voice**: Web Speech API (browser-based)
- **Memory**: Local JSON file storage

## 📦 Installation

### Prerequisites

**⚠️ IMPORTANT**: You need an OpenAI API key to use Verse. 

**📖 [Click here for detailed API key setup guide](API_KEY_SETUP.md)**

**Quick summary**:
1. Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or log in to OpenAI
3. Create a new API key
4. Copy the key (starts with `sk-`)

### Installation Steps

1. **Clone the repository**:
```bash
git clone https://github.com/xeroxverse/verse-ai.git
cd verse-ai
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key**:
```bash
cp .env.example .env
# Edit .env and replace 'your_openai_api_key_here' with your actual API key
```

Example:
```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

> 💡 **Need help?** See the [detailed API Key Setup Guide](API_KEY_SETUP.md)

4. **Run the application**:
```bash
python app.py
```

5. **Open your browser** and navigate to `http://localhost:5000`

> ⚠️ If you see "API key error", double-check your `.env` file configuration.

## 🎮 Usage

### Text Chat
1. Type your question in the input box
2. Press Enter or click ✈️ to send
3. Get instant AI-powered responses

### Voice Input
1. Click the 🎤 Voice button
2. Speak your question when the button turns red
3. Verse automatically processes and responds

### Speech Output
1. Click the 🔊 Speak button to enable
2. Verse will read all responses aloud
3. Perfect for hands-free multitasking

### Memory Features
- Verse automatically detects when you want to save something
- Say "remember this" or "yaad rakhna" to store information
- Your preferences persist between sessions
- Memory is stored locally in `user_memory/` folder

## 📋 Configuration

### API Key Configuration

The most important configuration is your OpenAI API key. Edit `.env` to customize:

```bash
# REQUIRED: Your OpenAI API key
OPENAI_API_KEY=sk-proj-your-actual-key-here

# OPTIONAL: Change the OpenAI model (default: gpt-3.5-turbo)
OPENAI_MODEL=gpt-3.5-turbo

# OPTIONAL: Use a different OpenAI endpoint
OPENAI_BASE_URL=https://api.openai.com/v1
```

**Getting your API key**: Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

**Need help?** Check out the [API Key Setup Guide](API_KEY_SETUP.md) for detailed instructions.

### Available Models

You can change the `OPENAI_MODEL` in your `.env` file:
- `gpt-3.5-turbo` - Fast and affordable (recommended)
- `gpt-4` - More capable but slower and more expensive
- `gpt-4-turbo` - Balance of speed and capability

## 🏗️ Project Structure

```
Verse/
├── app.py                      # Flask application with memory API
├── assistant.py                # AI core logic with context-aware prompt
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── API_KEY_SETUP.md            # Detailed API key setup guide
├── user_memory/                # Local memory storage (auto-created)
├── static/
│   ├── css/
│   │   └── style.css          # Mobile-first responsive styles
│   └── js/
│       └── main.js            # Frontend with voice features
├── templates/
│   └── index.html             # Minimalist mobile-optimized UI
└── README.md
```

## 🐛 Troubleshooting

### "API key error" or "not configured"

**Problem**: OpenAI API key is missing or invalid

**Solution**:
1. Make sure you have a `.env` file (copy from `.env.example`)
2. Add your API key from https://platform.openai.com/api-keys
3. Verify the key starts with `sk-`
4. Restart the application

📖 **See [API_KEY_SETUP.md](API_KEY_SETUP.md) for detailed instructions**

### "Insufficient quota" or "Billing error"

**Problem**: Your OpenAI account needs billing setup or has run out of credits

**Solution**:
1. Visit https://platform.openai.com/account/billing
2. Add a payment method
3. Check your usage and add credits if needed

### "Rate limit exceeded"

**Problem**: Too many requests to OpenAI API

**Solution**:
1. Wait a few minutes before trying again
2. If persistent, check your OpenAI plan limits

### Application won't start

**Problem**: Missing dependencies or configuration

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version (needs 3.8+)
python --version

# Verify .env file exists
ls -la .env
```

## 🔒 Privacy & Security

- **Local Memory**: All personal data stored on your device
- **No Cloud Sync**: Memory files stay on your computer
- **User Control**: Only saves what you explicitly ask
- **Transparent**: Memory stored in readable JSON format

## 🎯 Design Philosophy

Verse follows the **KISS principle** (Keep It Simple, Sidekick):
- No complex mode switching or UI clutter
- One global system prompt handles all contexts
- Mobile-first, minimalist interface
- Fast, practical, and helpful
- Voice-first ready for future enhancements

## 🔮 Future-Ready Features

Verse is designed to support (conceptually):
- Always-on assistant capabilities
- Gaming overlay integration
- Quick command shortcuts
- Long-term personalization
- Multi-language support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 💬 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Built for gamers, workers, students, and multitaskers**  
*Verse - Your AI sidekick for everything* 🤖✨
