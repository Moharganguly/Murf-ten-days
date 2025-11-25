#!/usr/bin/env python3
"""
Day 4 - Teach-the-Tutor: Active Recall Coach
Multi-agent system with Learn, Quiz, and Teach Back modes
LiveKit Agents 1.3.3 - TRUE FINAL WORKING VERSION
"""

import logging
import json
import os
import sys
from typing import Annotated
from dotenv import load_dotenv

# LiveKit core
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
)
from livekit.plugins import openai, deepgram, cartesia, silero

# Setup logging
logger = logging.getLogger("teach-tutor-agent")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Setup directories
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT, "shared-data")
os.makedirs(DATA_DIR, exist_ok=True)

# Content file
CONTENT_FILE = os.path.join(DATA_DIR, "day4_tutor_content.json")

print("\n" + "🎓" * 15)
print("📚 TEACH-THE-TUTOR: ACTIVE RECALL COACH - DAY 4")
print(f"📁 Content file: {CONTENT_FILE}")
print("🎓" * 15 + "\n")


# ---------------------------
# Content Data Manager
# ---------------------------
class ContentLoader:
    """Manages loading and accessing tutor content"""

    def __init__(self, content_path: str = CONTENT_FILE):
        self.content_path = content_path
        self.concepts = []
        self._ensure_content_exists()
        self.load_content()

    def _ensure_content_exists(self):
        """Create default content file if it doesn't exist"""
        if not os.path.exists(self.content_path):
            default_content = [
                {
                    "id": "variables",
                    "title": "Variables",
                    "summary": "Variables are containers that store values in programming. They allow you to save data like numbers, text, or complex objects, and reuse them throughout your code. Think of a variable as a labeled box where you can put information and retrieve it later by using its name.",
                    "sample_question": "What is a variable and why is it useful in programming?"
                },
                {
                    "id": "loops",
                    "title": "Loops",
                    "summary": "Loops are programming constructs that let you repeat actions multiple times without writing the same code over and over. A for loop is used when you know how many times you want to repeat something, like counting from 1 to 10. A while loop continues repeating as long as a certain condition remains true, useful when you don't know exactly how many iterations you need.",
                    "sample_question": "Explain the difference between a for loop and a while loop."
                },
                {
                    "id": "functions",
                    "title": "Functions",
                    "summary": "Functions are reusable blocks of code that perform specific tasks. They help organize your code, make it more readable, and avoid repetition. Functions can accept inputs called parameters and return outputs. This makes your code modular and easier to maintain.",
                    "sample_question": "What is a function and what are its main benefits?"
                }
            ]
            with open(self.content_path, 'w') as f:
                json.dump(default_content, f, indent=2)
            logger.info(f"✅ Created default content file at {self.content_path}")

    def load_content(self):
        """Load concepts from JSON file"""
        try:
            with open(self.content_path, 'r') as f:
                self.concepts = json.load(f)
            logger.info(f"✅ Loaded {len(self.concepts)} concepts from content file")
        except Exception as e:
            logger.error(f"❌ Failed to load content: {e}")
            self.concepts = []

    def get_all_concepts(self):
        """Return all concepts"""
        return self.concepts

    def get_concept(self, concept_id: str):
        """Get a specific concept by ID"""
        for concept in self.concepts:
            if concept['id'] == concept_id:
                return concept
        return None

    def get_concept_titles(self):
        """Get formatted list of all concept titles"""
        return ", ".join([c['title'] for c in self.concepts])

    def get_concept_ids(self):
        """Get list of concept IDs"""
        return [c['id'] for c in self.concepts]


# Global content loader
content_loader = ContentLoader()

# Current mode tracker
current_mode = {"mode": "greeter"}


