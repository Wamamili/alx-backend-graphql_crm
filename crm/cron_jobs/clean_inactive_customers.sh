#!/bin/bash
# clean_inactive_customers.sh
# Deletes customers with no orders since a year ago and logs the cleanup

# Activate virtual environment if needed (optional)
# source /path/to/venv/bin/activate

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Run Django command inside shell
DELETED_COUNT=$(python manage.py shell <<EOF
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True) | Customer.objects.exclude(order__order_date__gte=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Log the result
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> $LOG_FILE
