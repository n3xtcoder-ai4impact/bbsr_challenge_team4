from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from app.configuration.getConfig import Config
from app.functionalities.uuid_handler import uuid_input_handler
from app.functionalities.update_oekobaudat_version import DatasetUpdater
from app.functionalities.reembedding import ReEmbedder
from app.functionalities.data_loader import DataLoader
from app.model.RouterModels import UuidsOut, DatasetVersion, UpdateResponse
from loguru import logger

templates = Jinja2Templates(directory="app/templates/")

configuration = Config()

# SET THE API-ID: DO NOT CHANGE THIS!
API_ID = configuration.API_ID
API_VERSION = configuration.API_VERSION

router = APIRouter()


@router.get('/api/materials/{uuid_input}', response_model=UuidsOut)
async def get_generic_uuid(request: Request, uuid_input: str)->UuidsOut:
    """Takes in a UUID and, if it is specific and found, returns the generic matches for it"""
    result = uuid_input_handler(uuid_input=uuid_input,
                                obd=request.app.state.data.obd,
                                specific_generic_mapping=request.app.state.data.specific_generic_mapping)
    return result


@router.get("/api/dataset_info", response_model=DatasetVersion)
async def show_dataset_information(request: Request)->DatasetVersion:
    """Return information about the Ökobaudat dataset currently in use"""
    return request.app.state.data.current_dataset_version


@router.get("/api/update", response_model=UpdateResponse)
async def run_api_update(request: Request)->UpdateResponse:
    """Updates the Ökobaudat dataset"""
    update_response = update_reload_reembed(request=request)
    return update_response


@router.get('/')
def read_form(request: Request):
    return templates.TemplateResponse('index.html',
                                      context={'request': request, 'result': 'none'})


@router.get('/index')
def read_form(request: Request):
    return templates.TemplateResponse('index.html',
                                      context={'request': request, 'result': 'none'})


@router.get("/input")
def form_post(request: Request):
    result = "(waiting for input)"
    return templates.TemplateResponse('input.html',
                                      context={'request': request, 'result': result})


@router.post("/input")
def form_post(request: Request, uuid_input: str = Form(None), update: bool = Form(False)):
    """Handles all requests from the /input page: UUID queries and update button clicks"""
    if update:
        update_reload_reembed(request=request)
        result = "Update process completed successfully"

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

        specific_material = response.specific_material
        matches = response.matches
        message = response.message

        return templates.TemplateResponse('input.html',
                                          context={
                                              'request': request,
                                              'message': message,
                                              'specific_material': specific_material,
                                              'matches': matches
                                          })


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


def update_reload_reembed(request:Request):
    """Nomen est omen: updates dataset, reloads app.state.data so that new data is immediately available in the app,
     then re-embeds the material matchings and creates updated match files."""
    # Update
    updater = DatasetUpdater()
    update_response = updater.perform_update()

    # Re-load data
    request.app.state.data = DataLoader()

    # Re-embed
    reembedder = ReEmbedder()
    reembedder.run_reembedding()
    reembedder.create_best_matches_csv()

    return update_response
