from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.configuration.getConfig import Config
from app.routers import config, benchmark
from app.functionalities.data_loader import DataLoader
from loguru import logger

configuration = Config()

API_ID = configuration.API_ID
API_VERSION = configuration.API_VERSION

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.data = DataLoader() # type: ignore[attr-defined]
    yield
    logger.info('App shutdown successful')

app = FastAPI(title="BSSR Challenge Team 4",
              lifespan=lifespan)

app.mount("/app/static", StaticFiles(directory="app/static"), name="static")

# todo: remove before deployment
# specific dataset:
# 906a624c-2360-4a27-8493-c10fe7d398b2

# generic:
# ed391263-0e6d-43dd-ad3e-43607545f281

# todo: reload data after every update
# todo: make "/update" run an update
# todo: show log on /log (?)
# todo: write last updated file to a json/csv
# todo: show "used dataset version" on input html
# todo: Build "launch update process" html
# todo: change old logging to loguru


app.include_router(config.router)
app.include_router(benchmark.router)


# needed to start the application locally for development/debugging purpose. Will never be called on K8s.
if configuration.is_local:
    import uvicorn
    if __name__ == '__main__':
        uvicorn.run(app, host='127.0.0.1', port=8000)
