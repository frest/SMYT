# coding: utf-8
import os
import yaml

from django.db import models
from smyt.settings import YAML_DATA_FILE


def get_name(self):
    return self._meta.verbose_name_plural


def get_data():
    try:
        return yaml.load(file(YAML_DATA_FILE).read())
    except Exception:
        return {}


def create_field(field):
    for attr in ['id', 'type', 'title']:
        if attr not in field:
            return {}
    if field['type'] == 'int':
        return {field['id']:
                    models.IntegerField(verbose_name=field['title'])}
    elif field['type'] == 'date':
        return {field['id']:
                    models.DateField(verbose_name=field['title'])}
    return {field['id']:
                models.CharField(max_length=255, verbose_name=field['title'])}


def create_body(model, model_name):
    title = model['title']
    body = {'__module__': 'dynamic_models.models'}
    meta = type('Meta', (object, ),
                {'verbose_name_plural': title})
    body.update({'Meta': meta})
    body.update({'get_name': get_name})
    for field in model['fields']:
        body.update(create_field(field))

    return body


def generate_models():
    data = get_data()
    for name, model in data.iteritems():
        dynamic_models.update({
            name: type(name, (models.Model, ), create_body(model, name))})


dynamic_models = {}
generate_models()
