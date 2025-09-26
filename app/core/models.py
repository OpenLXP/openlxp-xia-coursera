import logging

from django.db import models
from openlxp_xia.models import XIAConfiguration, XISConfiguration

logger = logging.getLogger('dict_config_logger')


class XSRConfiguration(models.Model):
    """Model for XSR Configuration """

    DATA_TYPE_CHOICES = [
        ('course', 'Course Data'),
        ('competency', 'Competency Data'),
        ('learner', 'Learner Data'),
    ]

    token_url = models.CharField(
        help_text="Enter the token URL for Coursera", max_length=200
    )
    xsr_api_pk = models.CharField(
        help_text='Enter the Coursera Primary Key', max_length=200
    )
    xsr_api_sk = models.CharField(
        help_text='Enter the Coursera Secret Key', max_length=200
    )
    xsr_api_org_id = models.CharField(
        help_text='Enter the Coursera Organization ID', max_length=200
    )
    courses_url = models.CharField(
        help_text='Enter the URL to retrieve Coursera courses', max_length=200
    )
    key_fields = models.TextField(default='["Course_ID",'
                                  '"CourseProviderName"]',
                                  help_text='Enter list of field names '
                                  'to create metadata key',
                                  blank=True, null=True)

    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='course',
        help_text='Select the type of data for this configuration'
    )


class ConfigurationManager(models.Model):
    """Manager for XIA Configuration Model"""

    xsr_configuration = models.ForeignKey(
        'XSRConfiguration',
        on_delete=models.CASCADE,
        related_name='xsr_configuration',
        null=True,
        blank=True,
        help_text='Reference to the XSR Configuration'
    )
    xia_configuration = models.ForeignKey(
        XIAConfiguration,
        on_delete=models.CASCADE,
        related_name='xia_configuration',
        null=True,
        blank=True,
        help_text='Reference to the XIA Configuration'
    )
    xis_configuration = models.ForeignKey(
        XISConfiguration,
        on_delete=models.CASCADE,
        related_name='xis_configuration',
        null=True,
        blank=True,
        help_text='Reference to the XIS Configuration'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this configuration is active.'
    )
