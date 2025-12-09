from celery import Celery
from backend.app.core.config import settings

celery_app = Celery(
    "sentry_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['backend.app.workers.tasks.scan_dns',
             'backend.app.workers.tasks.scan_ports',
             'backend.app.workers.tasks.scan_osint',
             'backend.app.workers.tasks.scan_web',
             'backend.app.workers.tasks.scan_whois',
             'backend.app.workers.tasks.scan_fuzz',
             'backend.app.workers.tasks.scan_waf',
             'backend.app.workers.tasks.scan_ssl',
             'backend.app.workers.tasks.scan_api',
             'backend.app.workers.tasks.scan_cve',
             'backend.app.workers.tasks.scan_honeypot'
    ]
    
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Auto-discover tasks in the tasks folder
celery_app.autodiscover_tasks(['backend.app.workers.tasks'])