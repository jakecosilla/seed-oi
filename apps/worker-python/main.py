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
        from infrastructure.database import AsyncSessionLocal
        from jobs.issue_detection import run_issue_detection
        import uuid
        
        # Keep the worker running
        while True:
            # Simulate a heartbeat or polling interval
            await asyncio.sleep(60)
            logger.info("Running scheduled issue detection job...")
            
            # Using a placeholder tenant ID for local testing. In production, this would iterate active tenants.
            tenant_id = uuid.UUID('00000000-0000-0000-0000-000000000000')
            
            async with AsyncSessionLocal() as session:
                try:
                    await run_issue_detection(session, tenant_id)
                except Exception as e:
                    logger.error(f"Issue detection failed: {e}")
                    
            logger.debug("Worker heartbeat complete.")
    except asyncio.CancelledError:
        logger.info("Worker task cancelled.")
    except Exception as e:
        logger.error(f"Worker encountered an unexpected error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker shutting down gracefully (KeyboardInterrupt).")
