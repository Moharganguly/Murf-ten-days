# 🎭 Voice Improv Battle - AI Game Show

An interactive voice-powered improv comedy game show where you perform improvised scenes and receive real-time reactions from an AI host. Think "Whose Line Is It Anyway?" meets AI voice agents! Built for the Murf AI 10 Days of Voice Agents Challenge - Day 10.

## 🌟 Features

- **🎤 Voice-First Gameplay** - Entire game played through natural speech
- **🎭 AI Game Show Host** - Energetic, witty host with varied personality
- **🎬 15 Unique Scenarios** - From time-travel guides to talking parrots
- **💬 Real-Time Transcript** - See the conversation as it happens
- **🎯 Varied Reactions** - Host gives honest, creative feedback (not always positive!)
- **📊 Performance Summary** - Get your improv profile at the end
- **🛑 Full Controls** - Stop, disconnect, replay anytime
- **🎨 Dramatic UI** - Game show themed interface with animations

## 🎬 How It Works

### Game Flow:

**1. Welcome & Setup**
- Enter your stage name
- Connect to the show
- Host greets you with energy

**2. Round 1 - The Scenario**
Host: "Round 1 of 4: You are a barista who has to tell a customer that their latte is actually a portal to another dimension. And... ACTION!"

**3. Your Performance** (30 seconds)
You: *Improvises the scene with voice acting*

**4. Host Reaction**
Host: "HA! The way you casually mentioned 'slight dimensional turbulence' like it's normal - brilliant! Though you could've leaned more into the customer's panic. Let's keep rolling!"

**5. Repeat for 4 Rounds**

**6. Final Summary**
Host: "That's a wrap! You're an ABSURDIST at heart - everything got wonderfully weird! That portal latte and the robot yoga class were my favorites. Thanks for playing IMPROV BATTLE!"

## 🎭 Sample Scenarios

Our 15 improv scenarios include:

### Easy Scenarios:
- **Time-Travelling Tour Guide** - Explain smartphones to someone from the 1800s
- **Weather Forecaster** - Predict ridiculous weather (raining cats and dogs literally)

### Medium Scenarios:
- **Portal Latte Barista** - Tell customer their coffee is a dimensional portal
- **Escaped Order Waiter** - Explain that the customer's meal escaped the kitchen
- **Cursed Object Return** - Return an obviously cursed item to skeptical shop owner
- **Haunted House Agent** - Sell a haunted house to a ghost skeptic
- **Talking Parrot Detective** - Interrogate a parrot witness to cookie theft
- **Museum Guide** - Explain why dinosaurs come alive at night
- **Fantasy Flight Attendant** - Announce the plane entered a fantasy realm
- **Library Shusher** - Shush increasingly loud mythical creatures

### Hard Scenarios:
- **Vampire Tech Support** - Help a vampire set up video calls during daytime
- **Robot Yoga Instructor** - Teach yoga to malfunctioning robots
- **Superhero Therapist** - Counsel a burned-out superhero
- **Conscious Ingredients Chef** - Cook on live TV with sentient vegetables
- **Dragon Driving Instructor** - Teach a dragon to parallel park

## 🏗️ Architecture

Player Voice → LiveKit Cloud → Improv Agent
↓
┌───────────────┴──────────────┐
↓ ↓ ↓
Deepgram STT Gemini AI Murf Alicia TTS
↓ ↓ ↓
└───────────────┬──────────────┘
↓
Game State Management
(rounds, scenarios, reactions)
↓
Scenario Database (JSON)
15 unique improv prompts

text

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- LiveKit Agents SDK
- Murf AI Falcon (Alicia voice - high energy host)
- Deepgram Nova-2 (Speech-to-Text)
- Google Gemini 2.0 (Creative reactions & responses)
- JSON (Scenario database)
- Silero VAD (Voice Activity Detection)

**Frontend:**
- Next.js 15 (App Router + Turbopack)
- TypeScript
- LiveKit React Components
- TailwindCSS
- Real-time transcription display

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- Node.js 18+ and npm/pnpm
- LiveKit Cloud account
- API keys for: Murf AI, Deepgram, Google Gemini

### Backend Setup

Navigate to backend directory
cd backend

Install dependencies
pip install -r requirements.txt

text

### Frontend Setup

Navigate to frontend directory
cd frontend

Install dependencies
npm install

or
pnpm install

text

### Environment Configuration

Create a `.env.local` file in the project root:

LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_AGENT_NAME=improv-agent

AI Service APIs
GOOGLE_API_KEY=your_google_gemini_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
MURF_API_KEY=your_murf_api_key

text

## 🚀 Usage

### Start the Improv Host

cd backend
python improv_agent.py dev

text

You should see:
✅ Loaded 15 improv scenarios
✅ VAD Loaded
INFO: registered worker (improv-agent)

text

### Start the Frontend

cd frontend
npm run dev

text

Visit `http://localhost:3000` and enter your stage name to begin!

## 📂 Project Structure

Murf-Day10/
├── backend/
│ ├── improv_agent.py # Main AI host agent
│ ├── scenarios.json # 15 improv scenarios database
│ └── requirements.txt
├── frontend/
│ ├── app/
│ │ ├── api/
│ │ │ └── connection-details/
│ │ ├── page.tsx # Game UI with transcript
│ │ └── layout.tsx
│ ├── components/
│ └── hooks/
└── .env.local # Environment variables (not committed)

text

## 🎯 Game State Management

### State Object:

