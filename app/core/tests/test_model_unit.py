from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from core.models import XSRConfiguration


@tag('unit')
class ModelTests(TestCase):

    def test_create_xsr_configuration(self):
        """Test that creating a new XSR Configuration entry is successful
        with defaults """

        token_url = 'test.com'
        xsr_api_pk = '123'
        xsr_api_sk = '456'
        xsr_api_org_id = '789'
        courses_url = 'test2.com'

        xsrConfig = XSRConfiguration(
            token_url=token_url,
            xsr_api_pk=xsr_api_pk,
            xsr_api_sk=xsr_api_sk,
            xsr_api_org_id=xsr_api_org_id,
            courses_url=courses_url)

        self.assertEqual(xsrConfig.token_url,
                         token_url)
        self.assertEqual(xsrConfig.xsr_api_pk,
                         xsr_api_pk)
        self.assertEqual(xsrConfig.xsr_api_sk,
                         xsr_api_sk)
        self.assertEqual(xsrConfig.xsr_api_org_id,
                         xsr_api_org_id)
        self.assertEqual(xsrConfig.courses_url,
                         courses_url)

    def test_create_two_xsr_configuration(self):
        """Test that trying to create more than one XSR Configuration throws
        ValidationError """

        token_url = 'test.com'
        xsr_api_pk = '123'
        xsr_api_sk = '456'
        xsr_api_org_id = '789'
        courses_url = 'test2.com'

        with self.assertRaises(ValidationError):
            xsrConfig = \
                XSRConfiguration(
                    token_url=token_url,
                    xsr_api_pk=xsr_api_pk,
                    xsr_api_sk=xsr_api_sk,
                    xsr_api_org_id=xsr_api_org_id,
                    courses_url=courses_url)
            xsrConfig2 = \
                XSRConfiguration(
                    token_url=token_url,
                    xsr_api_pk=xsr_api_pk,
                    xsr_api_sk=xsr_api_sk,
                    xsr_api_org_id=xsr_api_org_id,
                    courses_url=courses_url)

            xsrConfig.save()
            xsrConfig2.save()
