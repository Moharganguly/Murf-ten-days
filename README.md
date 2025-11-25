# Day 4 - Teach-the-Tutor: Active Recall Coach 🎓

A multi-agent voice AI system built with LiveKit Agents that helps users learn programming concepts through active recall using three distinct learning modes.

## Overview

This project is part of the **Murf AI 10 Days of Voice Agents Challenge**. It demonstrates agent handoffs and mode-based learning with voice interaction.

### Learning Modes

- **Learn Mode** 📖 - The agent (Matthew) explains programming concepts clearly with examples
- **Quiz Mode** ❓ - The agent (Alicia) tests your knowledge with questions and provides feedback  
- **Teach Back Mode** 🗣️ - You explain concepts to the agent (Ken) who evaluates your understanding

### Available Topics

- Variables
- Loops  
- Functions

## Features

✅ **Voice-based interaction** using Deepgram STT and Cartesia TTS  
✅ **Multi-agent architecture** with seamless mode switching  
✅ **Dynamic instructions** that adapt to each learning mode  
✅ **Tool-based architecture** with function calling  
✅ **Content management** via JSON configuration  
✅ **Real-time feedback** and evaluation

## Architecture

The project uses LiveKit Agents 1.3.3 with:
- **STT**: Deepgram Nova-2
- **LLM**: OpenAI GPT-4o-mini
- **TTS**: Cartesia (multiple voices)
- **Tools**: 7 function tools for content retrieval and mode switching

## Project Structure

Murf-Day2/backend/
├── src/
│ └── agent.py # Main agent code
├── shared-data/
│ └── day4_tutor_content.json # Learning content
├── .env.local # API keys (not committed)
├── pyproject.toml # Dependencies
└── README.md # This file

text

## Prerequisites

- Python 3.10+
- LiveKit Cloud account
- API keys for:
  - LiveKit
  - OpenAI
  - Deepgram
  - Cartesia

## Installation

1. **Clone the repository**
git clone <your-repo-url>
cd Murf-Day2/backend

text

2. **Install dependencies**
uv sync

or with pip: pip install -r requirements.txt
text

3. **Configure environment variables**

Create a `.env.local` file:
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

OPENAI_API_KEY=your-openai-key
DEEPGRAM_API_KEY=your-deepgram-key
CARTESIA_API_KEY=your-cartesia-key

text

## Running the Agent

### Development Mode

uv run python src/agent.py dev

text

The agent will:
1. Start a worker process
2. Register with LiveKit Cloud
3. Wait for user connections
4. Create an agent instance for each session

### Connect to Your Agent

Use the [LiveKit Agents Playground](https://agents-playground.livekit.io/) or build your own frontend to connect to the agent.

## Usage

1. **Start a conversation**: The greeter explains the three modes
2. **Choose a mode**: Say "I want to learn about variables" or "Quiz me on loops"
3. **Switch modes anytime**: Say "Switch to quiz mode" or "Go back to menu"
4. **Learn by teaching**: In Teach Back mode, explain concepts and get feedback

### Example Interactions

**Learn Mode:**
User: "Teach me about variables"
Agent: [Explains variables with examples and analogies]

text

**Quiz Mode:**
User: "Quiz me on loops"
Agent: "Great! What's the difference between a for loop and a while loop?"

text

**Teach Back Mode:**
User: "Let me explain functions to you"
Agent: "Perfect! Go ahead and teach me about functions."
User: [Explains functions]
Agent: [Provides detailed feedback on accuracy and clarity]

text

## Customization

### Adding New Concepts

Edit `shared-data/day4_tutor_content.json`:

{
"id": "arrays",
"title": "Arrays",
"summary": "Arrays are...",
"sample_question": "What is an array?"
}

text

### Modifying Instructions

Update the `get_instructions_for_mode()` function in `agent.py` to customize agent behavior for each mode.

### Changing Voices

Modify the `VOICES` dictionary in the entrypoint to use different Cartesia voice IDs.

## Technical Details

### Agent Architecture

- **Agent Class**: Defines instructions and tools
- **AgentSession**: Manages STT, LLM, and TTS pipeline
- **Function Tools**: 7 tools with `@function_tool()` decorator
- **Mode Tracking**: Global state for current learning mode

### Tools Available

1. `get_concept_info()` - Retrieve concept details
2. `get_quiz_question()` - Get quiz questions
3. `get_reference_material()` - Get evaluation reference
4. `switch_to_learn_mode()` - Switch to Learn
5. `switch_to_quiz_mode()` - Switch to Quiz
6. `switch_to_teachback_mode()` - Switch to Teach Back
7. `return_to_menu()` - Return to greeter

## Troubleshooting

**Agent not starting:**
- Check all API keys are set correctly
- Verify LiveKit URL format (wss://...)
- Ensure dependencies are installed

**No voice output:**
- Verify Cartesia API key
- Check audio permissions in browser
- Test with LiveKit Agents Playground

**Tools not working:**
- Ensure `@function_tool()` decorator is used
- Verify `RunContext` parameter in tool functions
- Check tool names match LLM calls

## Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [Tool Definition Guide](https://docs.livekit.io/agents/build/tools/)
- [Agent Handoffs](https://docs.livekit.io/agents/build/agents-handoffs/)
- [Murf AI Challenge](https://murf.ai/falcon)

## License

MIT

## Acknowledgments

Built as part of the **Murf AI 10 Days of Voice Agents Challenge** using LiveKit Agents framework.
