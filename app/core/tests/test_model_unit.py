from unittest.mock import mock_open, patch

from clamd import EICAR
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase, tag

from core.models import XSRConfiguration


@tag('unit')
class ModelTests(TestCase):

    def test_create_xsr_configuration(self):
        """Test that creating a new XSR Configuration entry is successful
        with defaults """
        source_file = 'test_file.json'

        xiaConfig = XSRConfiguration(
            source_file=source_file)

        self.assertEqual(xiaConfig.source_file,
                         source_file)

    def test_xsr_configuration_filename(self):
        """Test that retrieving an XSR Configuration entry is successful
        """
        source_file = 'test_file.json'
        source_dir = 'directory'

        xiaConfig = XSRConfiguration(
            source_file=f"{source_dir}/{source_file}")

        self.assertEqual(xiaConfig.filename(),
                         source_file)

    def test_xsr_configuration_virus(self):
        """Test that creating a XSR Configuration with a virus fails"""

        file = ContentFile(EICAR, 'virus')

        xiaConfig = XSRConfiguration(
            source_file=file)

        with patch('core.models.logger') as log,\
                patch('core.models.clamd') as clam:
            clam.instream.return_value = {'stream': ('BAD', 'EICAR')}
            clam.ClamdUnixSocket.return_value = clam

            self.assertEqual(xiaConfig.source_file.size, len(EICAR))
            self.assertRaises(ValidationError, xiaConfig.clean)
            self.assertEqual(xiaConfig.source_file, None)
            self.assertGreater(log.error.call_count, 0)
            self.assertIn('EICAR', log.error.call_args[0][0])
            self.assertGreater(clam.instream.call_count, 0)
            self.assertEqual(file, clam.instream.call_args[0][0])

    def test_xsr_configuration_non_csv(self):
        """Test that creating a XSR Configuration with a non csv file fails"""

        file_contents = b'test string'
        file = ContentFile(file_contents, 'not csv')

        xiaConfig = XSRConfiguration(
            source_file=file)

        with patch('core.models.logger') as log,\
                patch('core.models.clamd') as clam,\
                patch('builtins.open', mock_open()),\
                patch('core.models.magic') as magic,\
                patch('core.models.os'):
            magic.from_file.return_value = 'text/plain'
            clam.instream.return_value = {'stream': ('OK', 'OKAY')}
            clam.ClamdUnixSocket.return_value = clam

            self.assertEqual(xiaConfig.source_file.size, len(file_contents))
            self.assertRaises(ValidationError, xiaConfig.clean)
            self.assertEqual(xiaConfig.source_file, None)
            self.assertGreater(log.error.call_count, 0)
            self.assertIn('text/plain',
                          log.error.call_args[0][1])

    def test_create_two_xsr_configuration(self):
        """Test that trying to create more than one XSR Configuration throws
        ValidationError """
        with self.assertRaises(ValidationError):
            xsrConfig = \
                XSRConfiguration(source_file="example1.json")
            xsrConfig2 = \
                XSRConfiguration(source_file="example2.json")

            xsrConfig.save()
            xsrConfig2.save()
