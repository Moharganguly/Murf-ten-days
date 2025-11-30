🛍️ E-commerce Voice Agent (ACP-Inspired)

A sophisticated voice-powered shopping assistant built following the Agentic Commerce Protocol (ACP) architecture. Shop naturally with your voice - browse products, apply filters, and place orders seamlessly. Built for the Murf AI 10 Days of Voice Agents Challenge - Day 9.

## 🌟 Features

- **🗣️ Voice-First Shopping** - Complete shopping experience through natural conversation
- **🏗️ ACP Architecture** - Clean separation between conversation and commerce logic
- **🔍 Smart Filtering** - Browse by category, price range, color, and size
- **📦 37 Products** - Diverse catalog across 10 categories (mugs to watches)
- **🛒 Order Management** - Structured order creation with unique IDs
- **💾 JSON Persistence** - Every order saved with complete details
- **📊 Order History** - View past orders with "What did I buy?"
- **🎯 Intent Understanding** - Natural queries like "Show me black hoodies under 1500"

## 🎬 How It Works

### Sample Shopping Flow:

**Agent:** "Hi! Welcome to StyleHub! I can help you find and buy products. We have mugs, t-shirts, hoodies, bags, and caps. What are you looking for today?"

**Customer:** "Show me some hoodies"

**Agent:** "I found 5 hoodies. Here are the top 5:
1. Black Pullover Hoodie - ₹1,499, black, size M
2. Grey Zip Hoodie - ₹1,699, grey, size L
3. Navy Blue Hoodie - ₹1,599, navy, size M
4. Oversized Hoodie - ₹1,799, beige, size XL
5. Sports Hoodie - ₹1,399, white, size L"

**Customer:** "Do you have any black hoodies under 1500?"

**Agent:** "I found 1 product:
1. Black Pullover Hoodie - ₹1,499, black, size M"

**Customer:** "I'll buy that one"

**Agent:** "Order ORD20251130120300 confirmed!
Items:
• 1x Black Pullover Hoodie @ ₹1,499 each
Total: ₹1,499
Status: confirmed"

**Customer:** "What did I just buy?"

**Agent:** "Order ORD20251130120300 confirmed!
Items:
• 1x Black Pullover Hoodie @ ₹1,499 each
Total: ₹1,499
Status: confirmed"

## 🏗️ ACP-Inspired Architecture

Voice Input → LiveKit → E-commerce Agent
↓
┌───────────────┴────────────────┐
↓ ↓ ↓
Deepgram STT Gemini LLM Murf Falcon TTS
↓ ↓ ↓
└───────────────┬────────────────┘
↓
Merchant Layer (catalog.py)
↓
┌───────────────┴────────────────┐
↓ ↓
Product Catalog Order Management
(37 products) (JSON persistence)
↓ ↓
list_products() create_order()
get_product_by_id() get_last_order()

text

### Key ACP Principles:

1. **Separation of Concerns** - Conversation logic separate from commerce logic
2. **Structured Data** - Products and orders follow consistent schema
3. **Stateless Functions** - Merchant functions are pure and testable
4. **JSON-Based** - Standard format for catalog and orders

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- LiveKit Agents SDK
- Murf AI Falcon (Text-to-Speech)
- Deepgram Nova-2 (Speech-to-Text)
- Google Gemini 2.0 (LLM)
- JSON (Data Storage)
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
LIVEKIT_AGENT_NAME=ecommerce-agent

AI Service APIs
GOOGLE_API_KEY=your_google_gemini_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
MURF_API_KEY=your_murf_api_key

text

## 🚀 Usage

### Start the E-commerce Agent

cd backend
python ecommerce_agent.py dev

text

### Start the Frontend

cd frontend
npm run dev

text

Visit `http://localhost:3000` and start shopping with your voice!

## 📂 Project Structure

Murf-Day9/
├── backend/
│ ├── ecommerce_agent.py # Main voice shopping agent
│ ├── catalog.py # ACP-inspired merchant layer
│ ├── orders/ # Saved order JSON files
│ │ └── ORD*.json
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

## 🗂️ Data Models (ACP-Inspired)

### Product Schema

{
"id": "hoodie-001",
"name": "Black Pullover Hoodie",
"description": "Cozy fleece hoodie with kangaroo pocket",
"price": 1499,
"currency": "INR",
"category": "hoodie",
"color": "black",
"size": "M",
"in_stock": true
}

text

### Order Schema

{
"id": "ORD20251130120300",
"items": [
{
"product_id": "hoodie-001",
"product_name": "Black Pullover Hoodie",
"quantity": 1,
"unit_price": 1499,
"subtotal": 1499
}
],
"total": 1499,
"currency": "INR",
"created_at": "2025-11-30T12:03:00",
"status": "confirmed"
}

text

## 🛍️ Product Catalog

### Categories & Products (37 Total)

