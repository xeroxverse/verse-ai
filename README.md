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

1. **Clone the repository**:
```bash
git clone https://github.com/xeroxverse/Verse.git
cd Verse
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
```

4. **Get your OpenAI API Key** (see detailed instructions below)

5. **Edit `.env` file** and add your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

6. **Run the application**:
```bash
python app.py
```

7. **Open your browser** and navigate to `http://localhost:5000`

## 🔑 Getting Your OpenAI API Key

Verse requires an OpenAI API key to function. Follow these steps to obtain one:

### Step 1: Create an OpenAI Account
1. Visit [OpenAI's website](https://platform.openai.com/)
2. Click **Sign Up** (or **Log In** if you already have an account)
3. Complete the registration process with your email address

### Step 2: Generate an API Key
1. Once logged in, go to [API Keys page](https://platform.openai.com/api-keys)
2. Click **"+ Create new secret key"**
3. Give your key a name (e.g., "Verse AI Assistant")
4. Click **"Create secret key"**
5. **Important**: Copy the key immediately - you won't be able to see it again!

### Step 3: Add the Key to Your .env File
1. Open the `.env` file in your project directory
2. Replace `your_openai_api_key_here` with your actual API key:
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxx
```
3. Save the file

### Step 4: Add Credits (If Needed)
- New OpenAI accounts may receive free credits
- If you've used your free credits, you'll need to [add billing information](https://platform.openai.com/account/billing)
- Verse uses GPT-3.5-turbo by default, which is cost-effective (~$0.002 per 1K tokens)

### 🔒 Security Note
- **Never share your API key** publicly or commit it to version control
- The `.env` file is in `.gitignore` to prevent accidental commits
- If you accidentally expose your key, delete it immediately from the OpenAI dashboard and create a new one

### ⚠️ Troubleshooting API Key Issues

**"API key error" message?**
- Verify your API key is correctly copied (no extra spaces)
- Check that you have credits available in your OpenAI account
- Ensure the key hasn't been revoked in the OpenAI dashboard

**"Rate limit exceeded" error?**
- You may have exceeded your usage quota
- Check your [usage dashboard](https://platform.openai.com/account/usage)
- Consider upgrading your plan or waiting for the quota to reset

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

Edit `.env` to customize:
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

## 🏗️ Project Structure

```
Verse/
├── app.py                      # Flask application with memory API
├── assistant.py                # AI core logic with context-aware prompt
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
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
