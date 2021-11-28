from django import forms
from . import models

# from django.utils.translation import gettext_lazy as _

class LeaveForm(forms.ModelForm):
    class Meta:
        model = models.Leave
        fields = ('title', 'startDate', 'endDate', 'dayCount', 'comment')
        labels = {
            'startDate': 'Start',
            'endDate': 'End',
            'dayCount': 'Day(s)',
        }
        widgets = {
            'startDate': forms.SelectDateWidget,
            'endDate': forms.SelectDateWidget,
        }
