import requests
import datetime
import time
import asyncio
    
class RedditStocks:
    def __init__(self):
        self.__trending_stocks = None
        self.__last_updated = None
        self.__update_trending_stocks()

    # Update the trending stocks every 15 minutes asynchronously. 15 minutes is the refresh rate of the tradestie api.
    async def __update(self):
        while True:
            # wait 15 minutes
            await asyncio.sleep(900)
            self.__update_trending_stocks()

    # start the update loop
    async def start(self):
        # start the update loop
        await asyncio.gather(self.__update())

    # fetch the trending stocks from the tradestie api
    def __update_trending_stocks(self):
        # fetch data from curl -XGET 'https://tradestie.com/api/v1/apps/reddit'
        trending_stocks_json = requests.get('https://tradestie.com/api/v1/apps/reddit').json()

        if len(trending_stocks_json) > 10:
            self.__trending_stocks = trending_stocks_json[:10]
        else:
            self.__trending_stocks = trending_stocks_json

        # get the comments for each stock
        comments = self.__get_comments([stock['ticker'] for stock in self.__trending_stocks])

        # add comments to trending stocks
        for stock in self.__trending_stocks:
            stock['no_of_comments'] = len(comments[stock['ticker']])
            stock['comments'] = comments[stock['ticker']]

        self.__last_updated = datetime.datetime.utcnow()

    # get comments for a list of tickers
    def __get_comments(self, tickers):
        comments = {}

        start_time = int((datetime.datetime.utcnow() - datetime.timedelta(days=1)).timestamp())
        end_time = int(datetime.datetime.utcnow().timestamp())

        for ticker in tickers:
            pushshift_base_url = f"https://api.pushshift.io/reddit/comment/search/?subreddit=wallstreetbets&over_18=true&created_utc={start_time}-{end_time}&q={ticker}&size=100"

            try:
                response = requests.get(pushshift_base_url)
                comments_json = response.json()
            except:
                print(f"Error fetching comments for {ticker}")
                continue

            data = comments_json['data']

            if len(data) > 0:
                comments[ticker] = dict()

                for comment in data:
                    comments[ticker][comment['created_utc']] = {
                        'author': comment['author'],
                        'body': comment['body'],
                        'score': comment['score'],
                        'permalink': comment['permalink']
                    }

            time.sleep(0.6)

        return comments
    
    # returns a jsonified string containing last updated time and trending stocks
    def get_trending_stocks(self):
        return {self.__last_updated.timestamp() : self.__trending_stocks}