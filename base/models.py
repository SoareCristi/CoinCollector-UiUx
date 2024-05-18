import datetime
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CoinList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    listType = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['completed']
    
class Issuer(models.Model):
    code = models.CharField(max_length=100, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Coin(models.Model):
    url = models.CharField(max_length=300, null=False, blank=False)
    title = models.CharField(max_length=300, null=False, blank=False)
    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, null=False, blank=False)
    minYear = models.IntegerField(null=False, blank=False)
    maxYear = models.IntegerField(null=False, blank=False)
    weight = models.FloatField(null=False, blank=False)
    size = models.FloatField(null=False, blank=False)

    def __str__(self):
        return self.title
    
    class Meta:

        ordering = ['issuer', 'title']

class CoinListCoinAssociative(models.Model):
    coinList = models.ForeignKey(CoinList, on_delete=models.CASCADE, null=False, blank=False)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, null=False, blank=False, default=1)
    isCaught = models.BooleanField(default=False)
    isWanted = models.BooleanField(default=False)

    def __str__(self):
        return self.coin.title
    
    class Meta:
        ordering = ['coinList']

class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    title = models.CharField(max_length=100, null=False, blank=False)
    body = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']

class Currency(models.Model):
    code = models.CharField(max_length=4, null=False, blank=False)

    def __str__(self):
        return self.code
    
    class Meta:
        ordering = ['code']

class Rates(models.Model):
    fromCurrency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='from_currency', null=False, blank=False)
    toCurrency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='to_currency', null=False, blank=False)
    date = models.DateField(null=False, blank=False, default=datetime.date.today)
    rate = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"{self.fromCurrency.code} to {self.toCurrency.code} - {self.date}"
    
    class Meta:
        ordering = ['fromCurrency', 'toCurrency']

class CoinConverter(models.Model):
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, null=False, blank=False)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=False, blank=False)
    amount = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"{self.coin.title} - {self.amount} {self.currency.code}"
    
    class Meta:
        ordering = ['coin', 'currency']