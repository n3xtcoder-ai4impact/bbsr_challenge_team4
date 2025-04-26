from app.functionalities.data_loader import OBD_2020, OBD_2023, OBD_2024, tbaustoff
from loguru import logger

def uuid_input_handler(uuid_input: str) -> str:
    logger.info(f'user input: {uuid_input}')

    for file in [OBD_2024, OBD_2023, OBD_2020]:
        if uuid_input in file['UUID'].unique():
            logger.info(f'Found UUID "{uuid_input}"')
            print(file[file['UUID']==uuid_input][['UUID', 'Typ']])
            if 'generic dataset' in list(file[file['UUID']==uuid_input][ 'Typ']):
                logger.info(f'generic dataset')
                # todo: look up uuid in tBaustoffe
            else:
                #todo: find generic dataset
                logger.info(f'non-generic dataset')
            result = f'Found UUID "{uuid_input}"'

            break
    else:
        result = f'Sorry, could not find UUID "{uuid_input}".'
    return result