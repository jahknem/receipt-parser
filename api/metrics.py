from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator

job_queue_depth = Gauge(
    "receipt_parser_job_queue_depth", "Number of jobs in the queue"
)

instrumentator = Instrumentator()
