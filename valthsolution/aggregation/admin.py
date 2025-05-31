from django.contrib import admin

from .models import NameAggregationModel, CountryModel, RegionModel

# Register your models here.

admin.site.register(NameAggregationModel)
admin.site.register(CountryModel)
admin.site.register(RegionModel)
