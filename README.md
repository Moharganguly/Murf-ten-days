🛒 AI Food & Grocery Ordering Voice Agent
An intelligent voice-powered shopping assistant that understands natural language requests, manages shopping carts, and processes orders seamlessly. Built for the Murf AI 10 Days of Voice Agents Challenge - Day 7.

🌟 Features
🧠 Recipe Intelligence - Say "I need ingredients for pasta" → automatically adds pasta + sauce

🛒 Smart Cart Management - Add, remove, update quantities with voice commands

🗣️ Natural Conversations - Powered by Murf AI Falcon for human-like interactions

📦 JSON Catalog - 21+ products across groceries, snacks, prepared food, and beverages

💾 Order Persistence - Every order saved with unique ID, timestamp, and customer details

🎯 Context Understanding - Understands complex requests like "breakfast items" or "pizza night"

💰 Real-time Totals - Automatic cart calculation and running totals

🎬 How It Works
Sample Conversation Flow:
Agent: "Hi! Welcome to QuickMart Express! I can help you order groceries, snacks, prepared food, and more! What would you like to order today?"

Customer: "I want to make a peanut butter sandwich"

Agent: "I've added bread and peanut butter to your cart for your peanut butter sandwich!"

Customer: "Also add milk and eggs"

Agent: "Added 1 Milk to your cart for ₹60.00 each. Added 1 Eggs to your cart for ₹80.00 each. Anything else?"

Customer: "What's in my cart?"

Agent: "1x Whole Wheat Bread @ ₹45.00 each
1x Peanut Butter @ ₹250.00 each
1x Milk @ ₹60.00 each
1x Eggs @ ₹80.00 each

Total: ₹435.00"

Customer: "That's all, place my order"

Agent: "What's your name?"

Customer: "Mohar Ganguly"

Agent: "And your delivery address?"

Customer: "123 Main Street, Mumbai"

Agent: "Order placed successfully! Your order ID is ORD20251128112300. Total: ₹435.00. Estimated delivery in 30 minutes. Thank you for shopping with QuickMart Express!"

