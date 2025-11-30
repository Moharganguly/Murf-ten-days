"""
ACP-inspired merchant layer
Handles product catalog and order management
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# Product Catalog (ACP-inspired structure)
PRODUCTS = [
    # Coffee Mugs
    {
        "id": "mug-001",
        "name": "Stoneware Coffee Mug",
        "description": "Handcrafted ceramic mug, perfect for morning coffee",
        "price": 450,
        "currency": "INR",
        "category": "mug",
        "color": "white",
        "in_stock": True
    },
    {
        "id": "mug-002",
        "name": "Travel Tumbler",
        "description": "Insulated steel tumbler, keeps drinks hot for 6 hours",
        "price": 850,
        "currency": "INR",
        "category": "mug",
        "color": "black",
        "in_stock": True
    },
    {
        "id": "mug-003",
        "name": "Glass Coffee Mug",
        "description": "Double-walled glass mug with handle",
        "price": 550,
        "currency": "INR",
        "category": "mug",
        "color": "clear",
        "in_stock": True
    },
    
    # T-Shirts
    {
        "id": "tshirt-001",
        "name": "Classic Cotton T-Shirt",
        "description": "100% cotton, comfortable fit",
        "price": 599,
        "currency": "INR",
        "category": "tshirt",
        "color": "black",
        "size": "M",
        "in_stock": True
    },
    {
        "id": "tshirt-002",
        "name": "Premium Cotton T-Shirt",
        "description": "Soft premium cotton with modern cut",
        "price": 799,
        "currency": "INR",
        "category": "tshirt",
        "color": "white",
        "size": "L",
        "in_stock": True
    },
    {
        "id": "tshirt-003",
        "name": "Graphic Print T-Shirt",
        "description": "Cool graphic design, 100% cotton",
        "price": 699,
        "currency": "INR",
        "category": "tshirt",
        "color": "navy",
        "size": "M",
        "in_stock": True
    },
    
    # Hoodies
    {
        "id": "hoodie-001",
        "name": "Black Pullover Hoodie",
        "description": "Cozy fleece hoodie with kangaroo pocket",
        "price": 1499,
        "currency": "INR",
        "category": "hoodie",
        "color": "black",
        "size": "M",
        "in_stock": True
    },
    {
        "id": "hoodie-002",
        "name": "Grey Zip Hoodie",
        "description": "Full-zip hoodie with drawstring hood",
        "price": 1699,
        "currency": "INR",
        "category": "hoodie",
        "color": "grey",
        "size": "L",
        "in_stock": True
    },
    {
        "id": "hoodie-003",
        "name": "Navy Blue Hoodie",
        "description": "Premium cotton blend, relaxed fit",
        "price": 1599,
        "currency": "INR",
        "category": "hoodie",
        "color": "navy",
        "size": "M",
        "in_stock": True
    },
    
    # Accessories
    {
        "id": "bag-001",
        "name": "Canvas Tote Bag",
        "description": "Eco-friendly canvas bag with leather straps",
        "price": 899,
        "currency": "INR",
        "category": "bag",
        "color": "beige",
        "in_stock": True
    },
    {
        "id": "cap-001",
        "name": "Baseball Cap",
        "description": "Adjustable cotton cap with embroidered logo",
        "price": 399,
        "currency": "INR",
        "category": "cap",
        "color": "black",
        "in_stock": True
    },
]

# Orders storage
ORDERS = []
ORDERS_DIR = os.path.join(os.path.dirname(__file__), "orders")
os.makedirs(ORDERS_DIR, exist_ok=True)


def list_products(filters: Optional[Dict] = None) -> List[Dict]:
    """
    ACP-inspired: Browse product catalog with filters
    
    Filters supported:
    - category: str
    - max_price: int
    - min_price: int
    - color: str
    - size: str
    """
    results = PRODUCTS.copy()
    
    if not filters:
        return results
    
    # Apply filters
    if "category" in filters:
        category = filters["category"].lower()
        results = [p for p in results if p.get("category", "").lower() == category]
    
    if "max_price" in filters:
        max_price = int(filters["max_price"])
        results = [p for p in results if p["price"] <= max_price]
    
    if "min_price" in filters:
        min_price = int(filters["min_price"])
        results = [p for p in results if p["price"] >= min_price]
    
    if "color" in filters:
        color = filters["color"].lower()
        results = [p for p in results if p.get("color", "").lower() == color]
    
    if "size" in filters:
        size = filters["size"].upper()
        results = [p for p in results if p.get("size", "").upper() == size]
    
    return results


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """Get a specific product by ID"""
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None


def create_order(line_items: List[Dict]) -> Dict:
    """
    ACP-inspired: Create an order
    
    line_items format: [
        {"product_id": "mug-001", "quantity": 2},
        {"product_id": "tshirt-001", "quantity": 1}
    ]
    
    Returns order object with:
    - id, items, total, currency, created_at, status
    """
    # Generate order ID
    order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Calculate order details
    order_items = []
    total = 0
    currency = "INR"
    
    for item in line_items:
        product = get_product_by_id(item["product_id"])
        if not product:
            continue
        
        quantity = item.get("quantity", 1)
        subtotal = product["price"] * quantity
        total += subtotal
        
        order_items.append({
            "product_id": product["id"],
            "product_name": product["name"],
            "quantity": quantity,
            "unit_price": product["price"],
            "subtotal": subtotal
        })
    
    # Create order object
    order = {
        "id": order_id,
        "items": order_items,
        "total": total,
        "currency": currency,
        "created_at": datetime.now().isoformat(),
        "status": "confirmed"
    }
    
    # Save to memory and file
    ORDERS.append(order)
    
    # Persist to JSON file
    order_file = os.path.join(ORDERS_DIR, f"{order_id}.json")
    try:
        with open(order_file, 'w', encoding='utf-8') as f:
            json.dump(order, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save order to file: {e}")
    
    return order


def get_last_order() -> Optional[Dict]:
    """Get the most recent order"""
    if ORDERS:
        return ORDERS[-1]
    return None


def format_product_list(products: List[Dict], max_items: int = 5) -> str:
    """Format product list for voice response"""
    if not products:
        return "I couldn't find any products matching your criteria."
    
    # Limit to max_items for voice readability
    display_products = products[:max_items]
    
    result = f"I found {len(products)} product(s). Here are the top {len(display_products)}:\n\n"
    
    for idx, product in enumerate(display_products, 1):
        result += f"{idx}. {product['name']} - ₹{product['price']}"
        if 'color' in product:
            result += f", {product['color']}"
        if 'size' in product:
            result += f", size {product['size']}"
        result += "\n"
    
    if len(products) > max_items:
        result += f"\n...and {len(products) - max_items} more. Would you like to hear more options?"
    
    return result


def format_order_summary(order: Dict) -> str:
    """Format order for voice confirmation"""
    summary = f"Order {order['id']} confirmed!\n\n"
    summary += "Items:\n"
    
    for item in order['items']:
        summary += f"• {item['quantity']}x {item['product_name']} @ ₹{item['unit_price']} each\n"
    
    summary += f"\nTotal: ₹{order['total']}\n"
    summary += f"Status: {order['status']}"
    
    return summary
