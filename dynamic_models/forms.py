from django import forms


def create_form(model):
    """ Return form for model. """
    meta = {'Meta': type('Meta', (object, ), {'model': model})}
    return type('Form', (forms.ModelForm, ), meta)
