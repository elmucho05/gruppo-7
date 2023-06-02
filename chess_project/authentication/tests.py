from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class TestAuthentication(TestCase):

  def setUp(self):
    User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
    User.objects.create_user('doe', 'doe@thebeatles.com', 'doepassword')
  
  def test_auth_user(self):
    """John user with right credentials"""
    user = User.objects.get(username='john')
    credentials = {'username':'john', 'password':'johnpassword'}
    self.assertIsNotNone(authenticate(**credentials), user)
    
    """doe user with right credentials"""
    user = User.objects.get(username='doe')
    credentials = {'username':'doe', 'password':'doepassword'}
    self.assertIsNotNone(authenticate(**credentials), user)
    
    """John user with wrong credentials"""
    user = User.objects.get(username='john')
    credentials = {'username':'john', 'password':'johnpasswordchanged'}
    self.assertIsNone(authenticate(**credentials), user)
