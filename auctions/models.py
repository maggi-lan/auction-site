from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watchlisted_by")


class Listing(models.Model):
	posted_by = models.ForeignKey("User", on_delete=models.CASCADE, related_name="listings")
	title = models.CharField(max_length=200)
	description = models.TextField()
	bid_details = models.OneToOneField("Bid", on_delete=models.CASCADE, related_name="listing")
	image = models.URLField(blank=True)
	category = models.CharField(blank=True, max_length=100)


class Bid(models.Model):
	starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
	current_bid = models.DecimalField(max_digits=10, null=True, decimal_places=2)
	highest_bidder = models.ForeignKey("User", blank=True, on_delete=models.CASCADE, related_name="winning_bids")
	opened = models.BooleanField(default=True)


class Comment(models.Model):
	posted_by = models.ForeignKey("User", on_delete=models.CASCADE, related_name="comments")
	listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="comments")
	comment = models.TextField()
