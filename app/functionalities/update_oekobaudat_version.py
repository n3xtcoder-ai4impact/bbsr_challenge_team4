import requests
import csv
from loguru import logger
from typing import Dict
from app.data.OBD.versions import OEKOBAUDAT_VERSIONS_OLD, OEKOBAUDAT_VERSIONS_DOWNLOADED

#TODO: add try-except brackets

def get_available_versions()->Dict:
    logger.info('Getting available versions from Oekobaudat API')
    response = contact_api(params={'format':'json'})
    if not response.status_code == 200:
        logger.error('Could not update list of available Oekobaudat data sets. Update aborted.')
        available_versions = {}
    else:
        available_versions = {item['uuid']: item['name'][0]['value'] for item in response.json()['dataStock']}
        logger.info(f'Got {len(available_versions)} available versions from Oekobaudat API.')
    return available_versions


def is_update_necessary()->bool:
    """Checks if a new Oekobaudat version is available on the official API"""
    available_versions = get_available_versions()

    if not available_versions:
        update_necessary = False

    else:
        new_version_uuid = list(set(available_versions.keys())-set(OEKOBAUDAT_VERSIONS_OLD.keys()))[0]
        # todo: Oekobaudat update - make this work for more than one new versions

        if not new_version_uuid:
            update_necessary = False

        else:
            if 'release' in available_versions[new_version_uuid].lower():
                logger.info(f'Found a new release: {new_version_uuid} - {available_versions[new_version_uuid]}')
                update_necessary = True

    return update_necessary


def download_new_version(version_uuid: str):

    # download data
    response = contact_api(url_tail=f'{version_uuid}/exportCSV')
    if not response.status_code == 200:
        logger.error('Update failed, response status_code:{response.status_code}. Could not update Oekobaudat data to release XXX with uuid YYY')
        update_success = False

    else:
        csv_from_api_response(response)

    message = 'Download successful'
    logger.info('Updated Oekobaudat data to release XXX with uuid YYY')
    return message

def contact_api(url_tail: str = '', params = None, headers = None, ):
    base_url = 'https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks/'
    url = base_url + url_tail

    if params is None:
        params = {}

    if headers is None:
        headers = {}

    response = requests.get(url, params=params, headers=headers)

    return response


def csv_from_api_response(response):
    lines = response.text.splitlines()
    with open('new_version.csv', mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        for line in lines:
            row = line.split(';')
            writer.writerow(row)

    return

# todo: development stuff below - remove before release!
if __name__=='__main__':
    is_update_necessary()
    # todo: continue here!