# ---------------------------
# Instructions for Each Mode
# ---------------------------
def get_instructions_for_mode(mode: str) -> str:
    """Get system instructions based on current mode"""

    available_concepts = content_loader.get_concept_titles()

    if mode == "learn":
        return f"""You are Matthew, an expert teacher in Learn mode.
Your role is to explain programming concepts clearly and thoroughly.

Available topics: {available_concepts}

Your approach:
- When the user asks about a concept, use get_concept_info() to retrieve the material
- Explain concepts using clear language and real-world analogies
- Break down complex ideas into digestible parts
- Use examples to illustrate key points
- Check for understanding before moving on
- Keep explanations concise (2-3 minutes per concept)

The user can switch modes anytime by asking.

Remember: You're teaching, so be clear, thorough, and supportive."""

    elif mode == "quiz":
        return f"""You are Alicia, an encouraging quiz master in Quiz mode.
Your role is to test the user's understanding with thoughtful questions.

Available topics: {available_concepts}

Your approach:
- When ready to quiz, use get_quiz_question() to get the reference question
- Ask clear, focused questions in an engaging way
- Listen carefully to their answers
- Provide constructive, specific feedback
- Praise correct answers enthusiastically
- For incorrect answers, gently explain the right concept
- Ask follow-up questions to deepen understanding

The user can switch modes anytime by asking.

Remember: You're testing knowledge, but stay encouraging and supportive!"""

    elif mode == "teachback":
        return f"""You are Ken, a patient and thoughtful listener in Teach Back mode.
Your role is to listen to the user explain concepts and provide helpful feedback.

Available topics: {available_concepts}

Your approach:
- Prompt the user to explain a concept in their own words
- Listen actively and attentively to their full explanation
- After they finish, use get_reference_material() to retrieve the correct information
- Provide specific, constructive feedback on accuracy, clarity, completeness
- Always start with what they did well
- Gently point out any gaps or misconceptions
- Encourage them to elaborate on unclear points

The user can switch modes anytime by asking.

Remember: Your goal is to help them learn by teaching!"""

    else:  # greeter
        return f"""You are a friendly learning assistant that helps users choose their learning mode.

Available learning modes:
- LEARN: You explain concepts to them (call switch_to_learn_mode)
- QUIZ: You test their knowledge (call switch_to_quiz_mode)
- TEACH_BACK: They explain concepts to you (call switch_to_teachback_mode)

Available topics: {available_concepts}

Your role:
1. Greet the user warmly and explain the three modes briefly
2. Ask which mode they'd like to start with
3. Once they choose, use the appropriate switch function

Keep your greeting brief and engaging. Let them know they can switch modes anytime."""


# ---------------------------
# Define Tools Outside of Agent Class
# ---------------------------
@function_tool()
async def get_concept_info(
    context: RunContext,
    concept_id: Annotated[str, "The ID of the concept. Options: variables, loops, functions"]
):
    """Retrieve information about a specific programming concept for teaching"""
    concept = content_loader.get_concept(concept_id)
    if concept:
        logger.info(f"📖 Retrieved concept: {concept['title']}")
        return f"Concept: {concept['title']}\n\nReference: {concept['summary']}\n\nUse this as a foundation but explain in your own engaging way with examples."
    return "Concept not found. Available concepts: " + content_loader.get_concept_titles()


@function_tool()
async def get_quiz_question(
    context: RunContext,
    concept_id: Annotated[str, "The ID of the concept to quiz on. Options: variables, loops, functions"]
):
    """Get a quiz question for a specific concept"""
    concept = content_loader.get_concept(concept_id)
    if concept:
        logger.info(f"❓ Quiz question for: {concept['title']}")
        return f"Concept: {concept['title']}\n\nSample Question: {concept['sample_question']}\n\nReference Answer: {concept['summary']}\n\nAsk the question engagingly, then evaluate their answer against the reference."
    return "Concept not found. Available concepts: " + content_loader.get_concept_titles()


