from prometheus_client import Counter

events_created_total = Counter(
    "events_created_total",
    "Total number of events created"
)