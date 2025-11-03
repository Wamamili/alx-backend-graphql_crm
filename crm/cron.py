import datetime
import requests

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
