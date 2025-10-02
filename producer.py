import pika
import json
import time
from datetime import datetime

def connect_to_rabbitmq():
    # Establish connection to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    # Declare a queue
    channel.queue_declare(queue='task_queue', durable=True)
    return connection, channel

def send_message(channel, message):
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ))
    # Use green checkmark (✓) with color codes
    print(f"\033[92m ✓ \033[0mSent message {message['id']}: {message['message']} at {datetime.fromtimestamp(message['timestamp']).strftime('%H:%M:%S')}")

def main():
    connection, channel = connect_to_rabbitmq()
    try:
        message_count = 1
        print("\033[94m[Producer Started]\033[0m Press Ctrl+C to stop")
        while True:
            message = {
                'id': message_count,
                'message': f'Message {message_count}',
                'timestamp': time.time()
            }
            send_message(channel, message)
            message_count += 1
            time.sleep(1)  # Wait for 1 second between messages
            
    except KeyboardInterrupt:
        print("\n\033[93m[Producer Stopped]\033[0m")
    finally:
        connection.close()

if __name__ == '__main__':
    main()