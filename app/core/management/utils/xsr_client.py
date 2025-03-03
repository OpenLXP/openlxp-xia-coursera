import hashlib
import json
import logging

import numpy as np
import pandas as pd
import requests
from openlxp_xia.management.utils.xia_internal import get_key_dict
from requests.auth import HTTPBasicAuth

from core.models import XSRConfiguration

logger = logging.getLogger('dict_config_logger')


def get_course_api_url():
    """"Retrieve course url api from XIS configuration"""
    logger.debug("Retrieve course url api from XIS configuration")
    xsr_data = XSRConfiguration.objects.first()
    url = xsr_data.courses_url
    org_id = xsr_data.xsr_api_org_id
    final_url = url.format(orgId=org_id)
    return final_url


def token_generation_for_api_endpoint():
    """Function that connects to Coursera api using an api key and
    secret to generates an access token, returns token"""
    xsr_data = XSRConfiguration.objects.first()

    headers = {"content-type": "application/x-www-form-urlencoded"}
    payload = {"grant_type": "client_credentials"}
    basic = HTTPBasicAuth(xsr_data.xsr_api_pk, xsr_data.xsr_api_sk)
    xis_response = requests.post(url=xsr_data.token_url,
                                 headers=headers, data=payload,
                                 auth=basic, verify=False)
    data = xis_response.json()
    return data['access_token']


def extract_source():
    token = token_generation_for_api_endpoint()
    url = get_course_api_url()

    header = {'Authorization': 'Bearer ' + token}
    data = {'start': '0', 'limit': '1000'}
    response = requests.get(url=url,
                            headers=header,
                            params=data,
                            verify=False)

    source_data_dict = json.loads(response.text)

    source_df_list = []

    while True:
        source_df = pd.DataFrame(source_data_dict['elements'])
        source_df = source_df.replace({np.nan: None})
        source_df_list.append(source_df)
        if 'next' not in source_data_dict['paging']:
            source_df_final = pd.concat(source_df_list).reset_index(drop=True)

            # Extracting only the instructor names from the data
            instructor_names = []
            for list in source_df_final['instructors']:
                names = []
                for item in list:
                    names.append(item['name'])
                instructor_names.append(names)
            # Re-assigning instructor column to only contain their names
            source_df_final['instructors'] = instructor_names

            # Extracting one URL from programs
            urls = []
            for row in source_df_final['programs']:
                url = row[0]['contentUrl']
                urls.append(url)
            # Re-assigning programs to only include a single URL
            source_df_final['programs'] = urls

            logger.info("Completed retrieving data from source")
            return source_df_final
        else:
            logger.info("Retrieving data starting from index "
                        + source_data_dict['paging']['next'])
            data = {'start': source_data_dict['paging']['next'],
                    'limit': '1000'}
            resp = requests.get(url=url,
                                headers=header,
                                params=data,
                                verify=False)
            source_data_dict = json.loads(resp.text)


def read_source_file():

    logger.info("Retrieving data from XSR")

    # Function call to extract data from source repository
    source_df = extract_source()

    #  Creating list of dataframes of sources
    source_list = [source_df]

    logger.debug("Sending source data in dataframe format for EVTVL")
    return source_list


def get_source_metadata_key_value(data_dict):
    """Function to create key value for source metadata """
    # field names depend on source data and SOURCESYSTEM is system generated
    field = ['id', 'SOURCESYSTEM']
    field_values = []

    for item in field:
        if not data_dict.get(item):
            logger.info('Field name ' + item + ' is missing for '
                                               'key creation')
            return None
        field_values.append(data_dict.get(item))

    # Key value creation for source metadata
    key_value = '_'.join(field_values)

    # Key value hash creation for source metadata
    key_value_hash = hashlib.sha512(key_value.encode('utf-8')).hexdigest()

    # Key dictionary creation for source metadata
    key = get_key_dict(key_value, key_value_hash)

    return key
