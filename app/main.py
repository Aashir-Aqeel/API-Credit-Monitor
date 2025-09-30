from fastapi import FastAPI
from app.services.monitor import check_user_credits
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import sys

# --------------------------
# Logger setup
# --------------------------
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
if not logger.handlers:
    # Console handler with UTF-8 encoding
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Optional: File handler
    fh = logging.FileHandler("credit_monitor.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

# --------------------------
# FastAPI app
# --------------------------
app = FastAPI(title="OpenAI Credit Monitor")

@app.get("/run-monitor")
async def run_monitor_api():
    logger.info("API /run-monitor hit")
    results = await check_user_credits()
    logger.info("API /run-monitor finished")
    return {"status": "success", "results": results}

# --------------------------
# Scheduler on startup
# --------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("⚡ Application startup complete. Scheduler is starting...")

    # AsyncIOScheduler runs inside FastAPI's event loop
    scheduler = AsyncIOScheduler()

    # Schedule check_user_credits coroutine
    scheduler.add_job(check_user_credits, 'interval', hours=6)  # real usage: every 6 hours
    # For testing, you can change to every 1 minute
    # scheduler.add_job(check_user_credits, 'interval', minutes=1)

    scheduler.start()
    logger.info("Scheduler started. Jobs scheduled for check_user_credits.")
