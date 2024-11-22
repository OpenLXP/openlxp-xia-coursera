import logging
import os
import secrets
import string

import clamd
import magic
from django.db import models
from django.forms import ValidationError

from openlxp_xia_coursera_project import settings

logger = logging.getLogger('dict_config_logger')


class XSRConfiguration(models.Model):
    """Model for XSR Configuration """

    source_file = models.FileField(blank=True, null=True, upload_to='source/',
                                   help_text='Upload the excel source '
                                             'file')

    def filename(self):
        return os.path.basename(self.source_file.name)

    def clean(self):
        if self.source_file:
            # scan file for malicious payloads
            cd = clamd.ClamdUnixSocket()
            extracted_file = self.source_file
            scan_results = cd.instream(extracted_file)['stream']
            if 'OK' not in scan_results:
                for issue_type, issue in [scan_results, ]:
                    self.source_file = None
                    logger.error(
                        f'{issue_type} {issue}')
                    raise ValidationError('File content is dangerous.')
            else:
                extracted_file.seek(0)

                # generate random file name
                alphabet = string.ascii_letters + string.digits
                tmp_dir = settings.TMP_SOURCE_DIR
                random_name = ''.join(secrets.choice(alphabet)
                                      for _ in range(8))
                full_path = tmp_dir + random_name

                extracted_file.open('rb')

                # write to file and use magic to check file type
                with open(full_path, 'wb') as local_file:
                    local_file.write(extracted_file.read())
                    local_file.flush()
                    mime_type = magic.from_file(full_path, mime=True)

                # delete file
                os.remove(full_path)
                # log issue if file isn't CSV
                if 'spreadsheet' not in mime_type.lower():
                    self.source_file = None
                    logger.error('Invalid file type detected. Expected CSV, '
                                 'found %s', mime_type)
                    raise ValidationError('Invalid file type detected. '
                                          'Expected spreadsheet.')

    def save(self, *args, **kwargs):
        if not self.pk and XSRConfiguration.objects.exists():
            raise ValidationError('There can be only one XISConfiguration '
                                  'instance')
        if self.source_file:
            return super(XSRConfiguration, self).save(*args, **kwargs)
