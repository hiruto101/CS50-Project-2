from django.contrib import admin
from .models import User, Listing, Category, Bid, Comment
# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    filter_horizontal = ("watchlist","bids")    

admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Comment)