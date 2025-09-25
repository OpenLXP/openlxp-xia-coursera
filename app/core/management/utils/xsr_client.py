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

adl_xapi_url = "http://adlnet.gov/expapi/verbs/"
host_project = "https://xapi.edlm/profiles/edlm-coursera" \
    "/concepts/activity-types/program"
object_type_uri = "https://w3id.org/xapi/cmi5/activitytype/course"
object_type = "Activity"
platform = "EDLM Coursera Integration - [Environment]"


def get_course_api_url(xsr_config=None):
    """"Retrieve course url api from XIS configuration"""
    logger.debug("Retrieve course url api from XIS configuration")
    if not xsr_config:
        # If no configuration is passed, get the first XSRConfiguration
        # from the database
        xsr_data = XSRConfiguration.objects.first()
    else:
        # If a configuration is passed, use it
        xsr_data = xsr_config
    url = xsr_data.courses_url
    org_id = xsr_data.xsr_api_org_id
    final_url = url.format(orgId=org_id)
    return final_url


def token_generation_for_api_endpoint(xsr_config=None):
    """Function that connects to Coursera api using an api key and
    secret to generates an access token, returns token"""
    if not xsr_config:
        xsr_data = XSRConfiguration.objects.first()
    else:
        xsr_data = xsr_config

    headers = {"content-type": "application/x-www-form-urlencoded"}
    payload = {"grant_type": "client_credentials"}
    basic = HTTPBasicAuth(xsr_data.xsr_api_pk, xsr_data.xsr_api_sk)
    xis_response = requests.post(url=xsr_data.token_url,
                                 headers=headers, data=payload,
                                 auth=basic, verify=False)
    data = xis_response.json()

    return data['access_token']


def coursera_courses_metadata_update(source_df_final):
    # Extracting only the instructor names from the data
    instructor_names = []
    if 'instructors' in source_df_final.columns:
        for list in source_df_final['instructors']:
            names = []
            for item in list:
                names.append(item['name'])
            instructor_names.append(names)
        # Re-assigning instructor column to only contain their names
        source_df_final['instructors'] = instructor_names

    partner_names = []
    # Extracting only the partner names from the data
    if 'partners' in source_df_final.columns:
        for list in source_df_final['partners']:
            names = []
            for item in list:
                names.append(item['name'])
            partner_names.append(names)
        # Re-assigning instructor column to only contain their names
        source_df_final['partners'] = partner_names

    # Extracting one URL from programs
    urls = []
    if 'programs' in source_df_final.columns:
        for row in source_df_final['programs']:
            url = row[0]['contentUrl']
            urls.append(url)
        # Re-assigning programs to only include a single URL
        source_df_final['programs'] = urls
    return source_df_final


def replace_coursera_learner_metadata(source_df_final):

    if 'email' in source_df_final.columns:
        source_df_final['email'] = "mailto:" + \
            source_df_final['email'].astype(str)

    if 'contentId' in source_df_final.columns:
        source_df_final['contentId'] = host_project + \
            "/courses/" + source_df_final['contentId'].astype(str)

        source_df_final["type"] = object_type_uri
        source_df_final["contextType"] = host_project
        source_df_final["objectType"] = object_type
        source_df_final["platform"] = platform
        source_df_final["programId"] = host_project + \
            "/courses/" + source_df_final['programId'].astype(str)
        source_df_final["programName"] = host_project + \
            "/courses/" + source_df_final['programName'].astype(str)
        source_df_final["verbStatus"] = None
        source_df_final["verbStatusURI"] = None

    if 'isCompleted' in source_df_final.columns:
        for index, row in source_df_final.iterrows():
            if row['isCompleted'] is True:
                source_df_final.loc[index, 'verbStatus'] = 'Completed'
            elif (row['isCompleted'] is False and
                    row['overallProgress'] > 0):
                source_df_final.loc[index, 'verbStatus'] = 'Progressed'
            else:
                source_df_final.loc[index, 'verbStatus'] = 'Registered'
            if source_df_final.loc[index, 'verbStatus'] is not None:
                source_df_final.loc[index, 'verbStatusURI'] = adl_xapi_url + \
                    source_df_final.loc[index, 'verbStatus'].lower()
    return source_df_final


def extract_source(xsr_config=None):

    if not xsr_config:
        xsr_config = XSRConfiguration.objects.first()
    else:
        xsr_config = xsr_config
    token = token_generation_for_api_endpoint(xsr_config)
    url = get_course_api_url(xsr_config)

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
        # if 'next' not in source_data_dict['paging']:
        #     source_df_final = pd.concat(source_df_list).
        # reset_index(drop=True)

        #     if xsr_config.data_type == "course":
        #         source_df_final = coursera_courses_metadata_update(
        #             source_df_final)
        #     elif xsr_config.data_type == "learner":
        #         source_df_final = replace_coursera_learner_metadata(
        #             source_df_final)

        #     logger.info("Completed retrieving data from source")
        #     return source_df_final
        # else:
        logger.info("Retrieving data starting from index "
                    + str(source_data_dict['paging']['next']))
        data = {'start': source_data_dict['paging']['next'],
                'limit': '1000'}
        resp = requests.get(url=url,
                            headers=header,
                            params=data,
                            verify=False)
        source_data_dict = json.loads(resp.text)

        # temp

        source_df = pd.DataFrame(source_data_dict['elements'])
        source_df = source_df.replace({np.nan: None})
        source_df_list.append(source_df)
        source_df_final = pd.concat(source_df_list).reset_index(drop=True)

        if xsr_config.data_type == "course":
            source_df_final = coursera_courses_metadata_update(
                source_df_final)
        elif xsr_config.data_type == "learner":
            source_df_final = replace_coursera_learner_metadata(
                source_df_final)

        logger.info("Completed retrieving data from source")
        return source_df_final


def read_source_file(xsr_config):

    logger.info("Retrieving data from XSR")

    # Function call to extract data from source repository
    source_df = extract_source(xsr_config)

    #  Creating list of dataframes of sources
    source_list = [source_df]

    logger.debug("Sending source data in dataframe format for EVTVL")
    return source_list


def get_source_metadata_key_value(xsr, data_dict):
    """Function to create key value for source metadata """
    # field names depend on source data and SOURCESYSTEM is system generated
    if not xsr:
        xsr_data = XSRConfiguration.objects.first()
    else:
        xsr_data = xsr
    if not xsr_data:  # pragma: no cover
        logger.error("XIA configuration is not set.")

    target_key_fields = xsr_data.key_fields

    key_fields = json.loads(target_key_fields)

    field_values = []
    data_df = pd.json_normalize(data_dict)

    for field in key_fields:
        try:
            value = data_df.at[0, field]
            field_values.append(str(value))
        except KeyError as e:
            logger.error(e)
            logger.info('Field name ' + field + ' is missing for '
                        'key creation')

    key_value = str()
    key_value_hash = str()
    if field_values:

        # Key value creation for source metadata
        key_value = '_'.join(field_values)

        if not key_value:

            logger.error('Key value is empty, cannot create key hash')
            key_value = None
            key_value_hash = None
        else:
            # Key hash creation for source metadata
            key_value_hash = hashlib.sha512(
                key_value.encode('utf-8')).hexdigest()

        # Key dictionary creation for source metadata
    key = get_key_dict(key_value, key_value_hash)
    return key
