from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
   pass


class Category(models.Model):
    category = models.CharField(max_length=30)
    
    def __str__(self):
        return f"Category: {self.category}"
    
    
class Bid(models.Model):
    bidprice = models.IntegerField(default=0)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userbid")
    
    def __str__(self):
        return f"Bidder: {self.bidder} Price: {self.bidprice}"
    
    
class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    imgURL = models.CharField(max_length=1500, blank=True, null=True)
    start_bid = models.IntegerField()
    date=models.CharField(max_length=100, blank=True, null=True)
    bid = models.ManyToManyField(Bid, blank=True, null=True, related_name="bids")
    isActive = models.BooleanField(default=True)
    listing_category=models.ForeignKey(Category, on_delete=models.CASCADE, related_name="cat", null=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name="w")
    bids = models.ManyToManyField(User, blank=True, related_name="userBid")
    owner=models.ForeignKey(User, on_delete=models.CASCADE, related_name="user", null=True)
    
    def __str__(self):
        return f"Title: {self.title}"
    
    
class Comment(models.Model):
    message = models.CharField(max_length=1000, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="list")
    
    def __str__(self):
        return f"user: {self.user} comment: {self.message}"