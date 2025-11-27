from fraud_db import FraudCaseDB
import json

db = FraudCaseDB()
cases = db.get_all_cases()

print("\n📊 FRAUD CASES DATABASE\n")
for case in cases:
    print(f"ID: {case['id']}")
    print(f"User: {case['userName']}")
    print(f"Card: ****{case['cardEnding']}")
    print(f"Transaction: ${case['transactionAmount']:.2f} to {case['transactionName']}")
    print(f"Status: {case['status']}")
    if case['outcome']:
        print(f"Outcome: {case['outcome']}")
    print("-" * 60)
