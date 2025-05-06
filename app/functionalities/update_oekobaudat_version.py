import requests
import os
import json
from loguru import logger
from typing import Dict, Optional, Tuple
from app.functionalities.helper_functions import read_json_file, overwrite_smaller_file, write_csv_from_response

#TODO: add try-except brackets at places most likely to fail

class DatasetUpdater:

    def __init__(self):
        self.new_version_uuid = None
        self.new_version_name = None
        self.new_version_description = None


    def get_available_versions(self)->Dict:
        """Checks the Oekobaudat API for available dataset versions. Returns a dict with names, descriptions and uuids."""
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
                # todo: Also compare the downloaded versions to the available versions
                oekobaudat_versions_old = read_json_file(file_path='../data/OBD/oekobaudat_versions_old.json')
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
        """Downloads a new Oekobaudat dataset version with the passed UUID."""

        response = self.contact_api(url_tail=f'{new_version_uuid}/exportCSV')
        if not response.status_code == 200:
            logger.error(f'Update failed, response status_code:{response.status_code}. Could not update Oekobaudat data to release XXX with uuid YYY')
        else:
            self.response_content_handler(response)

            # todo: make sure it updates any existing file with the same name instead of rewriting it.
            # write downloaded file name to json file 'oekobaudat_versions_downloaded.json
            data = {self.new_version_uuid: [self.new_version_description, self.new_version_name]}
            output_dir = os.path.join('../data/OBD')
            os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
            output_path = os.path.join(output_dir, 'oekobaudat_versions_downloaded.json')

            # Write data to the JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        logger.info(f'Update process completed')


    def response_content_handler(self, response):
        """Manages where to put the content of a downloaded file, whether to overwrite existing files, etc"""
        output_dir = os.path.join('../data/OBD')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{self.new_version_name}.csv')

        if os.path.exists(output_path):
            logger.info(f'Downloaded file "{self.new_version_name}" already exists.')
            output_path_temp = os.path.join(output_dir, 'obd_temp.csv')
            write_csv_from_response(response, output_path=output_path_temp)
            if overwrite_smaller_file(new_file=output_path_temp, old_file=output_path):
                logger.success(
                    f'Updated existing Oekobaudat file {self.new_version_name} with UUID {self.new_version_uuid} to a more recent version')

        else:
            write_csv_from_response(response, output_path=output_path)
            logger.success(f'Downloaded new Oekobaudat file {self.new_version_name} with UUID {self.new_version_uuid}')

        return


    def contact_api(self, url_tail: str = '', params=None, headers=None):
        """Makes contact to the Oekobauidat API and returns the response"""
        base_url = 'https://oekobaudat.de/OEKOBAU.DAT/resource/datastocks/'
        url = base_url + url_tail

        if params is None:
            params = {}

        if headers is None:
            headers = {}

        response = requests.get(url, params=params, headers=headers)

        return response

    def perform_update(self):
        """Triggers an update if necessary"""
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


