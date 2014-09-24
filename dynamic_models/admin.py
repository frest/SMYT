from django.contrib import admin

from .models import dynamic_models

#
# Registring models to django admin.
#

for model in dynamic_models:
    admin.site.register(dynamic_models[model])
