from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmailUserCreationForm, BidForm
from django.contrib.auth import login, logout
from .models import *
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
import redis
import time

def register(request):                                                         #registration view that it uses a class that inherits from Django's UserCreationForm
    if request.method == 'POST':
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'homepage.html')
    else:
        form = EmailUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):                                                      #login view uses Django's form AuthenticationForm
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('homepage')
    else:
        form = AuthenticationForm()
    return render(request, 'login_view.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login_view')


def homepage(request):
    return render(request, 'homepage.html')

def auction_list(request):                                                    #total auctions list order by datetime
    auctions = Auction.objects.all().order_by('start_time')
    return render(request, 'auction_list.html', {'auctions': auctions})

def auction_detail(request, pk):                                   #Auction's detail view 
    auction = get_object_or_404(Auction, pk=pk)
    now = timezone.now()
    auction_id = auction.id
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)       #redis connection
    cache_key = f"bids:{auction_id}"

    if now >= auction.end_time and not auction.is_closed:                     #cycle that closes the auctions with the time expired
        auction.refresh_from_db()
        auction.is_closed = True
        if auction.bids.exists():                                             #check if the auction has any offers
            latest_bid_serialized = redis_client.zrevrange(cache_key, 0, 0, withscores=True)
            latest_bid = json.loads(latest_bid_serialized[0][0].decode('utf-8'))                            #obtaining last bid from Redis database
            json_data = {'Auction ID': auction_id,                                                          #save on Redis the closed auction with json
                         'Auction item': auction.title,
                         'Starting price': auction.starting_price,
                         'Selling price': latest_bid['amount'],
                         'Start auction': auction.start_time,
                         'Selling datetime': auction.end_time,
                         'Winner': latest_bid['bidder_username'],
                         'Email': latest_bid['bidder_email'],
                         'First name': latest_bid['bidder_first_name'],
                         'Last name': latest_bid['bidder_last_name']
                         }
            formatted_date = json_data["Start auction"].isoformat()
            json_data["Start auction"] = formatted_date
            formatted_date = json_data["Selling datetime"].isoformat()
            json_data["Selling datetime"] = formatted_date
            file = f'auction_details_{auction_id}.json'
            with open(file, 'w') as json_file:                                #json file transfer for transaction function on blockchain 'writeOnChain'
                json.dump(json_data, json_file, indent=9)                     
            auction.data = json_data
            auction.writeOnChain()
            Transaction.objects.create(                                       #info transaction
                winner=latest_bid['bidder_username'],
                auction=auction,
                amount=latest_bid['amount'],
                transaction_time=timezone.now
            )
        auction.save()

    bid_form = BidForm(request.POST or None, instance=Bid(item=auction))                #BidForm, it allows you to interact and make bets

    if request.method == 'POST':
        if bid_form.is_valid():                                                         #check if entered form is valid
            if not auction.is_closed:                                                   #only if the auction is open user can place bids
                profile = Profile.objects.get(user=request.user)                        #register user profile for bid
                bid = bid_form.save(commit=False)            
                bid.bidder = profile                                                    #bid data in json for save on Redis database
                bid_data = {
                    'bidder_username': bid.bidder.user.username,
                    'bidder_email': bid.bidder.user.email,
                    'bidder_first_name': bid.bidder.user.first_name,
                    'bidder_last_name': bid.bidder.user.last_name,
                    'amount': bid.amount,
                    'datetime': bid.datetime.strftime('%Y-%m-%d %H:%M:%S')
                }
                serialized_data = json.dumps(bid_data)                                  
                redis_client.zadd(cache_key, {serialized_data: time.mktime(bid.datetime.timetuple())})    #save on Redis
                latest_bid_serialized = redis_client.zrevrange(cache_key, 0, 0, withscores=True)          #obtaining last bid from Redis database for save new bid for current price
                latest_bid = json.loads(latest_bid_serialized[0][0].decode('utf-8'))                      
                auction.current_price = latest_bid['amount']
                auction.save()
                bid.save()

    time_remaining = max(auction.end_time - now, timezone.timedelta())                         #auction timer from script in html

    transaction = Transaction.objects.filter(auction=auction).last()                           #view of last bids placed by users
    last_bids_serialized = redis_client.zrevrange(cache_key, 0, 2)                             #search for last bids on Redis to add to list 'last bids'
    last_bids = []

    for last_bid_serialized in last_bids_serialized:                                           #obtaining last bids from Redis and add them to the list
        bid = json.loads(last_bid_serialized.decode('utf-8'))
        last_bids.append({
            'bidder_username': bid['bidder_username'],
            'amount': bid['amount']
        })

    context = {
        'auction': auction,
        'time_remaining': time_remaining,
        'bid_form': bid_form,
        'transaction': transaction,
        'last_bids': last_bids
    }

    return render(request, 'auction_detail.html', context)

def transaction_detail(request, pk):                                                           #transaction detail views information of transaction
    auction = get_object_or_404(Auction, pk=pk)                                                #and tx of blockchain transaction
    transaction = get_object_or_404(Transaction, pk=pk)
    link = f"https://sepolia.etherscan.io/tx/{auction.txId}"
    return render(request, 'transaction_detail.html', {'transaction': transaction, 'link': link})
