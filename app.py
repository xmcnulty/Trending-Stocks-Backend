from flask import Flask, request, jsonify
from reddit_stocks import RedditStocks
import asyncio
import threading

app = Flask(__name__)

reddit_stocks = RedditStocks()

def run_app():
    print("Starting app...")
    app.run(debug=True)

@app.route('/api/v1/trending_stocks', methods=['GET'])
def aggregate_data():
    return jsonify(reddit_stocks.get_trending_stocks())

if __name__ == '__main__':
    run_app()