import logging

from django.db import models
from django.forms import ValidationError

logger = logging.getLogger('dict_config_logger')


class XSRConfiguration(models.Model):
    """Model for XSR Configuration """

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

    def save(self, *args, **kwargs):
        if not self.pk and XSRConfiguration.objects.exists():
            raise ValidationError('There can be only one XISConfiguration '
                                  'instance')
        return super(XSRConfiguration, self).save(*args, **kwargs)
