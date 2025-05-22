import pandas as pd
from app.model.RouterModels import UuidResponse
from loguru import logger
from typing import List

def uuid_input_handler(uuid_input: str,
                       obd:pd.DataFrame,
                       specific_generic_mapping:pd.DataFrame) -> UuidResponse:
    """Checks if a user input uuid is in OBD and decides how to proceed with it."""

    logger.info(f'user input: "{uuid_input}"')

    generic_material_info = []

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
                generic_material_info = gather_generic_material_info(obd, uuids_out_list)
                message = f'Found generic matches for entered specific material.'
                logger.info(f'{message}:{uuids_out_list}')
    else:
        message = f'Could not find UUID in Ökobaudat data.'
        logger.info(f'{message}')

    return UuidResponse(uuid_in=uuid_input,
                        material_info=generic_material_info,
                        message=message)

def gather_generic_material_info(obd:pd.DataFrame, uuid_list:List[str]):
    "Gets additional information about each material in the input list"
    generic_material_info=[]
    obd_unique = obd.drop_duplicates(subset=['UUID'])
    for uuid in uuid_list:
        generic_material_info.append({
            'UUID': uuid,
            'Name': obd_unique[obd_unique['UUID'] == uuid]['Name (de)'].values[0],
            'Kategorie': obd_unique[obd_unique['UUID'] == uuid]['Kategorie (original)'].values[0]
        })

    return generic_material_info
