import os
from typing import Callable
import pika
# from pika.exchange_type import ExchangeType
from dotenv import load_dotenv


# Load the .env file
load_dotenv()


class CloudAMQPHelper:
    """ The interface between this project and CloudAMQP """

    QUEUE_NAME = "slack_bot_queue"
  
    def __create_connection(self):
        """ Sets up a connection and a channel when this class is instantiated """

        url = os.environ.get("CLOUDAMQP_URL")
        params = pika.URLParameters(url)

        connection = pika.BlockingConnection(params) # Connect to CloudAMQP
        return connection
    
    def __create_channel(
        self, connection: pika.BlockingConnection
    ) -> pika.BlockingConnection:
        channel = connection.channel() # start a channel
        return channel
   
    def consume_message(self, callback: Callable) -> None:
        """ Reads a message published to a queue it's bound to """
        connection = self.__create_connection()
        
        channel = self.__create_channel(connection=connection)

        channel.basic_consume(
            self.QUEUE_NAME,
            callback,
            auto_ack=True
        )

        # start consuming (blocks)
        channel.start_consuming()
        connection.close()


# Create an instance
cloudamqp: CloudAMQPHelper = CloudAMQPHelper()