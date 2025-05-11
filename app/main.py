"""
This app was built based on a fantastic FastAPI-Docker template that can be found here:
https://github.com/Salfiii/fastapi-template. Many thanks got out to its maintainer!

---------------------- BBSR challenge - Team 4 info ------------------------------------
The app was built by one person and anything connected to sentence transfomers by two others. They did provide results
that were included in the app, but their code was not implemented as a functional part of it. In case anyone would
like to retrace their steps in the future, their code can be found in /sentence-tranformer-code.
"""

# todo: Re-read DataLoader right after update
# todo: make extra file for config parameters
# todo: show log on endpoint /log
# todo: change old logging to loguru


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
