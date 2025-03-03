from django.contrib import admin

from .models import XSRConfiguration

# Register your models here.


@admin.register(XSRConfiguration)
class XSRConfigurationAdmin(admin.ModelAdmin):
    list_display = ('token_url', 'xsr_api_pk', 'xsr_api_sk',
                    'xsr_api_org_id', 'courses_url')
    fields = ['token_url', 'xsr_api_pk', 'xsr_api_sk',
              'xsr_api_org_id', 'courses_url']
