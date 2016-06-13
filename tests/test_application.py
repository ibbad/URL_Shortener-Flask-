import unittest
import os

from app import create_app, db
from app.models import  Url
from app.main.views import random_hash_key


class TestApplication(unittest.TestCase):

    test_url = 'http://google.com'

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.key = random_hash_key(self.test_url)
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        assert 'form' in response.data

    def test_404_error_handler(self):
        response = self.client.get('/potato/potato')
        self.assertEqual(response.status_code, 404)
        assert "404: Not Found" in response.data

    def test_form(self):
        form = {'url': self.test_url}
        response = self.client.post('/form', data=form)
        link = Url.query.filter_by(url=self.test_url).first()
        self.assertIsNotNone(link)
        self.assertEqual(link.random_key, self.key)

    def test_link_expanding(self):
        link = Url(self.key, self.test_url)
        db.session.add(link)
        db.session.commit()
        response = self.client.get(self.key)
        self.assertEqual(response.status_code, 302)
        assert self.test_url and 'redirected' in response.data

    def test_expand_short_link(self):
        response = self.client.get('abcd')
        self.assertEqual(response.status_code, 302)
        assert '/' and 'redirected' in response.data
