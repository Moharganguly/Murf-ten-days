# 🎙️ Murf AI Voice Agent - SDR Lead Capture System

A fully functional AI-powered Sales Development Representative (SDR) voice agent built with Murf AI Falcon TTS, LiveKit, Deepgram STT, and Google Gemini. This intelligent voice agent answers FAQs, captures lead information, and saves qualified leads automatically.

## 🌟 Features

- **🗣️ Natural Voice Conversations** - Uses Murf AI Falcon TTS for realistic, human-like voice interactions
- **👂 Real-time Speech Recognition** - Deepgram Nova-2 for accurate speech-to-text conversion
- **🧠 Intelligent Responses** - Powered by Google Gemini 2.0 for contextual understanding
- **📋 FAQ Search** - Automated FAQ lookup with keyword-based scoring algorithm
- **💾 Lead Capture** - Automatically captures and stores lead information (Name, Email, Company, Use Case)
- **🎯 Voice Activity Detection** - Silero VAD for natural conversation flow
- **☁️ Cloud Deployment Ready** - Fully configured for LiveKit Cloud

## 🏗️ Architecture

Frontend (Next.js) → LiveKit Cloud → Python Voice Agent
↓
┌─────────────┴─────────────┐
↓ ↓ ↓
Deepgram STT Gemini LLM Murf Falcon TTS

text

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- LiveKit Agents SDK
- Murf AI Falcon (Text-to-Speech)
- Deepgram Nova-2 (Speech-to-Text)
- Google Gemini 2.0 (LLM)
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

Install dependencies (using uv - recommended)
uv pip install -r requirements.txt

Or using pip
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
LIVEKIT_AGENT_NAME=sdr-agent

AI Service APIs
GOOGLE_API_KEY=your_google_gemini_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
MURF_API_KEY=your_murf_api_key

text

## 🚀 Usage

### Start the Voice Agent

cd backend
python sdr_agent.py dev

text

### Start the Frontend

cd frontend
npm run dev

text

Visit `http://localhost:3000` and click "Connect" to start talking with your AI voice agent!

## 💡 How It Works

1. **User connects** through the web interface
2. **Agent greets** the user with Murf AI's natural voice
3. **User asks questions** - Agent searches FAQ database and responds
4. **Lead qualification** - Agent collects Name, Email, Company, and Use Case
5. **Data storage** - Lead information saved to `leads/` directory as JSON

## 📂 Project Structure

Murf-Day2/
├── backend/
│ ├── sdr_agent.py # Main agent logic
│ ├── shared_data/
│ │ └── razorpay_faq.json # FAQ database
│ └── leads/ # Saved lead data
├── frontend/
│ ├── app/
│ │ ├── api/
│ │ │ └── connection-details/ # LiveKit token endpoint
│ │ └── page.tsx
│ ├── components/
│ │ └── app/
│ │ ├── session-provider.tsx
│ │ └── view-controller.tsx
│ └── hooks/
│ └── useRoom.ts # LiveKit room connection
└── .env.local # Environment variables (not committed)

text

## 🎯 Key Functions

### Agent Tools

- `save_lead_field()` - Captures individual lead information fields
- `search_company_faq()` - Searches FAQ database with keyword scoring
- `complete_call_and_save_lead()` - Finalizes and saves lead data

## 🔒 Security Notes

- Never commit `.env.local` or `.env` files to version control
- Rotate API keys regularly
- Use environment variables for production deployments

## 📝 License

MIT License

## 🙏 Acknowledgments

- Built for the **Murf AI 10 Days of Voice Agents Challenge**
- Powered by [LiveKit Agents](https://github.com/livekit/agents)
- Voice by [Murf AI Falcon](https://murf.ai)

## 📧 Contact

Built by [Your Name] | [GitHub](https://github.com/yourusername) | [LinkedIn](https://linkedin.com/in/yourprofile)

---

⭐ If you found this helpful, please star the repo!
