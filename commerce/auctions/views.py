from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max, F,Case, When,Value, CharField
from django.db.models.functions import Coalesce
from datetime import datetime

from .models import User, Listing, Category, Bid, Comment


def index(request):
    if request.method == "POST":
        getCategory = request.POST.get("category", "all")
        category = Category.objects.all()
        #this is new
        listings = Listing.objects.filter(isActive = True).annotate(
            max_bid=Coalesce(Max("bid__bidprice"), F("start_bid"))
        )
        
        new_list=listings.filter(listing_category__category=getCategory)
      
        
        if getCategory.lower() == "all":
            new_list = listings
        
        return render(request, "auctions/index.html", {
            "listings":new_list,
            "category":category,
            "getCategory":getCategory
        })
    else:
        
        category=Category.objects.all()
        listings = Listing.objects.filter(isActive = True).annotate(
        max_bid=Coalesce(Max("bid__bidprice"), F("start_bid"))
        )
        
        return render(request, "auctions/index.html",{
            "listings":listings,
            "category":category,
            "getCategory":"all"
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def new_list(request):
    if request.method == "POST":
        category = Category.objects.all()
        
        title = request.POST.get("title")
        imgURL = request.POST.get("imgURL")
        desc = request.POST.get("desc")
        price = request.POST.get("price")
        listing_cat = Category.objects.get(category=request.POST.get("category"))
        listing_user = request.user
        listing_date = datetime.now()
        
        if(category != "" ):
            new_listing = Listing(title=title, 
                                  description=desc, 
                                  imgURL=imgURL, 
                                  start_bid=price,
                                  date =  listing_date.strftime("created on:""%B ""%d,""%Y,""%I:""%M""%p"),
                                  isActive=True,
                                  listing_category=listing_cat, 
                                  owner=listing_user)
            new_listing.save()
            
            return HttpResponseRedirect(reverse(index))

    else:
        category = Category.objects.all()
        user = request.user
        return render(request, "auctions/new_list.html", {
            "category":category,
            "user":user
            })
 

@login_required
def editlist(request, id):
    
    listing = Listing.objects.annotate(
        max_bid=Coalesce(Max("bid__bidprice"), F("start_bid"))
    ).get(pk=id)
    category = Category.objects.all()
    getCategory = listing.listing_category.category # this is how to access the value from foreign key
    
    return render(request, "auctions/editlist.html", {
        "listing":listing,
        "category":category,
        "getCategory":getCategory
    })


@login_required
def editsave(request, id):
    try:
        if request.method == "POST":
            listing = Listing.objects.get(pk = id)
            print("hello",listing)
            title = request.POST.get("title", listing.title)
            imgURL = request.POST.get("imgURL") or listing.imgURL
            desc = request.POST.get("desc", listing.description)
            category = request.POST.get("category", listing.listing_category.category)

            # Assign value
            listing.title = title
            listing.imgURL = imgURL
            listing.description = desc
            listing.category = category
            
            # Save the updated listing object
            listing.save()
            
            return HttpResponseRedirect(reverse("view_list", args=[id]))
        
    except Listing.DoesNotExist:
        print("Listing does not exist")
        
           
@login_required      
def mywatchlist(request):
    
    if request.method == "POST":
        userID = request.user
        listing = Listing.objects.filter(watchlist = userID)
        category = Category.objects.all()
        fil = request.POST.get("category")
        filteredList = getFilter(listing, fil)
        
 
        return render(request, "auctions/watchlist.html", {
            "listings":filteredList,
            "category":category,
            "getCategory":fil
        })
    
    # Method is GET
    listing = Listing.objects.filter(watchlist = request.user)
    category = Category.objects.all()
    return render(request, "auctions/watchlist.html", {
        "listings":listing,
        "category":category
    })


@login_required
def my_list(request):
    
    if request.method == "POST":
        
        listing = Listing.objects.filter(owner = request.user)
        category = Category.objects.all()
        fil = request.POST.get("category")
        
        filteredList = getFilter(listing, fil)
        
        return render(request, "auctions/my_list.html", {
            "listings":filteredList,
            "category":category,
            "getCategory":fil
        })
        
    else: #GET
        listing = Listing.objects.filter(owner = request.user)
        category = Category.objects.all()
        
        return render(request, "auctions/my_list.html", {
            "listings":listing,
            "category":category,
            "fil": "all"
        })

  
def view_list(request, id): # view individual active list
    isWinner = False
    if request.method == "POST":
        getComment = request.POST.get("comment")
        getId = request.POST.get("list_id")
        
        #check if there is a new comment
        if getComment:
            newComment = addComment(request, getId, getComment)
        #NEW KNOWLEDGE listing with annotate
        listing = Listing.objects.annotate(
            max_bid = Coalesce(Max("bid__bidprice"), 0),
        ).get(pk=id)
        # get the highest bidder
        highest_bidder = Bid.objects.filter(listing__id=id).order_by('-bidprice').first() # get the highest bidder
        # check if there is a bid and if the user is the winner
        if not listing.isActive and listing.bid:
            if request.user.username == highest_bidder.bidder:
                isWinner = True
        # 
        isUserWatching = request.user in listing.watchlist.all()
        message = listing.list.all().order_by('-pk') # All the comment messages
        if message == None:
            message = "No comment"
        
        return render(request,"auctions/listing.html", {
            "listing":listing,
            "highestBidder":highest_bidder,
            "isUserWatching":isUserWatching,
            "messages":message,
            "isWinner":isWinner
         })

    else:
        listing = Listing.objects.annotate(
            max_bid = Coalesce(Max("bid__bidprice"), 0),
        ).get(pk=id)
        curr_user = request.user.username
        highest_bidder = Bid.objects.filter(listing__id=id).order_by('-bidprice').first()
        if not listing.isActive and highest_bidder:
            if request.user.username == highest_bidder.bidder.username:
                isWinner = True
        isUserWatching = request.user in listing.watchlist.all()
        message = listing.list.all().order_by('-pk') # comments by users sorted 
    
        if message == None:
            message = "No comment"
        
        return render(request,"auctions/listing.html", {
            "listing":listing,
            "highestBidder":highest_bidder,
            "isUserWatching":isUserWatching,
            "messages":message,
            "isWinner":isWinner
        })
        
        
@login_required        
def removewatchlist(request, id):
    
    if request.method == "POST":
        user_id = request.POST.get("user")
        listing = Listing.objects.get(pk = id)
        listing.watchlist.remove(request.user)
        
        return HttpResponseRedirect(reverse("view_list", args=[id]))
      
        
@login_required        
def addwatchlist(request, id):
    
    if request.method == "POST":
        user_id = request.POST.get("user")
        listing = Listing.objects.get(pk = id)
        listing.watchlist.add(request.user)

    return HttpResponseRedirect(reverse("view_list", args=[id]))
        
# PLACE BID 
@login_required     
def placeBid(request, id):
    if request.method == "POST":
        try:
            bid = int(request.POST.get("bid")) # bid price
            bidder = User.objects.get(pk = request.user.id)
            status = False
            curr_list = Listing.objects.get(pk = id)
            has_bid = Bid.objects.filter(bidder=bidder, listing=curr_list).exists() # check if user has a bid
                         
            # check for highest bid
            if not curr_list.bid.exists(): # if no bid is placed yet
                if curr_list.start_bid <= bid:
                    new_bid = Bid.objects.create(bidprice=bid, bidder=bidder, listing=curr_list)
                    curr_list.bid.add(new_bid)
                    status = True
                else:
                    message = "Bid cannot be lower or equal than starting bid"      
            elif curr_list.bid.aggregate(Max('bidprice'))['bidprice__max'] < bid:
                if has_bid: # update the user bid
                    Bid.objects.filter(bidder=bidder, listing=curr_list).update(bidprice = bid)
                else:
                    new_bid = Bid.objects.create(bidprice=bid, bidder=bidder, listing=curr_list)
                    curr_list.bid.add(new_bid)
                    status = True
            else:
                message = "Bid is lower than highest bid"
           
            # add to the user's watchlist if not yet added 
            if bidder not in curr_list.watchlist.all():
                curr_list.watchlist.add(bidder)
                
            # pass this data
            highest_bidder = Bid.objects.filter(listing__id=id).order_by('-bidprice').first()
            listing = Listing.objects.annotate(
                max_bid = Coalesce(Max("bid__bidprice"), 0),
            ).get(pk=id)
                          
            return render(request, "auctions/listing.html", {
                "listing":listing,
                "highestBidder":highest_bidder,
                "message":message,
            })
            
        except Exception as e:
            message = "Error"
            print(e)
            return HttpResponseRedirect(reverse("view_list", args=[id]))
            
    #return HttpResponseRedirect(reverse("view_list", args=[id]))
    
    
@login_required    
def addComment(request, id, comment):
    
    listing = Listing.objects.get(id=int(id))
    newComment = Comment.objects.create(message=comment, user=request.user, listing=listing)
    newComment.save()


@login_required
def closeList(request):
    listid = request.POST.get("listid")
    print(listid)
    listing = Listing.objects.get(pk = listid)
    listing.isActive = False
    listing.save()
    
    return HttpResponseRedirect(reverse("my_list"))

    
def getFilter(currlist, category, isActive = None):

    if category.lower() == "all":
        if isActive == True:
            listing = currlist.filter(isActive = True)   
        elif isActive == False:
            listing = currlist.fitler(isActive = False)
        else:
             listing = currlist
    else:
        listing = currlist
        filteredList = []
        for fList in listing:
            if fList.listing_category.category.lower() == category.lower():
                filteredList.append(fList)
        listing = filteredList

    return listing


def getPrice():
    pass