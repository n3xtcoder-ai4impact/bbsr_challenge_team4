from pyexpat.errors import messages

from fastapi import APIRouter, Request, Form
from pydantic import ValidationError

from app.configuration.getConfig import Config
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates/")

from app.functionalities.uuid_handler import uuid_input_handler
from app.model.RouterModels import UuidsOut


# get the config file
configuration = Config()

# SET THE API-ID: DO NOT CHANGE THIS!
API_ID = configuration.API_ID
API_VERSION = configuration.API_VERSION

# fastAPI Instance
router = APIRouter()
# Logger
#logger = configuration.logger

from loguru import logger

@router.get('/')
def read_form(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request, 'result': 'none'})

@router.get('/index')
def read_form(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request, 'result': 'none'})

#todo: get current version of oekobaudat's dataset into this endpoint
@router.get("/dataset_info")
def show_dataset_information():
    dataset_info = {'uuid':'abc-123',
                    'name':'Ökobaudat1',
                    'description':'A very nice dataset!'}
    message = f'Current version of the dataset: {dataset_info}'
    return message

@router.get("/input")
def form_post(request: Request):
    result = "(waiting for input)"
    return templates.TemplateResponse('input.html', context={'request': request, 'result': result})


@router.post("/input")
def form_post(request: Request, uuid_input: str = Form(None)):
    if uuid_input is None:
        return templates.TemplateResponse('input.html',
                                          context={'request': request,
                                                   'result': 'Please enter a valid UUID'})
    if not uuid_input.replace('-', '').isalnum():
        return templates.TemplateResponse('input.html',
                                          context={'request': request,
                                                   'result': 'Please enter a valid UUID containing only letters, numbers and dashes.'})
    else:
        try:
            response = uuid_input_handler(uuid_input)
        except Exception as e:
            logger.critical(f'ERROR: {e}')
            return templates.TemplateResponse('input.html',
                                              context={'request': request, 'result': 'Something went wrong internally, please try again'})

        message=response.message
        uuids_out = response.uuids_out
        return templates.TemplateResponse('input.html', context={'request': request, 'result': f'{message}<br>{uuids_out}'})


@router.get('/materials/{uuid_input}', response_model=UuidsOut)
async def get_generic_uuid(uuid_input: str)->UuidsOut:
    result = uuid_input_handler(uuid_input)
    return result


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
