from quixstreams import Application
from constants import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
from quixstreams.sinks.community.postgresql import PostgreSQLSink


# Creates a PostgreSQL sink to store incoming data
def create_postgres_sink():
    sink = PostgreSQLSink(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        table_name="XRP",
        schema_auto_update=True,
    )
    return sink


# Extracts relevant cryptocurrency data and converts it into a structured format
def extract_coin_data(message):
    latest_quote = message["quote"]["USD"]  # Extracts price and volume in USD
    return {
        "coin": message["name"],  # Name of the cryptocurrency XRP (Ripple)
        "price_usd": latest_quote["price"],  # Latest price in USD
        "volume_usd": latest_quote["volume_24h"],  # 24-hour trading volume in USD
        "updated": message["last_updated"],  # Timestamp of the latest update}
    }


# Main function that sets up the streaming pipeline
def main():
    # Initialize Quix Streams application
    app = Application(
        broker_address="localhost:9092", # Kafka broker address
        consumer_group="coin_group",
        auto_offset_reset="earliest",
    ) 
    
    # Subscribe to the "coins" Kafka topic and deserialize incoming messages as JSON
    coins_topic = app.topic(
        name="coins", value_deserializer="json"
    ) 

    # Create a streaming dataframe from the topic
    sdf = app.dataframe(topic=coins_topic)
    
    # Apply transformation to extract and structure cryptocurrency data
    sdf = sdf.apply(extract_coin_data)
    
    # Print transformed data to the console 
    sdf.update(lambda coin_data: print(coin_data))

    # Create and attach a PostgreSQL sink to store transformed data
    postgres_sink = create_postgres_sink()
    sdf.sink(postgres_sink)

     # Run the Quix Streams application
    app.run()


if __name__ == "__main__":
    main()
