from django.contrib import admin
from .models import CoinList, Issuer, Coin, CoinListCoinAssociative, BlogPost, Currency, Rates, CoinConverter

# Register your models here.
admin.site.register(CoinList)
admin.site.register(Issuer)
admin.site.register(Coin)
admin.site.register(CoinListCoinAssociative)
admin.site.register(BlogPost)
admin.site.register(Currency)
admin.site.register(Rates)
admin.site.register(CoinConverter)