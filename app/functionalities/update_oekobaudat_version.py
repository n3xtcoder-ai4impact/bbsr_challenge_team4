import requests
import os
import json
from datetime import datetime
from loguru import logger
from typing import Dict, Optional, Tuple
from app.functionalities.helper_functions import read_json_file, write_csv_from_response
from app.model.RouterModels import DatasetVersion, UpdateResponse
from app.functionalities.helper_functions import save_dataset_version


class DatasetUpdater:
    """Used for updating Ökobaudat data. Contacts the official API for available datasets, compares them to the already
    known datasets and downloads a newer version if one is available.
    Updates are not always new versions (like 'OBD_2020 I' vs 'OBD_2020_II'), but can mean an existing version gets
    additional entries. In that case, the file in the API is longer and the existing file in the app gets overwritten
    with it."""
    def __init__(self):
        self.new_version_uuid = None
        self.new_version_name = None
        self.new_version_description = None
        self.new_version_message = 'no message'
        self.new_version_datetime = datetime.today().strftime("%Y-%m-%d %H:%M")


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
        """Checks if a new Oekobaudat version is available on the official API

        FUTURE IMPROVEMENTS:
            - In this state, the process misses incremental updates to the file currently in use, because its uuid is
            already in oekobaudat_versions_old.json
            - Instead of checking all versions in the API response, just checking the last one should be enough.
            In my understanding, a new version should include all older versions. As the UUIDs are unique, they will
            never be overwritten and deletions may occure because a product is not produced anymore.
        """
        available_versions = self.get_available_versions()


        if not available_versions:
            update_necessary = False

        else:
            try:
                oekobaudat_versions_old = read_json_file(file_path='app/data/OBD/oekobaudat_versions_old.json')
                self.new_version_uuid = list(set(available_versions.keys())-set(oekobaudat_versions_old.keys()))[0]
            except IndexError:
                pass

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
            self.handle_new_version_response(response)
            self.write_downloaded_version_details_to_json()

        logger.info(f'Update process completed')


    def handle_new_version_response(self, response):
        """Manages where to put the content of a downloaded file, whether to overwrite existing files, etc"""
        output_dir = os.path.join('app/data/OBD')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{self.new_version_name}.csv')

        if os.path.exists(output_path):
            logger.info(f'Downloaded file "{self.new_version_name}" already exists.')
            output_path_temp = os.path.join(output_dir, 'obd_temp.csv')
            write_csv_from_response(response, output_path=output_path_temp)
            if self.overwrite_smaller_file(new_file=output_path_temp, old_file=output_path):
                logger.success(
                    f'Updated existing Oekobaudat file {self.new_version_name} with UUID {self.new_version_uuid} to a more recent version')
                self.new_version_message = 'Updated the existing file to a more recent version'

        else:
            write_csv_from_response(response, output_path=output_path)
            logger.success(f'Downloaded new Oekobaudat file {self.new_version_name} with UUID {self.new_version_uuid}')
            self.new_version_message = 'Downloaded a new Oekobaudat file'

        # Save update details
        current_dataset_version = DatasetVersion(name=self.new_version_name,
                                                 description=self.new_version_description,
                                                 updated=self.new_version_datetime,
                                                 uuid=self.new_version_uuid
                                                 )

        save_dataset_version(dataset=current_dataset_version,
                             filepath='app/data/OBD/current_dataset_version.json')


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
        """Triggers an update if deemed necessary"""
        update_necessary, update_uuid = self.is_update_necessary()
        if update_necessary:
            logger.info('Update is possible, will download.')
            self.download_new_version(update_uuid)
        else:
            self.new_version_message = 'No new OBD releases found - no update necessary.'
            logger.info(self.new_version_message)

        return UpdateResponse(message=self.new_version_message,
                           name=self.new_version_name,
                           description=self.new_version_description,
                           uuid=self.new_version_uuid)

    def write_downloaded_version_details_to_json(self):
        """Writes details of the downloaded Ökobaudat file to a json, so a history of downloaded versions is available"""
        output_dir = os.path.join('app/data/OBD')
        output_path = os.path.join(output_dir, 'oekobaudat_versions_downloaded.json')

        new_version_data = {self.new_version_uuid: [self.new_version_description, self.new_version_name,
                                                    f'{self.new_version_datetime}']}

        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as json_file:
                try:
                    existing_data = json.load(json_file)
                except json.decoder.JSONDecodeError as e:
                    existing_data = {}
        else:
            existing_data = {}

        existing_data.update(new_version_data)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

    def overwrite_smaller_file(self, new_file: str, old_file: str):
        """Checks if a csv file already exists. If it does, the number of rows in the existing and
        the new file are compared. The old file gets replaced if it is shorter."""

        overwritten = False

        with open(old_file, 'r', encoding='latin-1') as f:
            existing_file_lines = sum(1 for _ in f)

        with open(new_file, 'r', encoding='latin-1') as f:
            new_file_lines = sum(1 for _ in f)

        if new_file_lines > existing_file_lines:
            os.replace(new_file, old_file)
            self.new_version_message = f'Overwriting existing file "{old_file}" because it was shorter than the downloaded file.'
            logger.info(self.new_version_message)
            overwritten = True
        else:
            self.new_version_message = f'Keeping existing file "{old_file}" because it is longer than or equal to the downloaded file.'
            logger.info(self.new_version_message)
            if os.path.exists(old_file):
                os.remove(new_file)

        return overwritten
