from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.utils.html import strip_tags

from .forms import RegistrationForm

class ViewLogin(View):
  form = AuthenticationForm()
  context = { 'form': form }

  def get(self, request):
    return render(request, "authentication/login.html", self.context)

  def post(self, request):
    self.form = AuthenticationForm(request.POST, data=request.POST)
    username = self.form.data.get('username')
    password = self.form.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
      login(request, user)
      messages.success(request, f'Login completato con successo')
      
      #?redirect_to=/account/
      redirect_to = request.GET.get('redirect_to', 'view_home')
      return redirect(redirect_to)
    
    for e in self.form.errors.values():
      messages.error(request, f'{strip_tags(e)}')
    return redirect('view_login')

class ViewSignUp(View):
  form = RegistrationForm()
  context = { 'form': form }

  def get(self, request):
    return render(request, "authentication/signup.html", self.context)

  def post(self, request):
    self.form = RegistrationForm(request.POST)

    if self.form.is_valid():
      user = self.form.save()
      login(request, user)
      messages.success(request, f'Registrazione completata!') 
      return redirect('view_home')
    
    for e in self.form.errors.values():
      print(e)
      messages.error(request, f'{strip_tags(e)}')
    return redirect('view_signup')

def view_logout(request):
  logout(request)
  return redirect("view_home")
  