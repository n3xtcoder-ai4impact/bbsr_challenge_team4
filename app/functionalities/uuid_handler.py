from app.functionalities.data_loader import OBD_2020, OBD_2023, OBD_2024, tbaustoff, generic_specific_matches
from app.model.RouterModels import UuidsOut
from loguru import logger
from typing import Union, Dict

def uuid_input_handler(uuid_input: str) -> UuidsOut:
    logger.info(f'user input: "{uuid_input}"')
    uuid_output=''
    #todo: make uuid_input_handler use all available OBD versions in data directory
    for file in [OBD_2024, OBD_2023, OBD_2020]:
        if uuid_input in file['UUID'].unique():
            logger.info(f'Found UUID "{uuid_input}" in OBD')
            if 'generic dataset' in list(file[file['UUID']==uuid_input][ 'Typ']):
                message= 'The uuid belongs to a generic material.'
                logger.info(f'{message}')
            else:
                df_generic_matches = list(get_generic_uuids_from_specific_uuid(uuid_specific=uuid_input))
                logger.info(f'UUID is a non-generic dataset.')
                if len(df_generic_matches) == 0:
                    message='Could not find any generic materials that match the input uuid'
                    logger.info(f'{message}')
                else:
                    uuid_output=df_generic_matches #list(df_generic_matches["uuid_generic"])
                    message='Found generic materials that match input uuid.'
                    logger.info(f'{message}:{uuid_output}')
            break

    else:
        message = f'Could not find UUID in Ökobaudat data.'
        logger.info(f'{message}')

    return UuidsOut(uuid_in=uuid_input,
                    uuids_out=uuid_output,
                    message=message)



def get_generic_uuids_from_specific_uuid(uuid_specific:str = None):
    """Returns the UUIDs of several generic datasets and their match scores given a UUID of a specific dataset"""
    logger.info(f'{print(generic_specific_matches)}')
    df_matches = generic_specific_matches[generic_specific_matches['uuid_specific']==uuid_specific]['uuid_generic']
    return df_matches