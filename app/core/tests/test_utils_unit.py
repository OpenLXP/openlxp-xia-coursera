import hashlib
import logging
from unittest.mock import patch

import pandas as pd
from ddt import data, ddt, unpack
from django.test import tag

from core.management.utils.xsr_client import (
    coursera_courses_metadata_update, extract_source, get_course_api_url,
    get_source_metadata_key_value,
    read_source_file, replace_coursera_learner_metadata,
    token_generation_for_api_endpoint)
from core.models import XSRConfiguration

from .test_setup import TestSetUp

logger = logging.getLogger('dict_config_logger')


@tag('unit')
@ddt
class UtilsTests(TestSetUp):
    """Unit Test cases for utils """

    # Test cases for XSR_CLIENT
    def test_read_source_file(self):
        """Test to check the extraction of source data from XSR for EVTVL"""
        with patch('core.management.utils.xsr_client'
                   '.XSRConfiguration.objects') as xsrCfg, \
                patch('core.management.utils.xsr_client.'
                      'extract_source')as ext_data:
            xsrCfg.first.source_file.return_value = 'Source_file'
            ext_data.return_value = pd.DataFrame. \
                from_dict(self.source_metadata, orient='index')
            return_from_function = read_source_file(xsrCfg)
            self.assertIsInstance(return_from_function, list)

    @data(('key_field1', 'key_field2'), ('key_field11', 'key_field22'))
    @unpack
    def test_get_source_metadata_key_value(self, first_value, second_value):
        """Test key dictionary creation for source"""
        test_dict = {
            'id': first_value,
            'SOURCESYSTEM': second_value
        }

        expected_key = first_value + '_' + second_value
        expected_key_hash = hashlib.sha512(expected_key.encode('utf-8')). \
            hexdigest()

        result_key_dict = get_source_metadata_key_value(self.xsr_config_obj,
                                                        test_dict)
        self.assertEqual(result_key_dict['key_value'], expected_key)
        self.assertEqual(result_key_dict['key_value_hash'], expected_key_hash)

    @data(('key_field1', ''))
    @unpack
    def test_get_source_metadata_key_value_fail(self,
                                                first_value, second_value):
        """Test key dictionary creation for source"""
        test_dict = {
            'LearningResourceIdentifier': first_value,
            'SOURCESYSTEM': second_value
        }

        result_key_dict = get_source_metadata_key_value(self.xsr_config_obj,
                                                        test_dict)

        self.assertEqual(result_key_dict['key_value'], None)

    def test_get_course_api_url(self):
        """ Testing function the checks ability to
            get the correct courses API """
        with patch('core.management.utils.xsr_client'
                   '.XSRConfiguration.objects') as xsrCfg:
            xisConfig = XSRConfiguration(
                courses_url=self.test_courses_url,
                xsr_api_org_id=self.orgId
            )
            xsrCfg.first.return_value = xisConfig
            return_from_function = get_course_api_url()
            self.assertEqual(xisConfig.courses_url, return_from_function)

    def test_token_generation_for_api_endpoint(self):
        """Test function to mock creating an access token"""
        with patch('core.management.utils.xsr_client'
                   '.requests') as mock_req:
            mock_req.post.return_value.json.return_value = {'access_token': 1}
            xsr_data = XSRConfiguration(token_url="token_url",
                                        xsr_api_pk="123",
                                        xsr_api_sk="456")
            xsr_data.save()
            response = token_generation_for_api_endpoint()

            self.assertEqual(response, 1)

    def test_extract_source(self):
        """Test Function to connect to Coursera endpoint
        API and get source metadata"""

        with patch('core.management.utils.xsr_client.requests') as mock_resp:

            val = '{"elements": [{"course": "test", "instructors": [],'\
                  '"programs": [{"contentUrl": "test"}]}],' \
                  '"paging": {"next":[]}}'

            mock_resp.get.return_value.text = val
            self.assertIsInstance(extract_source(
                self.xsr_config_obj), pd.DataFrame)

    def test_coursera_courses_metadata_update(self):
        """Test coursera_courses_metadata_update function"""
        data = {
            'instructors': [
                [{'name': 'Alice'}, {'name': 'Bob'}],
                [{'name': 'Charlie'}]
            ],
            'partners': [
                [{'name': 'Partner1'}, {'name': 'Partner2'}],
                [{'name': 'Partner3'}]
            ],
            'programs': [
                [{'contentUrl': 'http://example.com/program1'}],
                [{'contentUrl': 'http://example.com/program2'}]
            ]
        }
        df = pd.DataFrame(data)
        updated_df = coursera_courses_metadata_update(df.copy())

        self.assertEqual(updated_df['instructors'][0], ['Alice', 'Bob'])
        self.assertEqual(updated_df['instructors'][1], ['Charlie'])
        self.assertEqual(updated_df['partners'][0], ['Partner1', 'Partner2'])
        self.assertEqual(updated_df['partners'][1], ['Partner3'])
        # If your function extracts only the first URL, adjust as needed
        self.assertEqual(updated_df['programs'][0],
                         'http://example.com/program1')
        self.assertEqual(updated_df['programs'][1],
                         'http://example.com/program2')

    def test_replace_coursera_learner_metadata(self):
        """Test replace_coursera_learner_metadata function"""

        data = {
            'email': ['user1@example.com', 'user2@example.com'],
            'contentId': ['123', '456'],
            'programId': ['789', '012'],
            'programName': ['ProgramA', 'ProgramB'],
            'isCompleted': [True, False],
            'overallProgress': [1, 0]
        }
        df = pd.DataFrame(data)
        updated_df = replace_coursera_learner_metadata(df.copy())

        # Check email formatting
        self.assertEqual(updated_df['email'][0], 'mailto:user1@example.com')
        self.assertEqual(updated_df['email'][1], 'mailto:user2@example.com')

        # Check contentId, programId, programName formatting
        host_project = \
            "https://xapi.edlm/profiles/edlm-coursera/concepts/" \
            "activity-types/program"
        self.assertTrue(updated_df['contentId'][0].startswith(host_project))
        self.assertTrue(updated_df['programId'][0].startswith(host_project))
        self.assertTrue(updated_df['programName'][0].startswith(host_project))

        # Check verbStatus and verbStatusURI
        self.assertEqual(updated_df['verbStatus'][0], 'Completed')
        self.assertEqual(updated_df['verbStatus'][1], 'Registered')
        self.assertTrue(updated_df['verbStatusURI'][0].endswith('/completed'))
        self.assertTrue(updated_df['verbStatusURI'][1].endswith('/registered'))
