from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import json
import hashlib
from .utils import sendTransaction


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)


class Auction(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_price = models.FloatField()
    current_price = models.FloatField()
    image = models.ImageField(upload_to='auction_images/', blank=True, null=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    is_closed = models.BooleanField(default=False)
    data = models.JSONField(blank=True, null=True)
    hash = models.CharField(max_length=66, blank=True, null=True)
    txId = models.CharField(max_length=66, blank=True, null=True)

    def writeOnChain(self):
        json_data = json.dumps(self.data)
        self.hash = hashlib.sha256(json_data.encode('utf-8')).hexdigest()
        self.txId = sendTransaction(self.hash)
        self.save()

class Bid(models.Model):
    bidder = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='bids')
    item = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    amount = models.FloatField()
    datetime = models.DateTimeField(default=timezone.now)

class Transaction(models.Model):
    winner = models.CharField(max_length=50)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    amount = models.FloatField()
    transaction_time = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        profile.email = instance.email
        profile.first_name = instance.first_name
        profile.last_name = instance.last_name
        profile.save()
