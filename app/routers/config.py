from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from app.configuration.getConfig import Config
from app.functionalities.uuid_handler import uuid_input_handler
from app.functionalities.update_oekobaudat_version import DatasetUpdater
from app.model.RouterModels import UuidsOut
from loguru import logger

templates = Jinja2Templates(directory="app/templates/")

configuration = Config()

# SET THE API-ID: DO NOT CHANGE THIS!
API_ID = configuration.API_ID
API_VERSION = configuration.API_VERSION

router = APIRouter()


@router.get('/')
def read_form(request: Request):
    return templates.TemplateResponse('index.html',
                                      context={'request': request, 'result': 'none'})

@router.get('/index')
def read_form(request: Request):
    return templates.TemplateResponse('index.html',
                                      context={'request': request, 'result': 'none'})

#todo: get current version of oekobaudat's dataset into this endpoint - or show in footnote / somewhere else
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
    return templates.TemplateResponse('input.html',
                                      context={'request': request, 'result': result})

@router.get('/update')
def run_manual_update(request:Request):
    updater = DatasetUpdater()
    updater.perform_update()
    result = 'Update process completed'
    logger.info('Update process completed')
    return result

@router.post("/input")
def form_post(request: Request, uuid_input: str = Form(None), update: bool = Form(False)):
    if update:
        updater = DatasetUpdater()
        updater.perform_update()
        result = "Update completed successfully"
        return templates.TemplateResponse('input.html',
                                          context={'request': request, 'result': result})

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
            response = uuid_input_handler(uuid_input=uuid_input,
                                          obd=request.app.state.data.obd,
                                          specific_generic_mapping=request.app.state.data.specific_generic_mapping)
        except Exception as e:
            logger.critical(f'ERROR: {e}')
            return templates.TemplateResponse('input.html',
                                              context={'request': request,
                                                       'result': 'Something went wrong internally, please try again'})

        uuids_out = response.uuids_out

        if not uuids_out:
            return templates.TemplateResponse('input.html',
                                              context={'request': request,
                                                       'result': f'{response.message}'})
        else:
            return templates.TemplateResponse('input.html',
                                              context={'request': request,
                                                       'result': f'{response.message}:<br><br>' +
                                                                 "<br>".join([f'{i + 1}: {uuid}' for i, uuid in enumerate(uuids_out)])
                                                       }
                                              )

@router.get('/materials/{uuid_input}', response_model=UuidsOut)
async def get_generic_uuid(request: Request, uuid_input: str)->UuidsOut:
    result = uuid_input_handler(uuid_input=uuid_input,
                                obd=request.app.state.data.obd,
                                specific_generic_mapping=request.app.state.data.specific_generic_mapping)
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
