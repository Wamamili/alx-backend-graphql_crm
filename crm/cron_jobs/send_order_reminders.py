#!/usr/bin/env python3
"""
send_order_reminders.py
Queries the GraphQL endpoint for recent orders and logs reminders daily.
"""

import requests
from datetime import datetime, timedelta

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

# Define the date filter (orders within the last 7 days)
seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

# GraphQL query
query = f"""
{{
  allOrders(filter: {{ orderDateGte: "{seven_days_ago}" }}) {{
    edges {{
      node {{
        id
        customer {{
          email
        }}
        orderDate
      }}
    }}
  }}
}}
"""

def log_message(message: str):
    """Append a message with timestamp to the log file."""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")

def main():
    try:
        response = requests.post(GRAPHQL_ENDPOINT, json={"query": query})
        response.raise_for_status()
        data = response.json()

        orders = data.get("data", {}).get("allOrders", {}).get("edges", [])
        if not orders:
            log_message("No recent orders found.")
        else:
            for order in orders:
                node = order.get("node", {})
                order_id = node.get("id")
                email = node.get("customer", {}).get("email", "unknown")
                log_message(f"Reminder: Order ID {order_id} → Customer {email}")

        print("Order reminders processed!")
    except Exception as e:
        log_message(f"Error: {e}")
        print("Error occurred while processing order reminders.")

if __name__ == "__main__":
    main()
