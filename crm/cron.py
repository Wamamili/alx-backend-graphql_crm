import datetime
import gql
import requests
from gql.transport.requests import RequestsHTTPTransport
from gql import Client, gql, Client


def log_crm_heartbeat():
    """Logs a heartbeat message every 5 minutes."""
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    # Write (append) the log
    with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
        log_file.write(log_message)

    # Optional: Check GraphQL endpoint health
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200:
            print("✅ GraphQL endpoint is responsive.")
        else:
            print("⚠️ GraphQL endpoint returned non-200 status.")
    except Exception as e:
        print(f"❌ GraphQL check failed: {e}")

def update_low_stock():
    """Runs every 12 hours to restock products with low stock."""
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    mutation = """
    mutation {
      updateLowStockProducts {
        message
        updatedProducts
      }
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": mutation},
            timeout=10
        )

        data = response.json()
        message = data.get("data", {}).get("updateLowStockProducts", {}).get("message", "No response.")
        products = data.get("data", {}).get("updateLowStockProducts", {}).get("updatedProducts", [])

        # Log updates
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(f"\n[{timestamp}] {message}\n")
            for p in products:
                log_file.write(f" - {p}\n")

        print("✅ Low stock update job completed.")

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(f"\n[{timestamp}] ❌ Error: {e}\n")
        print(f"❌ Failed to update stock: {e}")