| Category | Count | Price Range |
|----------|-------|-------------|
| ☕ Mugs | 5 | ₹420 - ₹850 |
| 👕 T-Shirts | 6 | ₹599 - ₹899 |
| 🧥 Hoodies | 5 | ₹1,399 - ₹1,799 |
| 👖 Jeans | 4 | ₹1,299 - ₹1,599 |
| 🎒 Bags | 4 | ₹899 - ₹1,599 |
| 🧢 Caps | 4 | ₹349 - ₹449 |
| 🕶️ Sunglasses | 3 | ₹749 - ₹899 |
| 👟 Shoes | 4 | ₹1,299 - ₹2,499 |
| ⌚ Watches | 3 | ₹1,499 - ₹3,499 |

### Sample Products:

- **Stoneware Coffee Mug** - ₹450 (white)
- **Classic Cotton T-Shirt** - ₹599 (black, M)
- **Black Pullover Hoodie** - ₹1,499 (black, M)
- **Slim Fit Jeans** - ₹1,299 (blue, 32)
- **Canvas Tote Bag** - ₹899 (beige)
- **Baseball Cap** - ₹399 (black)
- **Aviator Sunglasses** - ₹799 (gold)
- **White Sneakers** - ₹1,999 (white, 9)
- **Smart Watch** - ₹3,499 (black)

## 🎯 Core Features Implementation

### 1. Browse Products (ACP Function)

@function_tool
async def browse_products(
context: RunContext,
category: Optional[str] = None,
max_price: Optional[int] = None,
color: Optional[str] = None,
size: Optional[str] = None
):
"""Browse catalog with filters"""
filters = {}
if category: filters["category"] = category
if max_price: filters["max_price"] = max_price
# ... apply filters
products = list_products(filters)
return format_product_list(products)

text

### 2. Place Order (ACP Function)

@function_tool
async def place_order(
context: RunContext,
product_id: str,
quantity: int = 1
):
"""Create order from product ID"""
line_items = [{"product_id": product_id, "quantity": quantity}]
order = create_order(line_items)
return format_order_summary(order)

text

### 3. Merchant Layer (catalog.py)

def list_products(filters: Optional[Dict] = None) -> List[Dict]:
"""Filter and return products"""
results = PRODUCTS.copy()
# Apply category, price, color, size filters
return results

def create_order(line_items: List[Dict]) -> Dict:
"""Generate order with unique ID, calculate total"""
order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
# Build order object and save to JSON
return order

text

## 🧪 Testing

### Test Scenario 1: Browse by Category

User: "Show me coffee mugs"
Agent: Lists 5 mugs with prices

text

### Test Scenario 2: Filtered Search

User: "Do you have any t-shirts under 700 rupees?"
Agent: Shows 2 matching t-shirts

text

### Test Scenario 3: Complex Filter

User: "Show me black hoodies in size M"
Agent: Filters by category, color, and size

text

### Test Scenario 4: Place Order

User: "I'll buy the first hoodie"
Agent: Creates order with ID, confirms total

text

### Test Scenario 5: Order History

User: "What did I just buy?"
Agent: Shows last order details

text

## 💡 Key Learnings

1. **ACP Architecture** - Separating conversation from commerce makes the system modular and testable
2. **Voice Commerce UX** - Listing 5 items max keeps voice responses digestible
3. **Filter Intelligence** - Gemini extracts filters naturally from user speech
4. **Order Persistence** - JSON files provide audit trail for all transactions
5. **Structured Data** - Consistent schemas enable easy integration with real commerce systems

## 🚧 Future Enhancements

- [ ] Multi-item cart (add multiple products before checkout)
- [ ] Product recommendations based on browsing history
- [ ] Price comparisons and deals
- [ ] Real payment gateway integration (Stripe, Razorpay)
- [ ] Inventory management with stock tracking
- [ ] User authentication and profiles
- [ ] Order tracking and status updates
- [ ] Product reviews and ratings
- [ ] Wishlist functionality
- [ ] Voice-based product search
- [ ] Full ACP specification compliance

## 🙏 Acknowledgments

- Built for the **Murf AI 10 Days of Voice Agents Challenge - Day 9**
- Inspired by the [Agentic Commerce Protocol (ACP)](https://www.agenticcommerce.dev/)
- Powered by [LiveKit Agents](https://github.com/livekit/agents)
- Voice by [Murf AI Falcon](https://murf.ai)
- Challenge details: [Murf AI GitHub](https://github.com/murf-ai/ten-days-of-voice-agents-2025)

## 📧 Contact

Built by Mohar Ganguly | [GitHub](https://github.com/yourusername) | [LinkedIn](https://linkedin.com/in/yourprofile)

---

⭐ If you found this helpful, please star the repo!

## 📄 License

MIT License

---

**Ready to shop with your voice?**

Start the E-commerce Agent
cd backend && python ecommerce_agent.py dev

Start the Frontend
cd frontend && npm run dev

text

**Happy Voice Shopping!** 🛍️✨
