import requests
import csv
import os
import json
from loguru import logger
from typing import Dict, Optional, Tuple
from app.functionalities.helper_functions import read_json_file

#TODO: add try-except brackets at places most likely to fail


class DatasetUpdater:

    def __init__(self):
        self.new_version_uuid = None
        self.new_version_name = None
        self.new_version_description = None


    def get_available_versions(self, )->Dict:
        logger.info('Getting available versions from Oekobaudat API')
        response = self.contact_api(params={'format':'json'})
        if not response.status_code == 200:
            logger.error('Could not update list of available Oekobaudat data sets. Update aborted.')
            available_versions = {}
        else:
            available_versions = {item['uuid']: [item['name'][0]['value'],item['shortName']] for item in response.json()['dataStock']}
            logger.info(f'Got {len(available_versions)} available versions from Oekobaudat API.')
        return available_versions


    def is_update_necessary(self)->Tuple[bool, Optional[str]]:
        """Checks if a new Oekobaudat version is available on the official API"""
        available_versions = self.get_available_versions()


        if not available_versions:
            update_necessary = False

        else:
            try:
                oekobaudat_versions_old = read_json_file(self, file_path=os.path.join('../data/OBD/oekobaudat_versions_old.json'))
                self.new_version_uuid = list(set(available_versions.keys())-set(oekobaudat_versions_old.keys()))[0]
            except IndexError:
                pass

            # todo: Oekobaudat update - make this work for more than one new versions
            if not self.new_version_uuid:
                update_necessary = False

            else:
                if 'release' in available_versions[self.new_version_uuid][0].lower():
                    self.new_version_name = available_versions[self.new_version_uuid][1]
                    self.new_version_description = available_versions[self.new_version_uuid][0]

                    logger.info(
                        f'Found a new release. uuid: {self.new_version_uuid}, '
                        f'name: {self.new_version_name}, '
                        f'description: {self.new_version_description}.'
                                   )
                    update_necessary = True
                else:
                    update_necessary = False

        return update_necessary, self.new_version_uuid


    def download_new_version(self, new_version_uuid: str):

        response = self.contact_api(url_tail=f'{new_version_uuid}/exportCSV')
        if not response.status_code == 200:
            logger.error(f'Update failed, response status_code:{response.status_code}. Could not update Oekobaudat data to release XXX with uuid YYY')
        else:
            self.csv_from_api_response(response)
            logger.success(f'Downloaded new Oekobaudat version with uuid {self.new_version_uuid}')


            # todo: make sure it updates any existing file with the same name instead of rewriting it.
            data = {self.new_version_uuid: [self.new_version_description, self.new_version_name]}
            output_dir = os.path.join('../data/OBD')
            os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
            output_path = os.path.join(output_dir, 'oekobaudat_versions_downloaded.json')

            # Write data to the JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        return

    def csv_from_api_response(self, response):
        lines = response.text.splitlines()
        output_dir = os.path.join('../data/OBD')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'new_version.csv')

        with open(output_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            for line in lines:
                row = line.split(';')
                writer.writerow(row)
        return

    def contact_api(self, url_tail: str = '', params=None, headers=None):
        base_url = 'https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks/'
        url = base_url + url_tail

        if params is None:
            params = {}

        if headers is None:
            headers = {}

        response = requests.get(url, params=params, headers=headers)

        return response

    def perform_update(self):

        update_necessary, update_uuid = self.is_update_necessary()
        if update_necessary:
            logger.info('Update is necessary, will attempt to download.')
            self.download_new_version(update_uuid)
        else:
            logger.info('No new OBD releases found - no update necessary.')


# todo: development stuff below - remove before release!
if __name__=='__main__':

    updater = DatasetUpdater()
    updater.perform_update()