@function_tool()
async def get_reference_material(
    context: RunContext,
    concept_id: Annotated[str, "The ID of the concept being explained. Options: variables, loops, functions"]
):
    """Get reference material to evaluate user's explanation"""
    concept = content_loader.get_concept(concept_id)
    if concept:
        logger.info(f"📋 Retrieved reference for: {concept['title']}")
        return f"Concept: {concept['title']}\n\nReference: {concept['summary']}\n\nCompare the user's explanation to this. Highlight what they got right, what they missed, and how clear their explanation was."
    return "Concept not found. Available concepts: " + content_loader.get_concept_titles()


@function_tool()
async def switch_to_learn_mode(context: RunContext):
    """Switch to Learn mode where the agent explains concepts"""
    logger.info("🔄 Switching to Learn mode")
    current_mode["mode"] = "learn"
    return "Switched to Learn mode! I'll explain programming concepts to you. Which topic would you like to learn about: Variables, Loops, or Functions?"


@function_tool()
async def switch_to_quiz_mode(context: RunContext):
    """Switch to Quiz mode where the agent tests your knowledge"""
    logger.info("🔄 Switching to Quiz mode")
    current_mode["mode"] = "quiz"
    return "Switched to Quiz mode! I'll test your knowledge. Which topic would you like to be quizzed on: Variables, Loops, or Functions?"


@function_tool()
async def switch_to_teachback_mode(context: RunContext):
    """Switch to Teach Back mode where you explain concepts"""
    logger.info("🔄 Switching to Teach Back mode")
    current_mode["mode"] = "teachback"
    return "Switched to Teach Back mode! Now you'll teach me. Which concept would you like to explain: Variables, Loops, or Functions?"


@function_tool()
async def return_to_menu(context: RunContext):
    """Return to the main menu"""
    logger.info("🔄 Returning to main menu")
    current_mode["mode"] = "greeter"
    return "Returning to main menu. Which learning mode would you like to try: Learn, Quiz, or Teach Back?"


# ---------------------------
# Main Entrypoint
# ---------------------------
async def entrypoint(ctx: JobContext):
    """Main entry point for the teach-tutor agent"""
    logger.info("=" * 60)
    logger.info("🎓 NEW TEACH-TUTOR SESSION STARTED")
    logger.info("Room: %s", ctx.room.name)
    logger.info("=" * 60)

    # Initialize with greeter mode
    current_mode["mode"] = "greeter"
    initial_instructions = get_instructions_for_mode("greeter")

    # Create agent with tools
    assistant = Agent(
        instructions=initial_instructions,
        tools=[
            get_concept_info,
            get_quiz_question,
            get_reference_material,
            switch_to_learn_mode,
            switch_to_quiz_mode,
            switch_to_teachback_mode,
            return_to_menu,
        ]
    )

    # Create the session with plugins
    session = AgentSession(
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(voice="79a125e8-cd45-4c13-8a67-188112f4dd22"),
    )

    # Start the session
    await session.start(agent=assistant, room=ctx.room)

    # Initial greeting
    await session.generate_reply(
        instructions=(
            f"Greet the user warmly and introduce yourself. "
            f"Explain that we have three learning modes available: "
            f"Learn mode where you explain concepts, "
            f"Quiz mode where you test their knowledge, "
            f"and Teach Back mode where they explain concepts to you. "
            f"We have {len(content_loader.get_all_concepts())} topics: {content_loader.get_concept_titles()}. "
            f"Ask which mode they'd like to try first."
        )
    )

    logger.info("✅ Session active - agent is listening...")


# ---------------------------
# CLI Entry Point
# ---------------------------
if __name__ == "__main__":
    logger.info("🚀 Starting Teach-the-Tutor Agent...")
    logger.info("Content directory: %s", DATA_DIR)

    # Check for required API keys
    required_keys = ["OPENAI_API_KEY", "DEEPGRAM_API_KEY", "CARTESIA_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        logger.error("❌ Missing required API keys in .env.local:")
        for key in missing_keys:
            logger.error("   - %s", key)
        logger.error("Please add these keys to your .env.local file")
        sys.exit(1)

    logger.info("✅ All required API keys found")
    logger.info("Starting LiveKit worker...")

    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
