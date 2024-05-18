from typing import Any
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.http import JsonResponse
import datetime
import requests

from django.contrib.auth.views import LoginView
from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login

from django.views.generic.edit import FormView
from django import forms

from .models import BlogPost, CoinList, Coin, CoinListCoinAssociative, Currency, Rates, CoinConverter

# Create your views here.
class CoinListView(LoginRequiredMixin, ListView):
    model = CoinListCoinAssociative
    template_name = 'base/coinlist.html'
    context_object_name = 'coinlist_associative'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['coinlist_associative'] = context['coinlist_associative'].filter(coinList__user = self.request.user)
        if context['coinlist_associative'].exists():
            context['coinlist_name'] = context['coinlist_associative'][0].coinList.name
        context['count'] = context['coinlist_associative'].filter(isCaught=True).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            aux = context['coinlist_associative'].filter(coin__title__icontains=search_input)
            if aux.exists() == False:
                context['coinlist_associative'] = context['coinlist_associative'].filter(coin__issuer__name__icontains=search_input)
            else:
                context['coinlist_associative'] = aux
        context['search_input'] = search_input 

        return context
    
class UpdateIsCaughtView(LoginRequiredMixin, View):

    def post(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            entry_id = request.POST.get('entry_id')
            is_caught = request.POST.get('is_caught')
            
            if is_caught == 'true':
                is_caught = True
            else:
                is_caught = False

            try:
                entry = CoinListCoinAssociative.objects.get(id=entry_id)
                entry.isCaught = bool(is_caught)
                entry.save()
                return JsonResponse({'message': 'Success'})
            except CoinListCoinAssociative.DoesNotExist:
                return JsonResponse({'message': 'Entry not found'})
        else:
            return JsonResponse({'message': 'Invalid request'})

class RegisterView(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('list') #de modif

    def create_CoinList(self, user):
        new_CoinList = CoinList(user = user,
                                name = "Full Coin List: " + user.username
                              )
        new_CoinList.save()

        coins = Coin.objects.all()   
        for coin in coins:
            new_CoinList_Coin_Associative = CoinListCoinAssociative(coinList = new_CoinList,
                                                                    coin = coin,
                                                                    isCaught = False,
                                                                    isWanted = False
                                                                    )
            new_CoinList_Coin_Associative.save()

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            self.create_CoinList(user)
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("list")
        return super(RegisterView, self).get(*args, **kwargs)


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('list')
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('list')
    
class CoinDetailView(DetailView):
    model = Coin
    context_object_name = 'coin'
    template_name = 'base/coin_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'base/blogpost_list.html'
    context_object_name = 'blogposts'

class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'base/blogpost.html'
    context_object_name = 'blogpost'
    
class CurrencyConversionForm(forms.Form):
    from_currency = forms.ModelChoiceField(queryset=Currency.objects.filter(code='EUR'), empty_label=None)
    to_currency = forms.ModelChoiceField(queryset=Currency.objects.all(), empty_label=None)
    amount = forms.FloatField()

class CoinValueForm(forms.Form):
    coin = forms.ModelChoiceField(queryset=Coin.objects.all(), empty_label=None)
    currency = forms.ModelChoiceField(queryset=Currency.objects.all(), empty_label=None)

class CurrencyConversionView(View):
    template_name = 'base/currency_conversion.html'

    def get(self, request, *args, **kwargs):
        print('real get')
        currency_conversion_form = CurrencyConversionForm()
        coin_value_form = CoinValueForm()
        return render(request, self.template_name, {
            'currency_conversion_form': currency_conversion_form,
            'coin_value_form': coin_value_form,
        })

    def post(self, request, *args, **kwargs):
        print('real post')
        currency_conversion_form = CurrencyConversionForm(request.POST)
        coin_value_form = CoinValueForm(request.POST)

        converted_amount = None
        if currency_conversion_form.is_valid():
            # Perform currency conversion logic here
            from_currency = currency_conversion_form.cleaned_data['from_currency']
            to_currency = currency_conversion_form.cleaned_data['to_currency']
            amount = currency_conversion_form.cleaned_data['amount']
            if from_currency == to_currency:
                converted_amount = amount
                return render(request, self.template_name, {
                    'coin_value_form': coin_value_form,
                    'currency_conversion_form': currency_conversion_form,
                    'converted_amount': converted_amount,
                })

            # Fetch the conversion rate from the database
            rate = Rates.objects.filter(fromCurrency=from_currency, toCurrency=to_currency).first()

            if rate:
                converted_amount = amount * rate.rate
            else:
                converted_amount = None
            
            return render(request, self.template_name, {
                'coin_value_form': coin_value_form,
                'currency_conversion_form': currency_conversion_form,
                'converted_amount': converted_amount,
            })

        coin_value = None
        if coin_value_form.is_valid():
            # Perform coin value calculation logic here
            coin = coin_value_form.cleaned_data['coin']
            to_currency = coin_value_form.cleaned_data['currency']

            # Fetch the value of the coin in the selected currency from the database
            coin_converter = CoinConverter.objects.filter(coin=coin).first()
            from_currency = coin_converter.currency

            if from_currency == to_currency:
                coin_value = coin_converter.amount
                return render(request, self.template_name, {
                    'coin_value_form': coin_value_form,
                    'currency_conversion_form': currency_conversion_form,
                    'coin_value': coin_value,
                })

            rate = Rates.objects.filter(fromCurrency=from_currency, toCurrency=to_currency).first()

            if coin_converter:
                coin_value = coin_converter.amount * rate.rate
            else:
                coin_value = None

            return render(request, self.template_name, {
                'coin_value_form': coin_value_form,
                'currency_conversion_form': currency_conversion_form,
                'coin_value': coin_value,
            })

        return render(request, self.template_name, {
                'currency_conversion_form': currency_conversion_form,
                'coin_value_form': coin_value_form,
            })

class CurrencyConversionProxyView(LoginRequiredMixin, View):
    template_name = 'base/currency_conversion.html'
    realCurrencyConversionView = CurrencyConversionView()

    def get(self, request, *args, **kwargs):
        print('proxy get')

        rate = Rates.objects.first()
        if rate.date != datetime.date.today():
            print('updating rates')
            api_key = '07d7e59b310069c719f18938a5be5edc'
            base_url = str.__add__('http://data.fixer.io/api/latest?access_key=', api_key)

            currency = Currency.objects.filter(code='EUR').first()
            rates_data = requests.get(base_url + '&base=' + currency.code).json()['rates']
            rates = Rates.objects.filter(fromCurrency=currency)
            for rate in rates:
                rate.rate = rates_data[rate.toCurrency.code]
                rate.date = datetime.date.today()
                rate.save()
        return self.realCurrencyConversionView.get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print('proxy post')
        return self.realCurrencyConversionView.post(request, *args, **kwargs)