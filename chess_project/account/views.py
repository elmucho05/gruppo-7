from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Sum

from game.models import ChessTrackPlayers

class ViewAccount(LoginRequiredMixin,View):
  login_url = "/authentication/login/"
  redirect_field_name = "redirect_to"

  def get(self, request):
    history = ChessTrackPlayers.objects.filter(player=request.user)
    total   = history.aggregate(Sum('score'))
    context = {
      'history' : history,
      'total' : total
    }
    return render(request, 'account/account.html', context)

  def post(self, request):
    pass