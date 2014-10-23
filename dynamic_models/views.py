# coding: utf-8
import json

from django.views import generic
from django.http import HttpResponse, Http404
from django.core import serializers
from django.forms.models import model_to_dict
from django.middleware.csrf import get_token

from .models import dynamic_models
from .forms import create_form


class BelongToModelMixin(object):
    @property
    def model(self):
        try:
            return dynamic_models[self.kwargs['model']]
        except Exception:
            raise Http404


class AjaxMixin(object):
    http_method_names = [u'post']

    def render_to_response(self, context):
        return HttpResponse(
            json.dumps(context),
            content_type='application/json',
        )


class FormMixin(object):
    @property
    def form_class(self):
        return create_form(self.model)


class IndexView(generic.TemplateView):
    template_name = 'dynamic_models/model_list.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context.update({'dynamic_models': dynamic_models})
        return context
    
    def render_to_response(self, context, **response_kwargs):
        get_token(self.request)
        return super(IndexView, self).render_to_response(context,
                                                        **response_kwargs)

    def render_to_response(self, context, **response_kwargs):
        get_context(self.request)
        return super(IndexView, self).render_to_response(context,
                                                         **response_kwargs)


class ModelListView(BelongToModelMixin, generic.ListView):
    def render_to_response(self, context, **response_kwargs):
        fields_dict = {f.name:
                       [f.verbose_name, f.get_internal_type()]
                       for f in self.model._meta.fields}

        fields_dict.pop('id')
        message = {'text': r'Данные модели загружены', 'status': 'success'}
        models = json.loads(serializers.serialize('json', self.get_queryset()))
        content = json.dumps({
            'models': models,
            'fields': fields_dict,
            'message': message
        })
        response = HttpResponse(
            content,
            content_type='application/json',
            **response_kwargs
        )
        return response


class ModelDeleteView(
    BelongToModelMixin,
    AjaxMixin,
    generic.DeleteView
):
    http_method_names = [u'post']

    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            context = {'message': {
                'text': r'Успешно удалено',
                'status': 'success',
            }}
        except Exception:
            context = {'message': {
                'text': r'Такого обхекта не существует',
                'status': 'error',
            }}
        return HttpResponse(
            json.dumps(context),
            content_type='application/json',
        )


class ModelCreateView(
    BelongToModelMixin,
    AjaxMixin,
    FormMixin,
    generic.CreateView
):
    template_name = 'dynamic_models/form.html'

    def post(self, request, *args, **kwargs):
        data = request.POST
        form_class = self.get_form_class()
        form = form_class(data)
        if form.is_valid():
            message = {'text': r'Успешно добавленно', 'status': 'success'}
            form.save()
        else:
            message = {'text': r'Данные не корректны', 'status': 'error'}
        return self.render_to_response({'message': message})


class ModelUpdateView(
    BelongToModelMixin,
    AjaxMixin,
    FormMixin,
    generic.UpdateView
):
    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        data = model_to_dict(instance)
        data.update({request.POST['field']: request.POST['value']})
        form_class = self.get_form_class()
        form = form_class(data, instance=instance)
        if form.is_valid():
            form.save()
            message = {'text': r'Успешно обновленно', 'status': 'success'}
        else:
            message = {'text': r'Данные не корректны', 'status': 'error'}
        return self.render_to_response({'message': message})
