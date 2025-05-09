from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.configuration.getConfig import Config
from app.routers import config, benchmark
from loguru import logger

# get the config file
configuration = Config()

API_ID = configuration.API_ID
API_VERSION = configuration.API_VERSION

# fastAPI Instance
app = FastAPI(
    title="BSSR Challenge Team 4")

app.mount("/app/static", StaticFiles(directory="app/static"), name="static")


# include the routers
app.include_router(config.router)
app.include_router(benchmark.router)


# needed to start the application locally for development/debugging purpose. Will never be called on K8s.
if configuration.is_local:
    import uvicorn
    if __name__ == '__main__':
        # if run locally, the port might already be in use, just use another one then.
        uvicorn.run(app, host='127.0.0.1', port=8000)