🏗️ Architecture
text
User Voice → LiveKit Cloud → Grocery Agent
                                    ↓
                    ┌───────────────┴──────────────┐
                    ↓               ↓              ↓
              Deepgram STT    Gemini LLM    Murf Falcon TTS
                    ↓               ↓              ↓
                    └───────────────┬──────────────┘
                                    ↓
                    ┌───────────────┴──────────────┐
                    ↓                              ↓
              catalog.json                    orders/*.json
           (Product Catalog)              (Saved Orders)
                    ↓
              recipes.json
         (Meal to Ingredients)
🛠️ Tech Stack
Backend:

Python 3.12+

LiveKit Agents SDK

Murf AI Falcon (Text-to-Speech)

Deepgram Nova-2 (Speech-to-Text)

Google Gemini 2.0 (LLM)

JSON (Data Storage)

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
LIVEKIT_AGENT_NAME=grocery-agent

# AI Service APIs
GOOGLE_API_KEY=your_google_gemini_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
MURF_API_KEY=your_murf_api_key
🚀 Usage
Start the Grocery Agent
bash
cd backend
python grocery_agent.py dev
Start the Frontend
bash
cd frontend
npm run dev
Visit http://localhost:3000 and click "Connect" to start shopping!

📂 Project Structure
text
Murf-Day7/
├── backend/
│   ├── grocery_agent.py        # Main voice agent
│   ├── catalog.json            # Product catalog (21 items)
│   ├── recipes.json            # Recipe to ingredients mapping
│   ├── orders/                 # Saved orders directory
│   │   └── ORD*.json          # Individual order files
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── api/
│   │   │   └── connection-details/
│   │   └── page.tsx
│   ├── components/
│   └── hooks/
└── .env.local                  # Environment variables (not committed)
🗂️ Data Structures
Product Catalog (catalog.json)
json
{
  "store_name": "QuickMart Express",
  "categories": {
    "groceries": [
      {
        "id": "g001",
        "name": "Whole Wheat Bread",
        "category": "groceries",
        "price": 45.00,
        "unit": "loaf",
        "brand": "Modern",
        "tags": ["vegetarian", "breakfast"]
      }
    ],
    "snacks": [...],
    "prepared_food": [...],
    "beverages": [...]
  }
}
Recipe Mapping (recipes.json)
json
{
  "recipes": {
    "peanut butter sandwich": {
      "items": ["g002", "g006"],
      "description": "bread and peanut butter"
    },
    "pasta": {
      "items": ["g007", "g008"],
      "description": "pasta and pasta sauce"
    }
  }
}
Order Output (orders/ORD*.json)
json
{
  "order_id": "ORD20251128112300",
  "customer_name": "Mohar Ganguly",
  "delivery_address": "123 Main Street, Mumbai",
  "items": [
    {
      "item_id": "g002",
      "name": "Whole Wheat Bread",
      "quantity": 1,
      "unit_price": 45.00,
      "subtotal": 45.00
    }
  ],
  "total": 435.00,
  "timestamp": "2025-11-28T11:23:00",
  "status": "placed"
}
🎯 Key Features Implementation
1. Add Item to Cart
python
@function_tool
async def add_item_to_cart(context: RunContext, item_name: str, quantity: int = 1):
    """Add an item to the shopping cart"""
    item = find_item_by_name(item_name)
    # Adds to cart with quantity tracking
2. Recipe Intelligence
python
@function_tool
async def add_recipe_ingredients(context: RunContext, recipe_name: str):
    """Add all ingredients for a recipe to the cart"""
    recipe = recipes.get('recipes', {}).get(recipe_name_lower)
    # Automatically adds multiple items for meal requests
3. Cart Management
python
@function_tool
async def show_cart(context: RunContext):
    """Show current cart contents and total"""
    # Displays items with quantities and running total
4. Place Order
python
@function_tool
async def place_order(context: RunContext, customer_name: str, delivery_address: str):
    """Place the order and save it to a JSON file"""
    # Saves order with unique ID and timestamp
📊 Available Products
Category	Items	Price Range
Groceries	Bread, Milk, Eggs, Butter, Peanut Butter, Pasta, Rice, Oil	₹40 - ₹250
Snacks	Chips, Chocolate, Cookies, Namkeen	₹20 - ₹50
Prepared Food	Pizza, Sandwiches, Wraps	₹80 - ₹250
Beverages	Juice, Cola, Coffee	₹40 - ₹350
Total: 21 products across 4 categories

🍳 Smart Recipe Mapping
The agent understands these meal requests:

"Peanut butter sandwich" → Bread + Peanut Butter

"Pasta" → Pasta + Pasta Sauce

"Breakfast" → Bread + Eggs + Milk + Butter

"Coffee" → Milk + Coffee

"Pizza night" → 2x Pizza + 2x Cola

🧪 Testing
Test Scenario 1: Simple Items
text
User: "I need bread and milk"
Agent: Adds both items
Result: Cart contains 2 items
Test Scenario 2: Recipe Request
text
User: "I want to make pasta"
Agent: Adds pasta and pasta sauce
Result: Cart contains recipe ingredients
Test Scenario 3: Cart Management
text
User: "What's in my cart?"
Agent: Lists all items with total
User: "Remove bread"
Agent: Removes bread from cart
Test Scenario 4: Place Order
text
User: "I'm done, place my order"
Agent: Asks for name and address
Agent: Saves order to JSON file
Result: Order file created in orders/ directory
💡 Key Learnings
Natural Language Understanding - Users don't say "add product ID 123", they say "I need pasta"

Context Management - Maintaining cart state across conversation turns

Recipe Intelligence - Mapping high-level intents (meals) to low-level items (ingredients)

Confirmation Flow - Verbally confirming each action builds trust

Error Handling - Graceful fallbacks when items aren't found

🚧 Future Enhancements
 Real-time inventory checking

 Product recommendations based on cart

 Previous order history ("Reorder my last order")

 Order tracking and status updates

 Multi-language support

 Price comparison and deals

 Dietary filters (vegan, gluten-free, etc.)

 Voice-based product search

 Integration with actual payment gateways

🙏 Acknowledgments
Built for the Murf AI 10 Days of Voice Agents Challenge - Day 7

Powered by LiveKit Agents

Voice by Murf AI Falcon

Challenge details: Murf AI GitHub

⚠️ Disclaimer
This is a demonstration project.

All products and prices are fictional

Not connected to real payment systems

Not intended for production use without proper security and payment integration

📧 Contact
Built by Mohar Ganguly | GitHub | LinkedIn

⭐ If you found this helpful, please star the repo!

📄 License
MIT License

Quick Start:

bash
# Backend
cd backend && python grocery_agent.py dev

# Frontend  
cd frontend && npm run dev
Happy Shopping! 🛒✨
