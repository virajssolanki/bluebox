from datetime import date
from django import forms 

class CustomDatePicker(forms.DateInput):
    def __init__(self, attrs={}, format=None):
        attrs.update(
            {
                'class': 'form-control',
                'type': 'date',
            }
        )
        self.format = format
        super().__init__(attrs, format=self.format)


class AvailableDateWidget(CustomDatePicker):
    def __init__(self, attrs={}, format=None):
        attrs.update({ 'max':date.today() })
        super().__init__(attrs, format=format)