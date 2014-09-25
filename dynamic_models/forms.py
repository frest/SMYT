from django import forms


def create_form(model):
    meta = {'Meta': type('Meta', (object, ), {'model': model})}
    return type('Form', (forms.ModelForm, ), meta)
