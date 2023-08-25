from django.contrib import admin
from .models import Profile, Auction, Bid, Transaction

admin.site.register(Profile)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Transaction)