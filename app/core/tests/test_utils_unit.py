import hashlib
import logging
from unittest.mock import patch

import pandas as pd
from ddt import data, ddt, unpack
from django.test import tag

from core.management.utils.xsr_client import (
    extract_source, get_course_api_url, get_source_metadata_key_value,
    read_source_file, token_generation_for_api_endpoint)
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
                  '"programs": [{"contentUrl": "test"}]}],"paging": []}'

            mock_resp.get.return_value.text = val

            self.assertIsInstance(extract_source(self.xsr_config_obj), pd.DataFrame)
