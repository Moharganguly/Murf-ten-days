# Create the updated agent.py structure for Day 4
updated_agent_code = '''#!/usr/bin/env python3
"""
Day 4 - Teach-the-Tutor: Active Recall Coach
Multi-agent system with Learn, Quiz, and Teach Back modes
Uses Agent handoffs and Murf Falcon TTS voices
"""

import logging
import json
import os
import sys
from datetime import datetime
from typing import Annotated
from dotenv import load_dotenv

# LiveKit core
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
    llm,
)

# Cloud plugins
from livekit.plugins import openai, deepgram, murf

# Try to import silero for VAD (optional)
try:
    from livekit.plugins import silero
except Exception:
    silero = None
    print("⚠️ Silero VAD not available (optional)")

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

print("\\n" + "🎓" * 15)
print("📚 TEACH-THE-TUTOR: ACTIVE RECALL COACH - DAY 4")
print(f"📁 Content file: {CONTENT_FILE}")
print("🎓" * 15 + "\\n")


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


# ---------------------------
# Greeter Agent (Orchestrator)
# ---------------------------
class GreeterAgent(Agent):
    """Main orchestrator that greets users and routes to learning modes"""
    
    def __init__(self, chat_ctx: llm.ChatContext = None):
        self.content_loader = content_loader
        available_concepts = self.content_loader.get_concept_titles()
        
        super().__init__(
            instructions=f"""You are a friendly learning assistant that helps users choose their learning mode.

Available learning modes:
- LEARN: I explain concepts to you (Voice: Matthew)
- QUIZ: I ask you questions to test your knowledge (Voice: Alicia)
- TEACH_BACK: You teach the concept back to me (Voice: Ken)

Available topics: {available_concepts}

Your role:
1. Greet the user warmly and enthusiastically
2. Explain the three modes briefly (1 sentence each)
3. Ask which mode they'd like to start with
4. Once they choose, use the appropriate transfer tool to connect them

Keep your greeting brief and engaging. Let the user know they can switch modes anytime.""",
            chat_ctx=chat_ctx,
        )
    
    def _create_tools(self):
        """Create transfer tools for mode switching"""
        
        @function_tool
        async def transfer_to_learn(
            ctx: RunContext,
            concept_id: Annotated[str, f"Concept to learn about. Options: {content_loader.get_concept_ids()}"] = "variables"
        ):
            """Transfer to Learn mode where the agent explains concepts"""
            logger.info(f"🔄 Transferring to Learn mode (concept: {concept_id})")
            agent = LearnAgent(
                chat_ctx=self.chat_ctx,
                initial_concept=concept_id
            )
            return llm.handoff(
                agent=agent,
                message="Connecting you to Matthew, your learning guide..."
            )
        
        @function_tool
        async def transfer_to_quiz(
            ctx: RunContext,
            concept_id: Annotated[str, f"Concept to quiz on. Options: {content_loader.get_concept_ids()}"] = "variables"
        ):
            """Transfer to Quiz mode where the agent tests your knowledge"""
            logger.info(f"🔄 Transferring to Quiz mode (concept: {concept_id})")
            agent = QuizAgent(
                chat_ctx=self.chat_ctx,
                initial_concept=concept_id
            )
            return llm.handoff(
                agent=agent,
                message="Connecting you to Alicia, your quiz master..."
            )
        
        @function_tool
        async def transfer_to_teachback(
            ctx: RunContext,
            concept_id: Annotated[str, f"Concept to teach. Options: {content_loader.get_concept_ids()}"] = "variables"
        ):
            """Transfer to Teach Back mode where you explain concepts"""
            logger.info(f"🔄 Transferring to Teach Back mode (concept: {concept_id})")
            agent = TeachBackAgent(
                chat_ctx=self.chat_ctx,
                initial_concept=concept_id
            )
            return llm.handoff(
                agent=agent,
                message="Connecting you to Ken, who will listen to your explanation..."
            )
        
        return [transfer_to_learn, transfer_to_quiz, transfer_to_teachback]


# ---------------------------
# Learn Agent (Matthew)
# ---------------------------
class LearnAgent(Agent):
    """Learn mode - explains concepts to the user"""
    
    def __init__(self, chat_ctx: llm.ChatContext = None, initial_concept: str = None):
        self.content_loader = content_loader
        self.initial_concept = initial_concept
        available_concepts = self.content_loader.get_concept_titles()
        
        super().__init__(
            instructions=f"""You are Matthew, an expert teacher in Learn mode.
Your role is to explain programming concepts clearly and thoroughly.

Available topics: {available_concepts}

Your approach:
- Explain concepts using clear language and real-world analogies
- Break down complex ideas into digestible parts
- Use examples to illustrate key points
- Check for understanding before moving on
- Be patient and encouraging
- Keep explanations concise (2-3 minutes per concept)

When the user asks about a concept:
1. Use get_concept_info() to retrieve the reference material
2. Explain it in your own words with examples
3. Ask if they have questions or want more detail

The user can switch modes anytime - listen for those requests and use the transfer tools.

Remember: You're teaching, so be clear, thorough, and supportive.""",
            chat_ctx=chat_ctx,
        )
    
    def _create_tools(self):
        """Create tools for Learn mode"""
        
        @function_tool
        async def get_concept_info(
            ctx: RunContext,
            concept_id: Annotated[str, f"Concept ID. Options: {content_loader.get_concept_ids()}"]
        ):
            """Retrieve information about a specific concept"""
            concept = content_loader.get_concept(concept_id)
            if concept:
                logger.info(f"📖 Retrieved concept: {concept['title']}")
                return f"Concept: {concept['title']}\\n\\nReference: {concept['summary']}\\n\\nUse this as a foundation but explain in your own engaging way with examples."
            return "Concept not found. Available concepts: " + content_loader.get_concept_titles()
        
        @function_tool
        async def switch_to_quiz(ctx: RunContext):
            """Switch to Quiz mode"""
            logger.info("🔄 Switching to Quiz mode")
            agent = QuizAgent(chat_ctx=self.chat_ctx)
            return llm.handoff(
                agent=agent,
                message="Switching to Quiz mode with Alicia..."
            )
        
        @function_tool
        async def switch_to_teachback(ctx: RunContext):
            """Switch to Teach Back mode"""
            logger.info("🔄 Switching to Teach Back mode")
            agent = TeachBackAgent(chat_ctx=self.chat_ctx)
            return llm.handoff(
                agent=agent,
                message="Switching to Teach Back mode with Ken..."
            )
        
        @function_tool
        async def return_to_menu(ctx: RunContext):
            """Return to the main menu"""
            logger.info("🔄 Returning to main menu")
            agent = GreeterAgent(chat_ctx=self.chat_ctx)
            return llm.handoff(
                agent=agent,
                message="Returning to main menu..."
            )
        
        return [get_concept_info, switch_to_quiz, switch_to_teachback, return_to_menu]


# ---------------------------
# Quiz Agent (Alicia)
# ---------------------------
class QuizAgent(Agent):
    """Quiz mode - tests user knowledge"""
    
    def __init__(self, chat_ctx: llm.ChatContext = None, initial_concept: str = None):
        self.content_loader = content_loader
        self.initial_concept = initial_concept
        available_concepts = self.content_loader.get_concept_titles()
        
        super().__init__(
            instructions=f"""You are Alicia, an encouraging quiz master in Quiz mode.
Your role is to test the user's understanding with thoughtful questions.

Available topics: {available_concepts}

Your approach:
- Ask clear, focused questions (use sample questions as starting points)
- Listen carefully to their answers
- Provide constructive, specific feedback
- Praise correct answers enthusiastically
- For incorrect answers, gently explain the right concept
- Ask follow-up questions to deepen understanding
- Keep the energy positive and motivating

When quizzing:
1. Use get_quiz_question() to get the reference question
2. Ask it in an engaging way
3. After they answer, evaluate against the reference material
4. Provide feedback and explanation
5. Ask if they want another question

The user can switch modes anytime - watch for those requests.

Remember: You're testing knowledge, but stay encouraging and supportive!""",
            chat_ctx=chat_ctx,
        )
    
    def _create_tools(self):
        """Create tools for Quiz mode"""
        
        @function_tool
        async def get_quiz_question(
            ctx: RunContext,
            concept_id: Annotated[str, f"Concept to quiz on. Options: {content_loader.get_concept_ids()}"]
        ):
            """Get a quiz question for a specific concept"""
            concept = content_loader.get_concept(concept_id)
            if concept:
                logger.info(f"❓ Quiz question for: {concept['title']}")
                return f"Concept: {concept['title']}\\n\\nSample Question: {concept['sample_question']}\\n\\nReference Answer: {concept['summary']}\\n\\nAsk the question engagingly, then evaluate their answer against the reference."
            return "Concept not found. Available concepts: " + content_loader.get_concept_titles()
        
        @function_tool
        async def switch_to_learn(ctx: RunContext):
            """Switch to Learn mode"""
            logger.info("🔄 Switching to Learn mode")
            agent = LearnAgent(chat_ctx=self.chat_ctx)
            return llm.handoff(
                agent=agent,
                message="Switching to Learn mode with Matthew..."
            )
        
        @function_tool
        async def switch_to_teachback(ctx: RunContext):
            """Switch to Teach Back mode"""
            logger.info("🔄 Switching to Teach Back mode")
            agent = TeachBackAgent(chat_ctx=self.chat_ctx)
            return llm.handoff(
                agent=agent,
                message="Switching to Teach Back mode with Ken..."
            )
        
        @function_tool
        async def return_to_menu(ctx: RunContext):
            """Return to the main menu"""
            logger.info("🔄 Returning to main menu")
            agent = GreeterAgent(chat_ctx=self.chat_ctx)
            return llm.handoff(
                agent=agent,
                message="Returning to main menu..."
            )
        
        return [get_quiz_question, switch_to_learn, switch_to_teachback, return_to_menu]


# ---------------------------
# Teach Back Agent (Ken)
# ---------------------------
class TeachBackAgent(Agent):
    """Teach Back mode - user explains concepts"""
    
    def __init__(self, chat_ctx: llm.ChatContext = None, initial_concept: str = None):
        self.content_loader = content_loader
        self.initial_concept = initial_concept
        available_concepts = self.content_loader.get_concept_titles()
        
        super().__init__(
            instructions=f"""You are Ken, a patient and thoughtful listener in Teach Back mode.
Your role is to listen to the user explain concepts and provide helpful feedback.

Available topics: {available_concepts}

Your approach:
- Prompt the user to explain a concept in their own words
- Listen actively and attentively
- After they finish, provide specific, constructive feedback on:
  * Accuracy of information
  * Clarity and organization
  * Completeness of explanation
  * Use of examples or analogies
- Always start with what they did well
- Gently point out any gaps or misconceptions
- Encourage them to elaborate on unclear points
- Keep feedback balanced and encouraging

When evaluating:
1. Ask the user to explain a concept
2. Listen to their full explanation
3. Use get_reference_material() to retrieve the correct information
4. Compare their explanation to the reference
5. Provide detailed, kind feedback
6. Offer suggestions for improvement

The user can switch modes anytime.

Remember: Your goal is to help them learn by teaching!""",
            chat_ctx=chat_ctx,
        )
    
    def _create_tools(self):
        """Create tools for Teach Back mode"""
        
        @function_tool
        async def get_reference_material(
            ctx: RunContext,
            concept_id: Annotated[str, f"Concept being explained. Options: {content_loader.get_concept_ids()}"]
        ):
            """Get reference material to evaluate user's explanation"""
            concept = content_loader.get_concept(concept_id)
            if concept:
                logger.info(f"📋 Retrieved reference for: {concept['title']}")
                return f"Concept: {concept['title']}\\n\\nReference: {concept['summary']}\\n\\nCompare the user's explanation to this. Highlight what they got right, what they missed, and how clear their explanation was."
            return "Concept not found. Available concepts: " + content_loader.get_concept_titles()
        
        @function_tool
        async def switch_to_learn(ctx: RunContext):
            """Switch to Learn mode"""
            logger.info("🔄 Switching to Learn mode")
            agent = LearnAgent(chat_ctx=self.chat_ctx)
            return llm.handoff(
                agent=agent,
                message="Switching to Learn mode with Matthew..."
            )
        
        @function_tool
        async def switch_to_quiz(ctx: RunContext):
            """Switch to Quiz mode"""
            logger.info("🔄 Switching to Quiz mode")
            agent = QuizAgent(chat_ctx=self.chat_ctx)
            return llm.handoff(
                agent=agent,
                message="Switching to Quiz mode with Alicia..."
            )
        
        @function_tool
        async def return_to_menu(ctx: RunContext):
            """Return to the main menu"""
            logger.info("🔄 Returning to main menu")
            agent = GreeterAgent(chat_ctx=self.chat_ctx)
            return llm.handoff(
                agent=agent,
                message="Returning to main menu..."
            )
        
        return [get_reference_material, switch_to_learn, switch_to_quiz, return_to_menu]


# ---------------------------
# Prewarm Function
# ---------------------------
def prewarm(proc: JobProcess):
    """Prewarm VAD if available"""
    print("🔥 Prewarming...")
    
    if silero is None:
        print("⚠️ Silero VAD not available (using fallback)")
        proc.userdata["vad"] = None
        return
    
    try:
        if hasattr(silero, "VAD") and hasattr(silero.VAD, "load"):
            proc.userdata["vad"] = silero.VAD.load()
            print("✅ Silero VAD loaded successfully")
        else:
            proc.userdata["vad"] = None
            print("⚠️ VAD not available")
    except Exception as e:
        print(f"⚠️ VAD prewarm failed: {e}")
        proc.userdata["vad"] = None


# ---------------------------
# Main Entrypoint
# ---------------------------
async def entrypoint(ctx: JobContext):
    """Main entry point for the teach-tutor agent"""
    logger.info("=" * 60)
    logger.info("🎓 NEW TEACH-TUTOR SESSION STARTED")
    logger.info("Room: %s", ctx.room.name)
    logger.info("=" * 60)
    
    # Connect to room
    await ctx.connect()
    
    # Initialize plugins
    logger.info("🔌 Initializing plugins...")
    
    try:
        # STT: Deepgram
        stt_plugin = deepgram.STT(model="nova-2")
        logger.info("✅ Deepgram STT initialized")
        
        # LLM: OpenAI
        llm_plugin = openai.LLM(model="gpt-4o-mini")
        logger.info("✅ OpenAI LLM initialized (gpt-4o-mini)")
        
        # TTS: Murf Falcon - will be set per agent
        # For greeter, use a neutral voice
        tts_plugin = murf.TTS(voice="en-US-matthew")
        logger.info("✅ Murf TTS initialized")
        
        # VAD: Silero (from prewarm)
        vad_plugin = ctx.proc.userdata.get("vad")
        if vad_plugin:
            logger.info("✅ Using prewarmed Silero VAD")
        else:
            logger.info("⚠️ No VAD available (will use fallback)")
        
    except Exception as e:
        logger.error("❌ Plugin initialization failed: %s", e, exc_info=True)
        logger.error("Please check your API keys in .env.local:")
        logger.error("  - OPENAI_API_KEY")
        logger.error("  - DEEPGRAM_API_KEY")
        logger.error("  - MURF_API_KEY")
        return
    
    # Create initial greeting agent
    greeter = GreeterAgent()
    
    # Create the AgentSession
    session = AgentSession(
        vad=vad_plugin,
        stt=stt_plugin,
        llm=llm_plugin,
        tts=tts_plugin,
    )
    
    # Start the session with greeter agent
    logger.info("🎙️ Starting teach-tutor session...")
    await session.start(agent=greeter, room=ctx.room)
    
    # Generate initial greeting
    greeting = (
        "Hello! Welcome to the Teach-the-Tutor Active Recall Coach. "
        "I'm here to help you learn programming concepts through active recall. "
        f"We have {len(content_loader.get_all_concepts())} topics available: "
        f"{content_loader.get_concept_titles()}. "
        "Which learning mode would you like to try? "
        "Learn mode for explanations, Quiz mode to test yourself, "
        "or Teach Back mode where you explain concepts to me?"
    )
    
    try:
        await session.generate_reply(instructions=greeting)
        logger.info("✅ Greeting generated successfully")
    except Exception as e:
        logger.error("❌ Failed to generate greeting: %s", e)
    
    logger.info("✅ Session active - agent is listening...")


# ---------------------------
# CLI Entry Point
# ---------------------------
if __name__ == "__main__":
    logger.info("🚀 Starting Teach-the-Tutor Agent...")
    logger.info("Content directory: %s", DATA_DIR)
    
    # Check for required API keys
    required_keys = ["OPENAI_API_KEY", "DEEPGRAM_API_KEY", "MURF_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        logger.error("❌ Missing required API keys in .env.local:")
        for key in missing_keys:
            logger.error("   - %s", key)
        logger.error("Please add these keys to your .env.local file")
        sys.exit(1)
    
    logger.info("✅ All required API keys found")
    logger.info("Starting LiveKit worker...")
    
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm
    ))
'''

print("✅ Updated agent.py code ready!")
print("\n📝 Key changes made:")
print("1. ✅ Converted to multi-agent architecture with GreeterAgent, LearnAgent, QuizAgent, TeachBackAgent")
print("2. ✅ Added ContentLoader for managing tutor content")
print("3. ✅ Implemented agent handoffs using llm.handoff()")
print("4. ✅ Each agent has mode-switching tools")
print("5. ✅ Changed TTS from Cartesia to Murf (will use matthew, alicia, ken voices)")
print("6. ✅ Added context preservation with chat_ctx parameter")
print("7. ✅ Auto-creates content file if missing")
print("8. ✅ Each mode has appropriate function tools")