from django.contrib import admin

from .models import Website, Webpage, Image, Content, DataSource, DataSourceContent

# Register your models here.

admin.site.register(Website)
admin.site.register(Webpage)
admin.site.register(Image)
admin.site.register(Content)
admin.site.register(DataSource)
admin.site.register(DataSourceContent)
