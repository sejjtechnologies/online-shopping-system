from pytz import timezone
from datetime import datetime

# Define Uganda timezone
UGANDA_TZ = timezone("Africa/Kampala")

# Define relative time filter
def relative_time(value):
    now = datetime.utcnow()
    diff = now - value
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    else:
        return f"{int(seconds // 86400)} days ago"