# 🔑 OpenAI API Key Setup Guide

This guide will help you get and configure your OpenAI API key for Verse AI.

## 📋 Quick Start

1. Get your API key from OpenAI
2. Create a `.env` file
3. Add your API key
4. Start using Verse!

---

## 🎯 Step 1: Getting Your OpenAI API Key

### Create an OpenAI Account

1. **Visit OpenAI's Website**
   - Go to [https://platform.openai.com](https://platform.openai.com)
   - Click "Sign up" if you don't have an account
   - Or click "Log in" if you already have an account

2. **Complete Registration**
   - Verify your email address
   - Add a phone number for verification (required by OpenAI)

### Generate Your API Key

1. **Navigate to API Keys Page**
   - Once logged in, go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Or click on your profile picture → "API keys"

2. **Create a New Key**
   - Click the "Create new secret key" button
   - Give it a name (e.g., "Verse AI Assistant")
   - Click "Create secret key"

3. **Copy Your Key**
   - ⚠️ **IMPORTANT**: Copy the key immediately and store it safely
   - You won't be able to see it again after closing the dialog
   - It looks like: `sk-proj-...` (starts with `sk-`)

---

## 🎯 Step 2: Configure Verse with Your API Key

### Method 1: Using .env File (Recommended)

1. **Create the `.env` file**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file**
   Open `.env` in your text editor and replace `your_openai_api_key_here` with your actual API key:
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-3.5-turbo
   ```

3. **Save the file**

### Method 2: Using Environment Variables

Alternatively, you can set the environment variable directly:

**Linux/Mac:**
```bash
export OPENAI_API_KEY='sk-proj-your-actual-key-here'
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY='sk-proj-your-actual-key-here'
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-proj-your-actual-key-here
```

---

## 🎯 Step 3: Verify Your Setup

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Check the terminal output**
   - ✅ If configured correctly, you'll see: "🎮 Starting Verse - Your AI Sidekick..."
   - ❌ If not configured, you'll see: "⚠️ WARNING: OPENAI_API_KEY not found!"

3. **Test in your browser**
   - Open http://localhost:5000
   - The status indicator should show "Ready" or "Connected"
   - Try sending a message like "Hello!"
   - If it works, you're all set! 🎉

---

## 💰 Cost and Billing

### Understanding OpenAI Pricing

- OpenAI charges based on usage (tokens processed)
- GPT-3.5-turbo (default model) is very affordable
- Typical cost: ~$0.002 per conversation (less than a penny!)

### Add Billing Information

1. Go to [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)
2. Click "Add payment method"
3. Add a credit/debit card
4. Optionally, set usage limits to control costs:
   - Click "Usage limits"
   - Set a monthly budget (e.g., $5)
   - Enable email notifications

### Free Trial Credits

- New OpenAI accounts often receive free trial credits
- Check your balance at [https://platform.openai.com/account/usage](https://platform.openai.com/account/usage)

---

## 🔒 Security Best Practices

### Keep Your API Key Safe

- ✅ **DO**: Store your API key in `.env` file (already in `.gitignore`)
- ✅ **DO**: Keep your API key private and never share it
- ✅ **DO**: Revoke and regenerate if accidentally exposed
- ❌ **DON'T**: Commit `.env` file to git
- ❌ **DON'T**: Share your API key in screenshots or logs
- ❌ **DON'T**: Hardcode API keys in source code

### Revoke a Compromised Key

If you accidentally exposed your API key:
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click the trash icon next to the compromised key
3. Create a new key
4. Update your `.env` file with the new key

---

## 🐛 Troubleshooting

### "API key error" or "Authentication failed"

**Problem**: Your API key is invalid or not set correctly

**Solutions**:
1. Double-check your API key in `.env` file
2. Make sure there are no extra spaces or quotes
3. Verify the key starts with `sk-`
4. Try regenerating your API key on OpenAI's website

### "Rate limit exceeded"

**Problem**: You've exceeded OpenAI's rate limits

**Solutions**:
1. Wait a few minutes and try again
2. Check your usage at https://platform.openai.com/account/usage
3. Consider upgrading your OpenAI plan if you need higher limits

### "Insufficient quota" or "Billing error"

**Problem**: Your OpenAI account doesn't have sufficient credits or billing setup

**Solutions**:
1. Add a payment method to your OpenAI account
2. Check if you have free trial credits remaining
3. Add more credits to your account

### Application shows "not configured" error

**Problem**: The `.env` file is not being loaded

**Solutions**:
1. Verify `.env` file exists in the project root directory
2. Make sure the file is named exactly `.env` (not `.env.txt`)
3. Restart the application after creating/editing `.env`
4. Check that `python-dotenv` is installed: `pip install python-dotenv`

---

## 🔄 Changing Your API Key

To use a different API key:
1. Open `.env` file
2. Replace the value of `OPENAI_API_KEY` with your new key
3. Save the file
4. Restart the application

---

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [OpenAI API Keys Management](https://platform.openai.com/api-keys)
- [OpenAI Pricing](https://openai.com/pricing)
- [OpenAI Usage Dashboard](https://platform.openai.com/account/usage)

---

## ❓ Still Need Help?

If you're still having trouble:
1. Check the [GitHub Issues](https://github.com/xeroxverse/verse-ai/issues) for similar problems
2. Create a new issue with details about your problem
3. Make sure to **NOT** include your actual API key in issue reports!

---

**Ready to start?** Follow the steps above, and you'll be chatting with Verse in no time! 🚀
