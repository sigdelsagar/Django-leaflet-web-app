from django.db import models
from CRUD.models import Hostel_info
from django.contrib import messages
from django.core.exceptions import ValidationError
# Create your models here.
from django.utils.translation import gettext_lazy as _


def validate_unique_date(value):
    if (0 != 0):
        raise ValidationError(
            _('%(value)s is not an even number'),
            params={'value': value},
        )


class PassRate(models.Model):
    Hostel = models.ForeignKey(
        Hostel_info, blank=True, on_delete=models.CASCADE)
    pass_year = models.PositiveIntegerField(
        null=True, blank=True, default=0, validators=[validate_unique_date])
    student_no = models.PositiveIntegerField(
        null=True, blank=True, default=0)

    def __str__(self):
        return str(self.Hostel)

    def clean(self):
        if PassRate.objects.filter(pass_year=self.pass_year).filter(Hostel=self.Hostel).exists():
            print(PassRate.objects.filter(pass_year=self.pass_year).filter(
                Hostel=self.Hostel).exists())
            raise ValidationError(
                '{} passrate for this {} already exist'.format(
                    self.pass_year, self.Hostel)

            )


class LikeRate(models.Model):
    Hostel = models.ForeignKey(
        Hostel_info, blank=True, on_delete=models.CASCADE)
    likes = models.PositiveIntegerField(
        null=True, blank=True, default=0)

    def __str__(self):
        return str(self.Hostel)
