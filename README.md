# 🎲 Voice Game Master - D&D Adventure Agent

An immersive voice-powered Dungeon Master that runs interactive D&D-style adventures in a fantasy world. Players speak their actions and the AI Game Master responds with dramatic narration, creating a unique story experience every time. Built for the Murf AI 10 Days of Voice Agents Challenge - Day 8.

## 🌟 Features

- **🎭 Dynamic Storytelling** - AI-generated adventures that adapt to player choices
- **🗣️ Voice-Only Gameplay** - Complete D&D experience through voice commands
- **🐉 Fantasy World (Eldoria)** - Rich setting with magic, dragons, and ancient ruins
- **🎯 Player Agency** - Accept any reasonable action with creative outcomes
- **💾 Story Continuity** - Remembers player name, choices, inventory, and NPC interactions
- **⚔️ Interactive Elements** - Combat, puzzles, NPCs, and quest progression
- **🎬 Dramatic Narration** - Powered by Murf AI Ken voice for theatrical storytelling
- **📖 8-15 Turn Adventures** - Complete story arcs with satisfying conclusions

## 🎮 How It Works

### Sample Adventure Flow:

**Game Master:** "Welcome, brave adventurer! You stand at the edge of Whispering Woods, where ancient magic still lingers in the misty air. The village elder has summoned you with urgent news. What is your name, hero?"

**Player:** "I'm Aldric"

**Game Master:** "Well met, Aldric! The elder's weathered face shows deep concern. 'The Crystal of Eternity has been stolen by shadow creatures from the Dark Caverns. Without it, our village will fall into eternal darkness!' He points a trembling finger toward the forest. What do you do?"

**Player:** "I accept the quest and ask for a weapon"

**Game Master:** "The elder nods and hands you an ancient silver sword, its blade gleaming with faint runes. 'This belonged to my grandfather. May it serve you well, Aldric.' You feel its weight in your hands. The forest entrance looms before you. What do you do?"

**Player:** "I enter the forest cautiously"

**Game Master:** "As you step into Whispering Woods, the trees seem to close in around you. Strange whispers echo through the branches. Suddenly, you hear a growl - a shadow wolf emerges from the mist, its eyes glowing red! What do you do?"

**Player:** "I fight it with my sword"

**Game Master:** "You swing the ancient blade! The runes flare with silver light as it connects. The shadow wolf howls and dissolves into mist. Your blade hums with power. The path ahead clears, leading deeper into the woods. What do you do?"

*...and the adventure continues for 8-15 exchanges...*

## 🏗️ Architecture

Player Voice → LiveKit Cloud → Game Master Agent
↓
┌───────────────┴──────────────┐
↓ ↓ ↓
Deepgram STT Gemini AI Murf Ken TTS
↓ ↓ ↓
└───────────────┬──────────────┘
↓
Adventure State Management
(Name, Location, Inventory, Turns)

text

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- LiveKit Agents SDK
- Murf AI Falcon (Ken voice - dramatic narration)
- Deepgram Nova-2 (Speech-to-Text)
- Google Gemini 2.0 (Creative storytelling)
- Silero VAD (Voice Activity Detection)

**Frontend:**
- Next.js 14+ (App Router)
- TypeScript
- LiveKit React Components
- TailwindCSS

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
LIVEKIT_AGENT_NAME=game-master

AI Service APIs
GOOGLE_API_KEY=your_google_gemini_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
MURF_API_KEY=your_murf_api_key

text

## 🚀 Usage

### Start the Game Master

cd backend
python game_master.py dev

text

### Start the Frontend

cd frontend
npm run dev

text

Visit `http://localhost:3000`, click "Connect", and begin your adventure!

## 📂 Project Structure

Murf-Day8/
├── backend/
│ ├── game_master.py # Main Game Master AI agent
│ └── requirements.txt
├── frontend/
│ ├── app/
│ │ ├── api/
│ │ │ └── connection-details/
│ │ └── page.tsx
│ ├── components/
│ └── hooks/
└── .env.local # Environment variables (not committed)

text

## 🎯 Game Master Capabilities

### Story Elements:

- **Opening Hook** - Sets the scene and asks for player's character name
- **Quest Introduction** - Village elder or NPC provides the main quest
- **Exploration** - Navigate through Whispering Woods and beyond
- **Combat Encounters** - Fight shadow creatures, wolves, or guardians
- **NPCs** - Meet helpful villagers, mysterious travelers, or quest givers
- **Puzzles** - Solve riddles or navigate ancient ruins
- **Discovery** - Find magical items, hidden paths, or quest objectives
- **Conclusion** - Satisfying resolution with rewards and recognition

### Player Actions Supported:

| Action Type | Examples |
|-------------|----------|
| Movement | "I enter the forest", "I go north", "I climb the mountain" |
| Combat | "I attack with my sword", "I defend", "I cast a spell" |
| Investigation | "I search the area", "I examine the statue", "I look around" |
| Social | "I talk to them", "I ask for help", "I negotiate" |
| Inventory | "I take it", "I use the potion", "Check my inventory" |
| Creative | "I try to sneak past", "I set a trap", "I climb the wall" |

