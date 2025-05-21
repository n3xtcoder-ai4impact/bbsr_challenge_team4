import pandas as pd
from app.model.RouterModels import UuidResponse
from loguru import logger

def uuid_input_handler(uuid_input: str,
                       obd:pd.DataFrame,
                       specific_generic_mapping:pd.DataFrame) -> UuidResponse:
    """Checks if a user input uuid is in OBD and decides how to proceed with it."""

    logger.info(f'user input: "{uuid_input}"')
    uuids_out_list=[]
    #for file in [obd]:
    if uuid_input in obd['UUID'].unique():
        logger.info(f'Found UUID "{uuid_input}" in OBD')
        if 'generic dataset' in list(obd[obd['UUID']==uuid_input]['Typ']):
            message= 'The uuid belongs to a generic material.'
            logger.info(f'{message}')
        else:
            uuids_out_list = list(specific_generic_mapping[specific_generic_mapping['Specific_UUID']==uuid_input]['Generic_UUID'])
            logger.info(f'UUID is a non-generic dataset.')
            if len(uuids_out_list) == 0:
                message='Could not find any generic materials that match the input uuid'
                logger.info(f'{message}')
            else:
                message='Found generic materials that match input uuid'
                logger.info(f'{message}:{uuids_out_list}')
        #break
    else:
        message = f'Could not find UUID in Ökobaudat data.'
        logger.info(f'{message}')

    return UuidResponse(uuid_in=uuid_input,
                        uuids_out=uuids_out_list,
                        message=message)