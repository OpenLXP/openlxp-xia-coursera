from django.contrib import admin

from .models import (XSRConfiguration,
                     ConfigurationManager)

# Register your models here.


@admin.register(XSRConfiguration)
class XSRConfigurationAdmin(admin.ModelAdmin):
    list_display = ('token_url', 'xsr_api_pk', 'xsr_api_sk',
                    'xsr_api_org_id', 'courses_url')
    fields = ['token_url', 'xsr_api_pk', 'xsr_api_sk',
              'xsr_api_org_id', 'courses_url', 'key_fields',
              'data_type']


@admin.register(ConfigurationManager)
class ConfigurationManagerAdmin(admin.ModelAdmin):
    list_display = ('xsr_configuration', 'xia_configuration',
                    'xis_configuration', 'is_active')
    list_filter = ('is_active',)
    fields = ['xsr_configuration', 'xia_configuration',
              'xis_configuration', 'is_active']
# This code registers the XSRConfiguration and
# ConfigurationManager models with the Django admin site.
# It allows administrators to manage these configurations
# through the admin interface.
