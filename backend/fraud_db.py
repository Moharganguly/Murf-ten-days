import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict

class FraudCaseDB:
    def __init__(self, db_path: str = "fraud_cases.db"):
        self.db_path = db_path
        self._create_tables()
        self._seed_sample_data()
    
    def _create_tables(self):
        """Create the fraud cases table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fraud_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userName TEXT NOT NULL,
                securityIdentifier TEXT NOT NULL,
                cardEnding TEXT NOT NULL,
                status TEXT DEFAULT 'pending_review',
                transactionName TEXT NOT NULL,
                transactionAmount REAL NOT NULL,
                transactionTime TEXT NOT NULL,
                transactionCategory TEXT NOT NULL,
                transactionSource TEXT NOT NULL,
                transactionLocation TEXT NOT NULL,
                securityQuestion TEXT NOT NULL,
                securityAnswer TEXT NOT NULL,
                outcome TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _seed_sample_data(self):
        """Add sample fraud cases if database is empty"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM fraud_cases")
        if cursor.fetchone()[0] == 0:
            sample_cases = [
                {
                    "userName": "John Smith",
                    "securityIdentifier": "12345",
                    "cardEnding": "4242",
                    "status": "pending_review",
                    "transactionName": "ABC Electronics Ltd",
                    "transactionAmount": 1299.99,
                    "transactionTime": "2025-11-27 02:45 AM IST",
                    "transactionCategory": "e-commerce",
                    "transactionSource": "alibaba.com",
                    "transactionLocation": "Shanghai, China",
                    "securityQuestion": "What is your mother's maiden name?",
                    "securityAnswer": "Johnson"
                },
                {
                    "userName": "Sarah Williams",
                    "securityIdentifier": "67890",
                    "cardEnding": "8888",
                    "status": "pending_review",
                    "transactionName": "Luxury Fashion Store",
                    "transactionAmount": 5499.00,
                    "transactionTime": "2025-11-27 03:15 AM IST",
                    "transactionCategory": "retail",
                    "transactionSource": "fashionlux.ru",
                    "transactionLocation": "Moscow, Russia",
                    "securityQuestion": "What is your pet's name?",
                    "securityAnswer": "Buddy"
                },
                {
                    "userName": "Michael Chen",
                    "securityIdentifier": "54321",
                    "cardEnding": "9999",
                    "status": "pending_review",
                    "transactionName": "Tech Gadgets Pro",
                    "transactionAmount": 899.50,
                    "transactionTime": "2025-11-27 01:30 AM IST",
                    "transactionCategory": "electronics",
                    "transactionSource": "techdeals.ng",
                    "transactionLocation": "Lagos, Nigeria",
                    "securityQuestion": "What city were you born in?",
                    "securityAnswer": "Mumbai"
                }
            ]
            
            for case in sample_cases:
                cursor.execute("""
                    INSERT INTO fraud_cases (
                        userName, securityIdentifier, cardEnding, status,
                        transactionName, transactionAmount, transactionTime,
                        transactionCategory, transactionSource, transactionLocation,
                        securityQuestion, securityAnswer
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    case["userName"], case["securityIdentifier"], case["cardEnding"],
                    case["status"], case["transactionName"], case["transactionAmount"],
                    case["transactionTime"], case["transactionCategory"], 
                    case["transactionSource"], case["transactionLocation"],
                    case["securityQuestion"], case["securityAnswer"]
                ))
            
            conn.commit()
            print(f"✅ Seeded {len(sample_cases)} sample fraud cases")
        
        conn.close()
    
    def get_pending_case_by_username(self, username: str) -> Optional[Dict]:
        """Get a pending fraud case for a specific user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM fraud_cases 
            WHERE userName = ? AND status = 'pending_review'
            ORDER BY created_at DESC
            LIMIT 1
        """, (username,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_case_status(self, case_id: int, status: str, outcome: str):
        """Update the status and outcome of a fraud case"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fraud_cases 
            SET status = ?, outcome = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, outcome, case_id))
        
        conn.commit()
        conn.close()
        print(f"✅ Updated case {case_id}: {status} - {outcome}")
    
    def get_all_cases(self):
        """Get all fraud cases (for debugging)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fraud_cases ORDER BY created_at DESC")
        cases = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return cases
