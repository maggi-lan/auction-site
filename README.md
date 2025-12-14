# Auction Platform

This is a mini backend clone of eBay's auction system built in Django. I have only focused on implementing the backend since I did this project only to learn Django.

## Features

- **User Authentication**: Register, login, and logout functionality
- **Create Listings**: Users can create auction listings with title, description, starting bid, image URL, and category
- **Bidding System**: Place bids on active listings with validation to ensure bids are higher than current price
- **Watchlist**: Add/remove listings to personal watchlist for easy tracking
- **Close Auctions**: Listing owners can close their auctions and determine winners
- **Comments**: Users can comment on active listings
- **Active/Closed Listings**: Separate views for browsing active and closed auctions

## Tech Stack

- **Backend**: Django 5.2.5
- **Database**: SQLite3
- **Frontend**: Basic HTML templates

## Models

- **User**: Extended Django AbstractUser with watchlist functionality
- **Listing**: Auction listings with title, description, image, category, and status
- **Bid**: Tracks starting bid, current bid, and highest bidder
- **Comment**: User comments on listings

## Project Structure

```
├── auctions/              # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # View functions and business logic
│   ├── urls.py            # URL routing
│   ├── templates/         # HTML templates
│   └── static/            # CSS files
├── commerce/              # Project configuration
│   ├── settings.py        # Django settings
│   └── urls.py            # Root URL configuration
└── manage.py              # Django management script
```

## Key Features Implementation

### Bid Validation
- First bid must be at least equal to starting bid
- Subsequent bids must be higher than current bid
- Users cannot bid on their own listings

### Watchlist Management
- Users can add/remove listings from watchlist
- Watchlist automatically cleared when auction closes
- Cannot watchlist own listings

### Auction Closure
- Only listing owner can close auction
- Winner is the highest bidder at closure
- Closed auctions remain viewable but inactive
