from app.functionalities.data_loader import OBD_2020, OBD_2023, OBD_2024, tbaustoff, generic_specific_matches
from loguru import logger

def uuid_input_handler(uuid_input: str) -> str:
    logger.info(f'user input: "{uuid_input}"')

    for file in [OBD_2024, OBD_2023, OBD_2020]:
        if uuid_input in file['UUID'].unique():
            logger.info(f'Found UUID "{uuid_input}" in OBD')
            if 'generic dataset' in list(file[file['UUID']==uuid_input][ 'Typ']):
                logger.info(f'UUID is a generic dataset')
                result = (f'UUID "{uuid_input}" is a generic dataset.')

            else:
                df_generic_matches = get_generic_uuids_from_specific_uuid(uuid_specific=uuid_input)

                logger.info(f'UUID "{uuid_input}" is a non-generic dataset.')
                if len(df_generic_matches) == 0:
                    logger.info('Could not find a generic match for the input material')
                else:
                    logger.info(f'Found generic match(es):{list(df_generic_matches["uuid_generic"])}')

                result = (f'UUID "{uuid_input} is a non-generic dataset.')
                result += (f' Found generic match(es):{list(df_generic_matches["uuid_generic"])}.')

            #todo: what to get from tBaustoffe?
            #t_baustoff_info = get_info_from_tbaustoff(uuid_generic)
            #result += (f'\nMaterial information from tBaustoff:\n{t_baustoff_info}')

            break

    else:
        result = f'Sorry, could not find UUID "{uuid_input}".'
        logger.info(f'No information found in OBD for UUID "{uuid_input}"')

    return result


def get_info_from_tbaustoff(uuid: str)-> str:
    """Returns material information from tBaustoff given a UUID"""
    #todo: what info to return from tBaustoffe?

    material_info = '(none)'
    return material_info

def get_generic_uuids_from_specific_uuid(uuid_specific:str = None):
    """Returns the UUIDs of several generic datasets and their match scores given a UUID of a specific dataset"""
    df_matches = generic_specific_matches[generic_specific_matches['uuid_specific']=='abc-123']
    #todo: exchange 'abc-123' for uuid_specific before deployment
    return df_matches