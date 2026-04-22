import asyncio
import logging
import sys

from infrastructure.config import get_settings

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("worker")

async def main():
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode.")
    
    # Placeholder for initializing a queue consumer or cron scheduler
    logger.info("Worker is ready and waiting for jobs...")
    
    try:
        # Keep the worker running
        while True:
            # Simulate a heartbeat or polling interval
            await asyncio.sleep(60)
            logger.debug("Worker heartbeat...")
    except asyncio.CancelledError:
        logger.info("Worker task cancelled.")
    except Exception as e:
        logger.error(f"Worker encountered an unexpected error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker shutting down gracefully (KeyboardInterrupt).")