## 🎭 Game Master Features

### 1. Adaptive Storytelling
GM responds dynamically to player choices
Player: "I try to befriend the wolf"
GM: "You speak softly. The wolf's eyes soften. It sniffs your hand..."

text

### 2. Memory & Continuity
adventure_state = {
"player_name": "Aldric",
"location": "Dark Forest",
"inventory": ["Ancient Sword", "Healing Potion"],
"turn_count": 7
}

text

### 3. Tools Integration
@function_tool
async def add_to_inventory(context: RunContext, item: str):
"""Track items player finds"""

@function_tool
async def check_inventory(context: RunContext):
"""Show what player is carrying"""

text

## 🌍 Setting: Eldoria

**Fantasy World Elements:**
- **Whispering Woods** - Ancient forest where magic lingers
- **Village of Eldoria** - Starting location with quest-giving elder
- **Dark Caverns** - Dangerous dungeon where the Crystal is hidden
- **Crystal of Eternity** - Legendary artifact that brings prosperity
- **Shadow Creatures** - Enemies that stole the Crystal

**Tone:** Dramatic, immersive, with moments of danger and wonder

## 🎨 Alternative Themes

The agent can be easily adapted to other genres:

### Sci-Fi (Mars Survival)
instructions = """
You are Mission Control AI running a survival adventure on Mars Colony Alpha.
Player is an engineer trying to survive after losing contact with Earth.
Tone: Tense, mysterious, hopeful.
"""

text

### Horror (Haunted Mansion)
instructions = """
You are the narrator of a gothic horror story in Blackwood Manor.
Player is investigating paranormal activity.
Tone: Spooky, atmospheric, suspenseful.
"""

text

### Cyberpunk (Neo-Tokyo)
instructions = """
You are an AI guide in a cyberpunk Neo-Tokyo.
Player is a hacker uncovering corporate conspiracies.
Tone: Gritty, neon-lit, tech-noir.
"""

text

## 🧪 Testing

### Test Adventure Path:

1. **Connect** → GM greets and asks for name
2. **Give name** → "I'm [Name]"
3. **Receive quest** → "I accept the quest"
4. **Enter location** → "I enter the forest"
5. **Encounter challenge** → "I fight it" or "I investigate"
6. **Make progress** → Continue responding to prompts
7. **Reach conclusion** → Complete mini-arc after 8-15 turns

### Example Session Log:

Turn 1: Player introduces self → "I'm Thorin"
Turn 2: Quest received → "I ask for a weapon"
Turn 3: Enter forest → "I go into the woods"
Turn 4: Combat encounter → "I attack the wolf"
Turn 5: Victory → "I continue forward"
Turn 6: Meet NPC → "I talk to the old woman"
Turn 7: Receive item → "I take the magical token"
Turn 8: Final challenge → "I use the token"
Turn 9: Resolution → Quest complete!

text

## 💡 Key Learnings

1. **Voice-First Design** - D&D works perfectly with voice because it's traditionally oral storytelling
2. **Prompt Engineering** - Clear GM instructions create consistent, engaging narratives
3. **Player Agency** - Accepting creative actions makes players feel empowered
4. **Pacing** - 8-15 turns is ideal for a complete mini-adventure
5. **Dramatic Voice** - Ken's voice adds theatrical quality to narration
6. **Memory Management** - Remembering names and choices builds immersion

## 🚧 Future Enhancements

- [ ] Multiple campaign settings (sci-fi, horror, mystery)
- [ ] Persistent character stats (HP, strength, magic)
- [ ] Dice rolling for combat outcomes
- [ ] Party play (multiple players)
- [ ] Campaign continuity (save/load adventures)
- [ ] Visual character sheets in UI
- [ ] Sound effects and ambient music
- [ ] Achievement system
- [ ] DM personality options (serious, humorous, etc.)

## 🙏 Acknowledgments

- Built for the **Murf AI 10 Days of Voice Agents Challenge - Day 8**
- Powered by [LiveKit Agents](https://github.com/livekit/agents)
- Voice by [Murf AI Falcon](https://murf.ai)
- Challenge details: [Murf AI GitHub](https://github.com/murf-ai/ten-days-of-voice-agents-2025)

## 📧 Contact

Built by Mohar Ganguly | [GitHub](https://github.com/yourusername) | [LinkedIn](https://linkedin.com/in/yourprofile)

---

⭐ If you enjoyed this adventure, please star the repo!

## 📄 License

MIT License

---

**Ready to embark on your voice-powered D&D adventure?**

Start the Game Master
cd backend && python game_master.py dev

Start the Frontend
cd frontend && npm run dev

text

**Roll for initiative!** 🎲⚔️✨
