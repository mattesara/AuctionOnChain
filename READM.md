Name of project: Auction site

This project allows interacting users to take part in auctions for an electric mobility company.

The user must register with username and password, after which he can immediately participate in the available auctions and place bets.

Auctions have a deadline which, once arrived, declares the user who makes the last bid, therefore the highest, as the winner.

When the auction is closed with a winner, a json file is created with all the details of it and a transaction is made on the blockchain containing that data.

For run the project, before, you need to open the folder project with: cd finalproject and after that, you need to install django in your code editor with:

pip install django (for windows)

For this project you need also Redis, because it's manage the bets, so you need to download Redis and after open the folder and click on redis-server for run(for windows).

You need to install also library like web3 and django-redis, for example using pip.

now you need to make migrations with command in terminal: python manage.py makemigrations

for application the migrations: python manage.py migrate

now, you can run the server and visit the page will appear in your terminal for use the site: python manage.py runserver
