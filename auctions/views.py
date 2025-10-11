from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import ModelForm, TextInput, Textarea, URLInput, NumberInput
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment

class ListingForm(ModelForm):
	class Meta:
		model = Listing
		fields = ["title", "description", "image", "category"]
		widgets = {
			"title": TextInput(attrs={"autofocus": "autofocus", "placeholder": "Title", "class": "form-control"}),
			"description": Textarea(attrs={"placeholder": "Description", "class": "form-control"}),
			"image": URLInput(attrs={"placeholder": "Image URL (Optional)", "class": "form-control"}),
			"category": TextInput(attrs={"placeholder": "Category (Optional)", "class": "form-control"}),
		}
		labels = {
			"title": "",
			"description": "",
			"image": "",
			"category": "",
		}

class StartBidForm(ModelForm):
	class Meta:
		model = Bid
		fields = ["starting_bid"]
		widgets = {"starting_bid": NumberInput(attrs={"placeholder": "Starting Bid", "class": "form-control"})}
		labels = {"starting_bid": ""}

class CommentForm(ModelForm):
	class Meta:
		model = Comment
		fields = ["comment"]
		widgets = {"comment": Textarea(attrs={"placeholder": "Write a Comment", "class": "form-control", "rows": "4"})}
		labels = {"comment": ""}



def index(request):
	listings = Listing.objects.filter(active=True)
	return render(request, "auctions/index.html", {"listings": listings, "active": True})


def closed(request):
	listings = Listing.objects.filter(active=False)
	return render(request, "auctions/index.html", {"listings": listings, "active": False})


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
def create(request):
	if request.method == "POST":
		form = ListingForm(request.POST)
		starting = StartBidForm(request.POST)
		if form.is_valid() and starting.is_valid():
			listing = form.save(commit=False)
			listing.posted_by = request.user
			bid = starting.save(commit=False)
			listing.bid_details = bid
			bid.save()
			listing.save()
			
			return HttpResponseRedirect(reverse("index"))
		else:
			return render(request, "auctions/create.html", {
				"form": form,
				"start_bid": starting,
				"message": "Invalid Input"
			})

	else:
		return render(request, "auctions/create.html", {
			"form": ListingForm(),
			"start_bid": StartBidForm()
		})


def listing(request, listing_id):
	try:
		listing = Listing.objects.get(id=listing_id)
	except:
		return render(request, "auctions/error.html", {"message": "Page Not Found"})
	
	watchlisted = False
	if request.user.is_authenticated:
		watchlisted = request.user.watchlist.filter(pk=listing.id).exists()
	
	return render(request, "auctions/listing.html", {
		"listing": listing,
		"watchlisted": watchlisted,
		"comment_form": CommentForm(),
		"comments": listing.comments.all()
	})


@login_required
def watchlist(request, listing_id):
	if request.method == "POST":
		try:
			listing = Listing.objects.get(id=listing_id)
		except:
			return render(request, "auctions/error.html", {"message": "Page Not Found"})
		
		if listing.posted_by == request.user:
			return render(request, "auctions/error.html", {"message": "Forbidden"})

		if not listing.active:
			return render(request, "auctions/error.html", {"message": "Bad Request"})

		# Deleting a listing from watchlist
		if request.user.watchlist.filter(pk=listing.id).exists():
			request.user.watchlist.remove(listing)

		# Adding a listing from watchlist
		else:
			request.user.watchlist.add(listing)

		return HttpResponseRedirect(reverse("listing", args=[listing_id]))
	else:
		return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def place_bid(request, listing_id):
	if request.method == "POST":
		try:
			listing = Listing.objects.get(id=listing_id)
		except:
			return render(request, "auctions/error.html", {"message": "Page Not Found"})

		if listing.posted_by == request.user:
			return render(request, "auctions/error.html", {"message": "Forbidden"})

		if not listing.active:
			return render(request, "auctions/error.html", {"message": "Bad Request"})

		try:
			bid = listing.bid_details
			bid_price = float(request.POST["current_bid"])
			print(bid_price, type(bid_price))

			if bid.current_bid == 0:
				if bid_price < bid.starting_bid:
					raise ValueError
			else:
				if bid_price <= bid.current_bid:
					raise ValueError
		except:
			return render(request, "auctions/listing.html", {
				"listing": listing,
				"watchlisted": request.user.watchlist.filter(pk=listing.id).exists(),
				"message": "Invalid Bid",
			})

		bid.current_bid = bid_price
		bid.highest_bidder = request.user
		bid.save()

		return render(request, "auctions/listing.html", {
			"listing": listing,
			"watchlisted": request.user.watchlist.filter(pk=listing.id).exists(),
			"success": "Bid Placed",
		})
	else:
		return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def close_bid(request, listing_id):
	if request.method == "POST":
		try:
			listing = Listing.objects.get(id=listing_id)
		except:
			return render(request, "auctions/error.html", {"message": "Page Not Found"})

		if listing.posted_by != request.user:
			return render(request, "auctions/error.html", {"message": "Forbidden"})

		if not listing.active:
			return render(request, "auctions/error.html", {"message": "Bad Request"})

		listing.active = False
		listing.watchlisted_by.clear()
		listing.save()
	
	return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def comment(request, listing_id):
	if request.method == "POST":
		try:
			listing = Listing.objects.get(id=listing_id)
		except:
			return render(request, "auctions/error.html", {"message": "Page Not Found"})

		if listing.posted_by == request.user:
			return render(request, "auctions/error.html", {"message": "Forbidden"})

		if not listing.active:
			return render(request, "auctions/error.html", {"message": "Bad Request"})

		form = CommentForm(request.POST)
		
		print("form recieved")

		if form.is_valid():
			print("form is valid")
			comment = form.save(commit=False)
			comment.posted_by = request.user
			comment.listing = listing
			comment.save()

	return HttpResponseRedirect(reverse("listing", args=[listing_id]))
