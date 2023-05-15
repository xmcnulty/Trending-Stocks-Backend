import requests
import datetime
import time
import asyncio
import threading
    
class RedditStocks:

    def __init__(self):
        self.__trending_stocks = dict()
        self.__stock_comments = dict() # dictionary with ticker as key to comments as value
        self.__last_updated = None
        self.__update_trending_stocks()

        async def update_task():
            await self.__update()

        self.__loop = asyncio.new_event_loop()

        def loop_runner():
            asyncio.set_event_loop(self.__loop)
            self.__loop.run_until_complete(update_task())

        self.__update_thread = threading.Thread(target=loop_runner)
        self.__update_thread.start()

    # Update the trending stocks every 15 minutes asynchronously. 15 minutes is the refresh rate of the tradestie api.
    async def __update(self):
        while True:
            # wait 15 minutes
            await asyncio.sleep(900)
            self.__update_trending_stocks()

    # fetch the trending stocks from the tradestie api
    def __update_trending_stocks(self):
        # fetch data from curl -XGET 'https://tradestie.com/api/v1/apps/reddit'
        trending_stocks_json = requests.get('https://tradestie.com/api/v1/apps/reddit').json()

        trending_size = 10 if len(trending_stocks_json) > 10 else len(trending_stocks_json)

        for x in range(trending_size):
            self.__trending_stocks[trending_stocks_json[x]['ticker']] = trending_stocks_json[x]

        # get the comments for each stock
        self.__get_comments(self.__trending_stocks.keys())

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

                    self.__trending_stocks[ticker]['no_of_comments'] = len(comments[ticker])
                    
                    self.__stock_comments[ticker] = comments
                else:
                    self.__stock_comments[ticker] = {}
            except Exception as err:
                print(f"Error fetching comments for {ticker}")
                continue


            time.sleep(0.6)
    
    # returns a jsonified string containing last updated time and trending stocks
    def get_trending_stocks(self, with_comments=False):
        if not with_comments:
            return {self.__last_updated.timestamp() : self.__trending_stocks}
        else:
            # for each stock in trending stocks, add the comments and return the new dictionary
            trending_stocks_with_comments = {}

            for stock in self.__trending_stocks:
                trending_stocks_with_comments[stock['ticker']] = {
                    'comments': self.__stock_comments[stock['ticker']],
                    'no_of_comments': stock['no_of_comments'],
                    'sentiment': stock['sentiment'],
                    'sentiment_score': stock['sentiment_score']
                }

            return {self.__last_updated.timestamp() : trending_stocks_with_comments}

    
    # attempts to get comments for a ticker. returns none if no comments are found
    def get_comments(self, ticker):
        try:
            return self.__stock_comments[ticker]
        except:
            return None