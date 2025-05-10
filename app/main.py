from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.configuration.getConfig import Config
from app.routers import config, benchmark
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.functionalities.update_oekobaudat_version import DatasetUpdater
from app.functionalities.data_loader import DataLoader
from loguru import logger

# todo: remove before deployment

# specific dataset:
# 906a624c-2360-4a27-8493-c10fe7d398b2
# generic:
# ed391263-0e6d-43dd-ad3e-43607545f281

# todo: show log on /log (?)
# todo: show "used dataset version" and "last updated at" on input html
# todo: write last updated file to a json/csv
# todo: change old logging to loguru

configuration = Config()

API_ID = configuration.API_ID
API_VERSION = configuration.API_VERSION
UPDATE_HOUR = int(configuration.configuration_dict.get('UPDATE', {}).get('HOUR', 3))
UPDATE_MINUTE = int(configuration.configuration_dict.get('UPDATE', {}).get('MINUTE', 19))


def run_daily_update(app: FastAPI):
    logger.info("Running daily update")
    updater = DatasetUpdater()
    updater.perform_update()
    app.state.data = DataLoader()  # type: ignore[attr-defined]

    logger.info("Daily update process finished")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.data = DataLoader()  # type: ignore[attr-defined]
    scheduler = BackgroundScheduler()
    trigger = CronTrigger(hour=UPDATE_HOUR, minute=UPDATE_MINUTE)
    scheduler.add_job(run_daily_update, trigger, args=[app])
    scheduler.start()
    yield
    scheduler.shutdown()
    logger.info('App shutdown successful')


app = FastAPI(title="BSSR Challenge Team 4",
              lifespan=lifespan)

app.mount("/app/static", StaticFiles(directory="app/static"), name="static")

app.include_router(config.router)
app.include_router(benchmark.router)


# needed to start the application locally for development/debugging purpose. Will never be called on K8s.
if configuration.is_local:
    import uvicorn
    if __name__ == '__main__':
        uvicorn.run(app, host='127.0.0.1', port=8000)
