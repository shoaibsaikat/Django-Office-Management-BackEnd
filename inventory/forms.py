from django import forms
from . import models

# from django.utils.translation import gettext_lazy as _

class RequisitionForm(forms.ModelForm):
    class Meta:
        model = models.Requisition
        fields = ('title', 'inventory', 'approver', 'amount', 'comment')

# class InventoryUpdateForm(forms.ModelForm):

#     name = forms.CharField(disabled=True)

#     class Meta:
#         model = models.Inventory
#         fields = ('name', 'description', 'unit', 'count')

    # below works same as, disbaled=True
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['name'].widget.attrs['readonly'] = True
