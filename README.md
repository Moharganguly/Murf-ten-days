🚨 AI Fraud Alert Voice Agent
An intelligent voice agent that detects suspicious transactions and verifies them with customers in real-time. Built for the Murf AI 10 Days of Voice Agents Challenge - Day 6.

🌟 Features
🔍 Fraud Detection - Automatically identifies suspicious transactions from database

🗣️ Natural Voice Alerts - Uses Murf AI Falcon TTS for trustworthy, human-like conversations

🔐 Secure Verification - Validates customer identity with security questions

💳 Transaction Review - Reads detailed transaction information (amount, merchant, location, time)

⚡ Real-time Updates - Updates database instantly based on customer confirmation

🎯 Smart Decision Flow - Marks transactions as safe or fraudulent based on customer response

🚫 Auto Card Blocking - Immediately blocks compromised cards when fraud is confirmed

🎬 How It Works
Sample Conversation Flow:
Agent: "Hello, this is the SecureBank Fraud Prevention Department. We've detected a suspicious transaction on your account and need to verify it with you."

Customer: "Okay, what's going on?"

Agent: "May I have your full name please?"

Customer: "John Smith"

Agent: "What is your mother's maiden name?"

Customer: "Johnson"

Agent: "Thank you. We detected a transaction of $1,299.99 to ABC Electronics Ltd in Shanghai, China at 2:45 AM. Did you authorize this transaction?"

Customer: "No, I didn't make that purchase!"

Agent: "I've immediately blocked your card ending in 8888 and initiated a dispute for this transaction. You will receive a replacement card within 5-7 business days."

🏗️ Architecture
text
User Call → LiveKit Cloud → Python Fraud Agent
                                    ↓
                    ┌───────────────┴──────────────┐
                    ↓               ↓              ↓
              Deepgram STT    Gemini LLM    Murf Falcon TTS
                    ↓               ↓              ↓
                    └───────────────┬──────────────┘
                                    ↓
                              SQLite Database
                           (Fraud Cases Storage)
🛠️ Tech Stack
Backend:

Python 3.12+

LiveKit Agents SDK

Murf AI Falcon (Text-to-Speech)

Deepgram Nova-2 (Speech-to-Text)

Google Gemini 2.0 (LLM)

SQLite3 (Database)

Silero VAD (Voice Activity Detection)

Frontend:

Next.js 14+ (App Router)

TypeScript

LiveKit React Components

TailwindCSS

📦 Installation
Prerequisites
Python 3.12 or higher

Node.js 18+ and npm/pnpm

LiveKit Cloud account

API keys for: Murf AI, Deepgram, Google Gemini

Backend Setup
bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt
Frontend Setup
bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
pnpm install
Environment Configuration
Create a .env.local file in the project root:

text
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_AGENT_NAME=fraud-agent

# AI Service APIs
GOOGLE_API_KEY=your_google_gemini_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
MURF_API_KEY=your_murf_api_key
🚀 Usage
Start the Fraud Alert Agent
bash
cd backend
python fraud_agent.py dev
Start the Frontend
bash
cd frontend
npm run dev
Visit http://localhost:3000 and click "Connect" to start the fraud alert call!
