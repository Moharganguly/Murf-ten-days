# Day 3: Health & Wellness Voice Companion 🧘

A supportive daily check-in voice agent built with LiveKit Agents v1.3.x that tracks mood, energy levels, and daily goals through natural conversation.

## 🌟 Overview

The Wellness Companion conducts personalized voice-based check-ins to help users:
- Reflect on their current mood and energy
- Set 1-3 daily intentions or goals
- Receive simple, actionable wellness suggestions
- Track progress over time with conversation memory

**Important:** This is a supportive companion, not a medical professional. It provides no diagnosis, treatment, or therapy.

## ✨ Features

### Primary Features
- ✅ **Voice-Based Check-Ins** - Natural conversation via voice (STT + TTS)
- ✅ **Mood & Energy Tracking** - Asks about how you're feeling today
- ✅ **Daily Goal Setting** - Helps identify 1-3 main objectives
- ✅ **JSON Persistence** - All check-ins saved to `wellness_log.json`
- ✅ **Conversation Memory** - References previous check-ins naturally
- ✅ **Grounded Advice** - Simple, realistic suggestions (no medical claims)
- ✅ **Session Recap** - Summarizes and confirms before saving

### Agent Behavior
- Warm and empathetic (not overly cheerful or clinical)
- Asks ONE question at a time for natural flow
- Context-aware greetings based on check-in history
- Offers small, actionable suggestions (breaks, walks, hydration)
- Never provides medical advice or diagnosis

## 🏗️ Architecture

```
wellness_agent.py
├── WellnessDataManager     # Handles JSON persistence
│   ├── load_history()      # Loads all check-ins
│   ├── get_last_check_in() # Gets most recent session
│   └── save_check_in()     # Saves new check-in
│
├── Function Tools (@function_tool)
│   ├── record_mood()       # Saves mood/energy summary
│   ├── record_objectives() # Saves daily goals
│   └── complete_check_in() # Finalizes session
│
└── entrypoint()            # Main conversation loop
```

## 📦 Installation

