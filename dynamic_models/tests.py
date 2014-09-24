# coding: utf-8
import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import dynamic_models


class ModelTest(TestCase):
    def test_users_model_exist(self):
        self.assertIn('users', dynamic_models)

    def test_rooms_model_exist(self):
        self.assertIn('rooms', dynamic_models)

    def test_users_stucture(self):
        fields = {
            'name': 'CharField',
            'paycheck': 'IntegerField',
            'date_joined': 'DateField',
        }
        users_struct = {f.name: f.get_internal_type()
                       for f in dynamic_models['users']._meta.fields}

        for field, value in fields.iteritems():
            self.assertIsNotNone(users_struct[field])
            self.assertEqual(users_struct[field], value)

    def test_rooms_stucture(self):
        fields = {
            'department': 'CharField',
            'spots': 'IntegerField',
        }
        rooms_struct = {f.name: f.get_internal_type()
                       for f in dynamic_models['rooms']._meta.fields}

        for field, value in fields.iteritems():
            self.assertIsNotNone(rooms_struct[field])
            self.assertEqual(rooms_struct[field], value)

    def test_user_can_be_created(self):
        user = dynamic_models['users'].objects.create(
            name='John Doe',
            paycheck=90000,
            date_joined="2006-03-12",
        )

        self.assertIsInstance(user, dynamic_models['users'])
        self.assertEqual(user.name, 'John Doe')
        self.assertEqual(user.paycheck, 90000)
        self.assertEqual(user.date_joined, '2006-03-12')

    def test_room_can_be_created(self):
        room = dynamic_models['rooms'].objects.create(
            department='Managers',
            spots=5,
        )

        self.assertIsInstance(room, dynamic_models['rooms'])
        self.assertEqual(room.department, 'Managers')
        self.assertEqual(room.spots, 5)


class RequestTest(TestCase):
    def test_main_page(self):
        response = self.client.get('/')
        self.assertRedirects(
            response,
            expected_url=str(reverse('dynamic:index')),
            status_code=301
        )

    def test_get_list(self):
        blocks = ['message', 'models', 'fields']
        response = self.client.get(
            str(reverse('dynamic:table', kwargs={'model': 'users'}))
        )
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        for block in blocks:
            self.assertIn(block, content)

    def test_update_valid(self):
        user = dynamic_models['users'].objects.create(
            name='John Doe',
            paycheck=90000,
            date_joined="2006-03-12",
        )
        response = self.client.post(
            str(reverse('dynamic:update', kwargs={
                'model': 'users',
                'pk': user.pk
            })),
            {
                'field': 'name',
                'value': 'Jhoana Doe'
            }
        )
        content = json.loads(response.content)
        user = dynamic_models['users'].objects.get(pk=user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['message']['status'], 'success')
        self.assertEqual(user.name, 'Jhoana Doe')

    def test_update_invalid(self):
        user = dynamic_models['users'].objects.create(
            name='John Doe',
            paycheck=90000,
            date_joined="2006-03-12",
        )
        response = self.client.post(
            str(reverse('dynamic:update', kwargs={
                'model': 'users',
                'pk': user.pk
            })),
            {
                'field': 'paycheck',
                'value': 'abc'
            }
        )
        content = json.loads(response.content)
        user = dynamic_models['users'].objects.get(pk=user.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['message']['status'], 'error')
        self.assertEqual(user.paycheck, 90000)

    def test_remove_valid(self):
        room = dynamic_models['rooms'].objects.create(
            department='Managers',
            spots=5,
        )
        response = self.client.post(
            str(reverse('dynamic:delete', kwargs={
                'model': 'rooms',
                'pk': room.pk
            }))
        )
        content = json.loads(response.content)
        count = dynamic_models['rooms'].objects.filter(pk=room.pk).count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, 0)
        self.assertEqual(content['message']['status'], 'success')

    def test_remove_invalid(self):
        room = dynamic_models['rooms'].objects.create(
            department='Managers',
            spots=5,
        )
        pk = room.pk
        room.delete()
        response = self.client.post(
            str(reverse('dynamic:delete', kwargs={
                'model': 'rooms',
                'pk': pk
            }))
        )
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['message']['status'], 'error')

    def test_create_valid(self):
        response = self.client.post(
            str(reverse('dynamic:create', kwargs={'model': 'users'})),
            {
                'name': 'Gilbert Bates',
                'paycheck': 200000,
                'date_joined': '2001-03-25'
            }
        )
        user = dynamic_models['users'].objects.get(name='Gilbert Bates')
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['message']['status'], 'success')
        self.assertIsInstance(user, dynamic_models['users'])

    def test_create_invalid(self):
        response = self.client.post(
            str(reverse('dynamic:create', kwargs={'model': 'users'})),
            {
                'name': 'Gilbert Bates',
                'paycheck': 'abc',
                'date_joined': '2001-003-25'
            }
        )
        count = dynamic_models['users'].objects.filter(name='Gilbert Bates').count()
        content = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['message']['status'], 'error')
        self.assertEqual(count, 0)
