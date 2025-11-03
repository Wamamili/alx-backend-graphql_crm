import datetime
import requests
from celery import shared_task

@shared_task
def generate_crm_report():
    """Generates a weekly CRM report and logs it."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = """
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            timeout=10
        )

        data = response.json().get("data", {})

        total_customers = data.get("totalCustomers", 0)
        total_orders = data.get("totalOrders", 0)
        total_revenue = data.get("totalRevenue", 0.0)

        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(
                f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"
            )

        print("✅ CRM report generated successfully.")

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} - ❌ Error: {e}\n")
        print(f"❌ Failed to generate report: {e}")
