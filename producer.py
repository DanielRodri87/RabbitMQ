import pika
import json
import time
import uuid
from datetime import datetime
import random
import os
import cv2
import numpy as np
import glob

def connect_to_rabbitmq():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()
    
    # Declare topic exchange
    channel.exchange_declare(exchange='image_exchange', exchange_type='topic')
    return connection, channel

def get_random_image():
    dataset_path = 'dataset-face/train/*/*.jpg'  # Path to all training images
    all_images = glob.glob(dataset_path)
    if not all_images:
        raise Exception("No images found in dataset")
    return random.choice(all_images)

def send_message(channel, routing_key):
    message_id = str(uuid.uuid4())
    image_path = get_random_image()
    
    message = {
        'id': message_id,
        'type': routing_key,
        'image_path': image_path,
        'emotion': os.path.basename(os.path.dirname(image_path)),  # Get emotion from folder name
        'timestamp': time.time()
    }
    
    channel.basic_publish(
        exchange='image_exchange',
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print(f"Published -> key: {routing_key} id: {message_id}")

def main():
    connection, channel = connect_to_rabbitmq()
    try:
        print("\033[94m[Producer Started]\033[0m Press Ctrl+C to stop")
        while True:
            # Randomly choose between face and team messages
            routing_key = random.choice(['face', 'team'])
            send_message(channel, routing_key)
            time.sleep(0.2)  # 5 messages per second
            
    except KeyboardInterrupt:
        print("\n\033[93m[Producer Stopped]\033[0m")
    finally:
        connection.close()

if __name__ == '__main__':
    main()