from app.functionalities.data_loader import OBD_2020, OBD_2023, OBD_2024, tbaustoff
from loguru import logger

def uuid_input_handler(uuid_input: str) -> str:
    logger.info(f'user input: "{uuid_input}"')

    for file in [OBD_2024, OBD_2023, OBD_2020]:
        if uuid_input in file['UUID'].unique():
            logger.info(f'Found UUID "{uuid_input}" in OBD')
            if 'generic dataset' in list(file[file['UUID']==uuid_input][ 'Typ']):
                uuid_generic = uuid_input

                logger.info(f'UUID is a generic dataset')
                result = (f'UUID "{uuid_input}" is a generic dataset.')

            else:
                uuid_generic = get_generic_uuid_from_obd(uuid_specific=uuid_input)

                logger.info(f'UUID "{uuid_input}" is a non-generic dataset')
                logger.info(f'UUID "{uuid_generic}" is the matching generic dataset')

                result = (f'UUID "{uuid_input} is a non-generic dataset')
                result += (f'\nThe matching generic material is {uuid_generic}')

            t_baustoff_info = get_info_from_tbaustoff(uuid_generic)
            # todo what information to retrieve from tBaustoff?
            result += (f'\nMaterial information from tBaustoff:\n{t_baustoff_info}')

            break

    else:
        result = f'Sorry, could not find UUID "{uuid_input}".'
        logger.info(f'No information found in OBD for UUID "{uuid_input}"')

    return result


def get_info_from_tbaustoff(uuid: str)-> str:
    """Retrieves material information from tBaustoff with a UUID"""
    #todo: fill tBaustoff function with functionality

    material_info = ('none')

    return material_info

def get_generic_uuid_from_obd(uuid_specific:str = None):
    """Retrieves the UUID of a generic dataset given a UUID of a specific dataset"""
    #todo write function content for retrieval of a generic uuid with a specific uuid
    uuid_generic = 'abc-123'

    return uuid_generic