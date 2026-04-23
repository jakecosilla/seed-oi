import logging
import sys
import structlog
from asgi_correlation_id import correlation_id

def setup_logging():
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
    ]

    # Add correlation ID to logs
    def add_correlation_id(_, __, event_dict):
        cid = correlation_id.get()
        if cid:
            event_dict["correlation_id"] = cid
        return event_dict

    structlog.configure(
        processors=shared_processors + [
            add_correlation_id,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Root logger setup
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

def get_logger(name: str):
    return structlog.get_logger(name)
