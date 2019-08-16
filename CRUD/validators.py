from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class validate_Hostel_field:
    def regex_Mobile_No(self):
        print ("tedt")
        # message='Enter valid mobile number')#,message='suggestion',code='invalid')
        return RegexValidator(regex=r'^\d{10}$',message='mobile no consists of 10 digits',code='invalid mobile no')

    def regex_Ph_No(self):
        return RegexValidator(r'^\d{7}$')