improv_state = {
"player_name": "Comedy King",
"current_round": 2,
"max_rounds": 4,
"rounds": [
{
"round_number": 1,
"scenario": "You are a barista...",
"host_reaction": "That was brilliant!"
}
],
"phase": "awaiting_improv", # intro | awaiting_improv | reacting | done
"used_scenario_ids":
}

text

### Function Tools:

@function_tool
async def start_improv_round(context: RunContext):
"""Start a new round with random scenario"""

@function_tool
async def record_host_reaction(context: RunContext, reaction: str):
"""Save host's reaction to player performance"""

@function_tool
async def end_improv_show(context: RunContext):
"""End show and prepare summary"""

text

## 🎨 UI Features

### Landing Page:
- 🎭 Dramatic animated title with gradient
- 📋 Clear game rules (4 steps)
- 🎤 Stage name input field
- 🎬 Bouncing "START" button
- ⚠️ Fun disclaimer

### In-Game Interface:
- 🔴 **Live Indicator** - Pulsing red "LIVE" badge
- 🎭 **Player Display** - Shows stage name prominently
- 🛑 **Stop Button** - Red emergency stop control
- 💬 **Transcript Box** - Real-time conversation log with color coding:
  - 🎭 Purple: Host messages
  - 🎤 Green: Your messages
  - ℹ️ Blue: System messages
- 📢 **Quick Tips** - Reminders for gameplay
- 💡 **Pro Tip** - Performance suggestions
- ⏰ **Timestamps** - Track conversation timing

### Color Scheme:
- **Background**: Purple → Pink → Red gradient
- **Accents**: Yellow, white borders
- **Host messages**: Purple
- **Player messages**: Green
- **System**: Blue

## 🧪 Testing

### Test Session Example:

[System] 🎭 Connected to IMPROV BATTLE! The host will greet you shortly...

[Host] WELCOME to IMPROV BATTLE! I'm your host Alicia! What's your name?

[You] I'm Alex

[Host] ALEX! Perfect! We're doing 4 quick improv scenes. I'll give you a scenario, you act it out, I'll react. Ready to make me laugh?

[Host] Round 1 of 4: You are a time-travelling tour guide explaining modern smartphones to someone from the 1800s. And... ACTION!

[You] performs for 30 seconds

[Host] Not bad! Though you could've really played up the confusion more. The person from 1800 would be FREAKING OUT!

[Host] Round 2! You are a restaurant waiter who must calmly tell a customer that their order has escaped the kitchen. GO!

...continues for 4 rounds...

[Host] That's a wrap, Alex! You brought ENERGY to every scene. You're definitely a high-commitment improviser. That escaped order scene was my favorite - the way you stayed so calm was perfect! Thanks for playing IMPROV BATTLE!

text

## 💡 Key Learnings

1. **Voice Acting Works** - People naturally commit to characters when using voice
2. **Varied Reactions Matter** - Not every reaction should be positive; honesty makes it real
3. **Pacing is Critical** - 4 rounds × 2 minutes = perfect 8-minute game
4. **Scenario Quality** - Clear, absurd scenarios work best ("cursed object return")
5. **Visual Feedback** - Transcript box helps players see what was understood
6. **Energy Management** - High-energy host voice (Alicia) sets the right tone

## 🎭 Host Personality Design

The AI host is designed to be:

### Personality Traits:
- **Enthusiastic** - High energy, exclamation points, emojis
- **Honest** - Not afraid to say "that was a bit flat"
- **Supportive** - Constructive criticism, not mean
- **Quick** - Fast-paced, keeps momentum
- **Funny** - Uses humor and references

### Reaction Variety:

**Great Performance:**
- "STOP. THAT WAS INCREDIBLE!"
- "Someone get this person a Netflix special!"

**Good Performance:**
- "Ha! That was brilliant, especially when you..."
- "Okay okay, I did NOT see that coming!"

**Mediocre Performance:**
- "Not bad! Though you could've leaned into the [aspect] more"
- "I see what you were going for, but the energy felt flat"

**Weak Performance:**
- "Ehhh, that felt rushed. You had a good setup but didn't commit"
- "I'm not sure you understood the scenario, but points for trying!"

## 🚧 Future Enhancements

- [ ] Multi-player mode (2 players take turns)
- [ ] Difficulty levels (easy/medium/hard scenarios)
- [ ] Score/points system
- [ ] Leaderboard with best performers
- [ ] Custom scenario upload
- [ ] Record and replay performances
- [ ] Share highlights on social media
- [ ] Different host personalities (serious, absurd, supportive)
- [ ] Team improv modes
- [ ] Audience voting system
- [ ] Weekly improv challenges
- [ ] Achievement badges

## 🙏 Acknowledgments

- Built for the **Murf AI 10 Days of Voice Agents Challenge - Day 10**
- Powered by [LiveKit Agents](https://github.com/livekit/agents)
- Voice by [Murf AI Falcon](https://murf.ai) (Alicia)
- Challenge details: [Murf AI GitHub](https://github.com/murf-ai/ten-days-of-voice-agents-2025)

## 📧 Contact

Built by Mohar Ganguly | [GitHub](https://github.com/yourusername) | [LinkedIn](https://linkedin.com/in/yourprofile)

---

⭐ If you enjoyed this, please star the repo!

## 📄 License

MIT License

---

**Ready to improvise?**

Start the Host
cd backend && python improv_agent.py dev

Start the UI
cd frontend && npm run dev

text

**Break a leg!** 🎭✨🎤
