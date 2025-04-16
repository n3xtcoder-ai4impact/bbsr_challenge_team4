#@TODO: Webservice entry point: https://fastapi.tiangolo.com/tutorial/bigger-applications/
import json
from fastapi import Depends, APIRouter, Request, Form
from app.configuration.getConfig import Config
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates/")


# get the config file
configuration = Config()

# SET THE API-ID: DO NOT CHANGE THIS!
API_ID = configuration.API_ID
API_VERSION = configuration.API_VERSION

# fastAPI Instance
router = APIRouter()
# Logger
logger = configuration.logger

@router.get('/')
def read_form():
    return 'hello world'

@router.get("/input")
def form_post(request: Request):
    result = "Enter a number"
    return templates.TemplateResponse('input.html', context={'request': request, 'result': result})


@router.post("/input")
def form_post(request: Request, num: int = Form(...)):
    result = num * 10
    return templates.TemplateResponse('input.html', context={'request': request, 'result': result})



@router.get("/config/", tags=["config"])
def get_config():
    """
    Returns the configuration of the webservice
    """
    return configuration.configuration_dict


@router.get("/actuator/health", tags=["config"])
async def health() -> dict:
    """
    Actuator health check
    :return:
    """

    global_status = "UP"

    status_dict = {
        "status": global_status,
        "description": "Health",
        "details": {
            "Just another check": {
                "status": "UP",
                "description": "description"
            },
        }
    }

    return status_dict
