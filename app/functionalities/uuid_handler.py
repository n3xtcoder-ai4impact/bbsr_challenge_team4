import pandas as pd
from app.model.RouterModels import UuidsOut
from loguru import logger

def uuid_input_handler(uuid_input: str,
                       obd:pd.DataFrame,
                       specific_generic_mapping:pd.DataFrame) -> UuidsOut:
    """Checks if a user input uuid is in OBD and decides how to proceed with it."""

    logger.info(f'user input: "{uuid_input}"')
    uuid_output=[]
    for file in [obd]:
        if uuid_input in file['UUID'].unique():
            logger.info(f'Found UUID "{uuid_input}" in OBD')
            if 'generic dataset' in list(file[file['UUID']==uuid_input][ 'Typ']):
                message= 'The uuid belongs to a generic material.'
                logger.info(f'{message}')
            else:
                df_generic_matches = list(specific_generic_mapping[specific_generic_mapping['Specific_UUID']==uuid_input]['Generic_UUID'])
                logger.info(f'UUID is a non-generic dataset.')
                if len(df_generic_matches) == 0:
                    message='Could not find any generic materials that match the input uuid'
                    logger.info(f'{message}')
                else:
                    uuid_output=df_generic_matches
                    message='Found generic materials that match input uuid'
                    logger.info(f'{message}:{uuid_output}')
            break

    else:
        message = f'Could not find UUID in Ökobaudat data.'
        logger.info(f'{message}')

    return UuidsOut(uuid_in=uuid_input,
                    uuids_out=uuid_output,
                    message=message)