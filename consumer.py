import pika
import json
import time
from datetime import datetime

def connect_to_rabbitmq():
    # Establish connection to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    # Declare the same queue as producer
    channel.queue_declare(queue='task_queue', durable=True)
    return connection, channel

def callback(ch, method, properties, body):
    message = json.loads(body)
    # Use blue arrow for received
    print(f"\033[94m → \033[0mReceived message {message['id']}: {message['message']}")
    time.sleep(1)  # Simulate processing
    # Use green checkmark for completed
    print(f"\033[92m ✓ \033[0mProcessed message {message['id']}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection, channel = connect_to_rabbitmq()
    
    # Fair dispatch - don't give more than one message to a worker at a time
    channel.basic_qos(prefetch_count=1)
    
    # Set up consumer
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    print('\033[94m[Consumer Started]\033[0m Press Ctrl+C to stop')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n\033[93m[Consumer Stopped]\033[0m")
    finally:
        connection.close()

if __name__ == '__main__':
    main()