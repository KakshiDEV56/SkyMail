"""Celery configuration and setup."""

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue
from app.utils import constants

# Initialize Celery app
app = Celery(
    "skymail",
    broker=constants.CELERY_BROKER_URL,
    backend=constants.CELERY_RESULT_BACKEND,
)

# ======================== CELERY CONFIGURATION ========================

# Broker settings
app.conf.broker_url = constants.CELERY_BROKER_URL
app.conf.result_backend = constants.CELERY_RESULT_BACKEND

# Task settings
app.conf.task_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.result_serializer = "json"
app.conf.timezone = "UTC"
app.conf.enable_utc = True

# Task routing
default_exchange = Exchange("skymail", type="direct")
app.conf.task_queues = (
    Queue(
        "campaigns",
        exchange=default_exchange,
        routing_key="campaign.send",
        priority=10,
    ),
    Queue(
        "email_batches",
        exchange=default_exchange,
        routing_key="email.batch",
        priority=9,
    ),
    Queue(
        "scheduled",
        exchange=default_exchange,
        routing_key="scheduler.enqueue",
        priority=8,
    ),
)

app.conf.task_routes = {
    "app.workers.campaign_scheduler.enqueue_due_campaigns": {"queue": "scheduled"},
    "app.workers.campaign_send.send_campaign": {"queue": "campaigns"},
    "app.workers.email_batch.send_campaign_batch": {"queue": "email_batches"},
}

# Task time limits
app.conf.task_time_limit = 30 * 60  # 30 minutes hard limit
app.conf.task_soft_time_limit = 25 * 60  # 25 minutes soft limit

# Result backend settings
app.conf.result_expires = 3600  # Results expire after 1 hour

# ======================== CELERY BEAT SCHEDULE ========================

app.conf.beat_schedule = {
    "enqueue-due-campaigns": {
        "task": "app.workers.campaign_scheduler.enqueue_due_campaigns",
        "schedule": constants.CAMPAIGN_SCHEDULER_INTERVAL_SECONDS,  # Run every minute
        "options": {
            "queue": "scheduled",
            "priority": 10,
        },
    },
}

# Use database-backed schedule for distributed environments
app.conf.beat_scheduler = "celery.beat:PersistentScheduler"


# ======================== AUTO-DISCOVER TASKS ========================

app.autodiscover_tasks([
    "app.workers.campaign_scheduler",
    "app.workers.campaign_send",
    "app.workers.email_batch",
])


if __name__ == "__main__":
    app.start()
