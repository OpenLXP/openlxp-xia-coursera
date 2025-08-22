import pandas as pd
from django.test import TestCase

from core.models import XSRConfiguration


class TestSetUp(TestCase):
    """Class with setup and teardown for tests in XIS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        # globally accessible data sets

        self.source_metadata = {
            "1": {
                "Test": "0",
                "Test_id": "2146",
                "Test_url": "https://example.test.com/",
                "End_date": "9999-12-31T00:00:00-05:00",
                "test_name": "test name",
                "Start_date": "2017-03-28T00:00:00-04:00",
                "LearningResourceIdentifier": "TestData 123",
                "SOURCESYSTEM": "coursera",
                "test_description": "test description",
                "supplemental_data": "sample1"
            }
        }

        self.key_value = "TestData 123_coursera"
        self.key_value_hash = \
            "348a3c0ceae1888ea586252c6f66c9010917935237688771c638" \
            "e46dfc50efb473a9d7ceded9f27b4c41f83a4d949d4382b5ace3" \
            "912f5f7af59bcfc99c9f2d7f"
        self.hash_value = \
            "513a7f00940220c7839f5a0969afbdb6dff4a5d93b5af813287db6" \
            "01885349670875f27fcedbee8aa7b2bbbae9617853c8f9b14098faa1" \
            "92b2f1816a147ebd88"

        self.test_data = {
            "key1": ["val1"],
            "key2": ["val2"],
            "key3": ["val3"]}

        self.test_courses_url = \
            'https://api.coursera.com/ent/api/businesses.v1/123/contents'

        self.orgId = '123'

        self.metadata_df = pd.DataFrame.from_dict({1: self.source_metadata},
                                                  orient='index')

        self.xsr_config_obj = XSRConfiguration.objects.create(
            token_url="123",
            xsr_api_pk="123",
            xsr_api_sk="456",
            xsr_api_org_id="789",
            courses_url=self.test_courses_url,
            key_fields='["id", "SOURCESYSTEM"]'
        )

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