### Prerequisites
- Python 3.9+
- LiveKit account ([sign up here](https://livekit.io))
- API Keys:
  - OpenAI (for LLM)
  - Deepgram (for Speech-to-Text)
  - Cartesia (for Text-to-Speech)

### Setup Steps

1. **Install Dependencies**
```bash
pip install livekit livekit-agents[openai,deepgram,cartesia,silero] python-dotenv
```

2. **Configure Environment Variables**

Create `.env.local` in the backend folder:
```bash
# .env.local
OPENAI_API_KEY=sk-proj-your-key-here
DEEPGRAM_API_KEY=your-key-here
CARTESIA_API_KEY=your-key-here
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

3. **Run the Agent**
```bash
python wellness_agent.py dev
```

## 🎯 How It Works

### Conversation Flow

1. **Greeting** → Agent welcomes user with context
   - First time: "Hello! Welcome to your first wellness check-in"
   - Returning: "Welcome back! This is check-in #5. Last time you mentioned..."

2. **Mood Exploration** → Natural questions about feelings
   - "How are you feeling today?"
   - "What's your energy like?"
   - Calls `record_mood()` when understanding is clear

3. **Goal Discussion** → Identifies daily intentions
   - "What are 1-3 things you'd like to accomplish today?"
   - Calls `record_objectives()` when goals are shared

4. **Supportive Suggestions** → Offers small, actionable advice
   - Break large tasks into smaller steps
   - Take short breaks
   - 5-minute walks
   - Hydration reminders

5. **Recap & Confirmation** → Summarizes the session
   - "So you're feeling [mood] and want to [objectives]. Does this sound right?"
   - Calls `complete_check_in()` once confirmed

6. **Closing** → Positive sign-off
   - "Have a wonderful day, and I'll check in with you again tomorrow!"

## 📊 Data Format

Check-ins are stored in `wellness_data/wellness_log.json`:

```json
{
  "check_ins": [
    {
      "timestamp": "2025-11-23T10:30:00.123456",
      "mood_summary": "Feeling tired but motivated to get things done",
      "objectives": [
        "Finish the project report",
        "Go for a 20-minute walk",
        "Prep meals for tomorrow"
      ],
      "agent_summary": "User is managing low energy with clear goals and self-care plans"
    }
  ]
}
```

### Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 timestamp of check-in |
| `mood_summary` | string | Brief summary of mood and energy |
| `objectives` | array | List of 1-3 daily goals |
| `agent_summary` | string | Agent's one-sentence session summary |

## 🛠️ Technology Stack

- **LiveKit Agents v1.3.x** - Voice agent framework
- **OpenAI GPT-4o-mini** - Language model
- **Deepgram Nova-2** - Speech-to-Text
- **Cartesia** - Text-to-Speech
- **Silero VAD** - Voice Activity Detection (optional)

## 🧪 Testing

### Manual Testing

1. **First Check-In**
   - Run the agent
   - Share your mood when asked
   - State 1-3 goals
   - Confirm the recap
   - Check `wellness_data/wellness_log.json` was created

2. **Second Check-In** (Next Day)
   - Run the agent again
   - Verify it references your previous check-in
   - Complete a new session
   - Confirm data is appended to JSON

3. **Verify Conversation Flow**
   - Agent asks ONE question at a time
   - Tone is warm but grounded
   - No medical advice given
   - Recap is accurate

### Expected Output

When running successfully, you should see:
```
🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟
🧘 WELLNESS COMPANION - DAILY CHECK-IN AGENT v1.3
📁 Check-ins will be saved to: /path/to/wellness_data
🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟

🔥 Prewarming...
✅ Silero VAD loaded successfully
============================================================
🧘 NEW WELLNESS CHECK-IN SESSION STARTED
Room: your-room-name
============================================================
🔌 Initializing plugins...
✅ Deepgram STT initialized
✅ OpenAI LLM initialized (gpt-4o-mini)
✅ Cartesia TTS initialized
✅ Using prewarmed Silero VAD
🎙️ Starting wellness check-in session...
✅ Greeting generated successfully
✅ Session active - agent is listening...
```

## 📁 Project Structure

```
backend/
├── wellness_agent.py          # Main agent file
├── .env.local                 # API keys (not committed)
├── .gitignore                 # Git ignore rules
└── wellness_data/             # Data directory
    └── wellness_log.json      # Check-in history
```

## 🚀 Usage Example

### Starting a Check-In

```bash
python wellness_agent.py dev
```

### Example Conversation

**Agent:** "Hi! Welcome back to your daily check-in. This is check-in number 3. Last time you mentioned feeling a bit overwhelmed. How are you feeling today?"

**You:** "I'm feeling much better today, more energized."

**Agent:** "That's wonderful to hear! What's giving you that energy today?"

**You:** "I got good sleep and I'm excited about my projects."

**Agent:** "Great! What are 1-3 things you'd like to accomplish today?"

**You:** "I want to finish my wellness agent project, go for a run, and meal prep."

**Agent:** "Perfect! So today you're feeling energized and excited, and you want to finish your project, go for a run, and do meal prep. Does that sound right?"

**You:** "Yes, that's right."

**Agent:** "Wonderful! I've saved today's check-in. Have a great day!"

## 🔒 Privacy & Safety

### What the Agent Does NOT Do
- ❌ Diagnose medical or mental health conditions
- ❌ Provide therapy or clinical treatment
- ❌ Act as a replacement for professional care
- ❌ Store data in the cloud (only local JSON)
- ❌ Share your data with third parties

### Data Privacy
- All check-in data stored locally in `wellness_log.json`
- No data sent to external services except:
  - Voice transcription (Deepgram)
  - LLM processing (OpenAI)
  - Voice synthesis (Cartesia)
- You can delete `wellness_log.json` anytime to remove all history

## 🎨 Customization

### Change Voice Settings

In `entrypoint()` function:
```python
# Different TTS voices available
tts_plugin = cartesia.TTS(voice="friendly-woman")  # or other voices

# Different LLM models
llm_plugin = openai.LLM(model="gpt-4o")  # for higher quality
```

### Adjust Conversation Style

Edit the `create_system_instructions()` function to:
- Change tone (more casual vs. formal)
- Adjust conversation length
- Modify types of questions asked
- Change advice guidelines

### Track Additional Data

Modify the function tools to capture:
- Sleep quality
- Exercise completed
- Water intake
- Stress level (1-10)
- Custom fields

## 🐛 Troubleshooting

### Agent doesn't remember past check-ins
- Check that `wellness_data/wellness_log.json` exists and is valid JSON
- Verify permissions to read/write in the directory

### Voice not working
- Ensure microphone permissions are granted
- Check VAD is loading correctly
- Try adjusting microphone sensitivity

### API errors
- Verify all API keys in `.env.local` are correct
- Check API key quotas haven't been exceeded
- Ensure internet connection is stable

### Functions not being called
- Check logs for function call attempts
- Verify function descriptions are clear
- Make sure conversation reaches the right trigger points

## 📚 Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [LiveKit Function Tools](https://docs.livekit.io/agents/build/tools/)
- [Agent API v1.3.x Guide](https://docs.livekit.io/agents/build/)
- [Day 3 Assignment](https://docs.livekit.io/agents/examples/wellness/)

## 🤝 Contributing

Feel free to:
- Fork and extend with advanced features
- Add MCP server integration for task management
- Implement analytics and insights
- Create visualizations of mood trends
- Add multi-language support

## 📝 License

MIT License - Feel free to use and modify for your projects!

## 🙏 Acknowledgments

Built as part of the LiveKit Agents learning series.

Special thanks to:
- LiveKit team for the excellent voice agent framework
- OpenAI, Deepgram, and Cartesia for their APIs

---

**Ready to start your wellness journey?** Run `python wellness_agent.py dev` and have your first check-in! 🌟🧘
