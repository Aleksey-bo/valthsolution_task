from django.db import models


# Create your models here.
class NameAggregationModel(models.Model):
    id = models.AutoField(verbose_name="ID", primary_key=True, unique=True)
    name = models.TextField(verbose_name="Name")
    count = models.IntegerField(verbose_name="Count Of Requests", default=0)
    last_access = models.DateTimeField(verbose_name="Last Accessed")
    country_id = models.ForeignKey("CountryModel", on_delete=models.CASCADE)
    probability = models.FloatField(verbose_name="Probability", default=0.00)

    def __str__(self) -> str:
        return self.name


class CountryModel(models.Model):
    id = models.AutoField(verbose_name="ID", primary_key=True, unique=True, auto_created=True)
    common_country_name = models.TextField(
        verbose_name="Country Name (Common)", unique=True
    )
    official_country_name = models.TextField(
        verbose_name="Country Name (Official)", unique=True
    )
    cca2 = models.TextField(unique=True)
    independent = models.BooleanField(default=False, verbose_name="Independent")
    region_id = models.ForeignKey(
        "RegionModel", on_delete=models.CASCADE, verbose_name="Region"
    )
    capital = models.TextField(verbose_name="Capital Country")
    capital_lat = models.DecimalField(
        verbose_name="Capital Latitude", max_digits=9, decimal_places=6
    )
    capital_lon = models.DecimalField(
        verbose_name="Capital Longitude", max_digits=9, decimal_places=6
    )
    flag_png = models.TextField(verbose_name="Flage image (PNG)")
    flag_svg = models.TextField(verbose_name="Flag image (SVG)")
    flag_alt = models.TextField(verbose_name="Flag Alt")
    coat_of_arms_svg = models.TextField(verbose_name="Coat of Arms (SVG)")
    coat_of_arms_png = models.TextField(verbose_name="Coat of Arms (PNG)")
    borders_with = models.TextField(verbose_name="Borders with")

    def __str__(self) -> str:
        return self.common_country_name


class RegionModel(models.Model):
    id = models.AutoField(verbose_name="ID", primary_key=True, unique=True, auto_created=True)
    region = models.TextField(verbose_name="Region")
    subregion = models.TextField(verbose_name="Subregion")

    def __str__(self) -> str:
        return self.subregion
