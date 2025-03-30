import time
from quixstreams import Application
from constants import COINMARKET_API
from requests import Session
import json


# Function to make a GET request to the CoinMarketCap API and retrieve the latest data for a specific cryptocurrency
def get_latest_coin_data(target_symbol="XRP"):
    # CoinMarketCap API
    API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    # Target symbol for the cryptocurrency we want (XRP in this case)
    parameters = {"symbol": target_symbol, "convert": "USD"}

    headers = {
        "Accepts": "application/json",  # Accepts: This header tells the server that the client expects a JSON response.
        "X-CMC_PRO_API_KEY": COINMARKET_API,  # X-CMC_PRO_API_KEY: This is an API key used to authenticate the request to the CoinMarketCap API. You must have a valid key to access the API.
    }

    # Creating a session object to manage the request
    session = Session()
    session.headers.update(headers)

    # Making the API Request to the coinmarketcap API
    response = session.get(
        API_URL, params=parameters
    )  # Sending GET request with parameters
    return json.loads(response.text)["data"][
        target_symbol
    ]  # Returning the response as JSON for the target symbol


# Function for our application, starts the app

def main():
    # Create an instance of the Quix application and connect to the Kafka broker
    app = Application(broker_address="localhost:9092", consumer_group="coin_group")
    # Define the Kafka topic "coins" where the data will be sent
    coins_topic = app.topic(name="coins", value_serializer="json")

    # Start the producer (this part is responsible for sending data to Kafka)
    with app.get_producer() as producer:  # The while loop will run every 40 seconds to fetch updates
        while True:
            # Fetch the latest coin data (XRP)
            coin_latest = get_latest_coin_data("XRP")

            # Serialize the data to prepare it for Kafka (key-value format)
            kafka_message = coins_topic.serialize(
                key=coin_latest["symbol"], value=coin_latest
            )

            # Print the key and price of the coin being produced to Kafka for debugging or logging
            print(
                f"Produce event with key = {kafka_message.key}, price = {coin_latest['quote']['USD']['price']}"
            )
            # Produce the message to the Kafka topic
            producer.produce(
                topic=coins_topic.name, key=kafka_message.key, value=kafka_message.value
            )
            # Wait for 40 seconds before fetching the next update
            time.sleep(40)

# If the script is run directly, start the application
if __name__ == "__main__":

    main()
