import asyncio
from infrastructure.config import get_settings
from infrastructure.logging import setup_logging, get_logger

# Initialize structured logging
setup_logging()
logger = get_logger("worker")

async def main():
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode.")
    
    # Placeholder for initializing a queue consumer or cron scheduler
    logger.info("Worker is ready and waiting for jobs...")
    
    try:
        from infrastructure.database import AsyncSessionLocal
        from jobs.issue_detection import run_issue_detection
        from jobs.impact_analysis import run_impact_analysis_cycle
        from jobs.recommendation_engine import run_recommendation_cycle
        from application.services import event_publisher
        import uuid
        
        # Initialize scalable event publisher
        event_publisher.publisher = event_publisher.get_event_broker(
            environment=settings.environment,
            database_url=settings.database_url
        )
        
        # Keep the worker running
        while True:
            # Simulate a heartbeat or polling interval
            await asyncio.sleep(60)
            logger.info("Running scheduled intelligence cycle (Detection + Impact + Recommendations)...")
            
            # Using a placeholder tenant ID for local testing. In production, this would iterate active tenants.
            tenant_id = uuid.UUID('00000000-0000-0000-0000-000000000000')
            
            async with AsyncSessionLocal() as session:
                try:
                    logger.info("-> Detecting issues...")
                    await run_issue_detection(session, tenant_id)
                    
                    logger.info("-> Analyzing downstream impacts...")
                    await run_impact_analysis_cycle(session, tenant_id)
                    
                    logger.info("-> Generating recommendations...")
                    await run_recommendation_cycle(session, tenant_id)
                    
                except Exception as e:
                    logger.error(f"Intelligence cycle failed: {e}")
                    
            logger.debug("Worker cycle complete.")
    except asyncio.CancelledError:
        logger.info("Worker task cancelled.")
    except Exception as e:
        logger.error(f"Worker encountered an unexpected error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker shutting down gracefully (KeyboardInterrupt).")
