from flask import Flask, request, jsonify
from reddit_stocks import RedditStocks
import asyncio
import threading

app = Flask(__name__)

reddit_stocks = RedditStocks()

def run_app():
    # create a task for the start() method
    #task = asyncio.create_task(reddit_stocks.start())

    # run the task in the background thread
    #def run_loop(loop):
    #    asyncio.set_event_loop(loop)
    #    loop.run_until_complete(task)

    #thread = threading.Thread(target=run_loop, args=(asyncio.new_event_loop(),))
    #thread.start()

    print("Starting app...")
    app.run(debug=True)

@app.route('/api/v1/trending_stocks', methods=['GET'])
def aggregate_data():
    return jsonify(reddit_stocks.get_trending_stocks())

if __name__ == '__main__':
    run_app()