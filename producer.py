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

def get_random_image(type_key):
    try:
        if type_key == 'face':
            dataset_path = 'dataset-face/train/*/*.jpg'
        else:  # team
            dataset_path = 'dataset-team/*/*.png'
        
        all_images = glob.glob(dataset_path)
        if not all_images:
            return None
        return random.choice(all_images)
    except Exception as e:
        print(f"Error getting image for {type_key}: {e}")
        return None

class MessageProducer:
    def __init__(self):
        self.face_count = 0
        self.max_faces = 10
        self.face_completed = False

    def send_message(self, channel, routing_key):
        # After face processing is complete, only send team messages
        if self.face_completed:
            routing_key = 'team'
        
        # Skip if we already sent max faces
        if routing_key == 'face' and self.face_count >= self.max_faces:
            self.face_completed = True
            routing_key = 'team'
            
        message_id = str(uuid.uuid4())
        image_path = get_random_image(routing_key)
        
        if image_path is None:
            print(f"No {routing_key} images found")
            return False

        message = {
            'id': message_id,
            'type': routing_key,
            'image_path': image_path,
            'team' if routing_key == 'team' else 'emotion': os.path.basename(os.path.dirname(image_path)),
            'timestamp': time.time()
        }
        
        channel.basic_publish(
            exchange='image_exchange',
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"Published -> key: {routing_key} id: {message_id}")

        if routing_key == 'face':
            self.face_count += 1
            if self.face_count >= self.max_faces:
                self.face_completed = True
                print("\n[INFO] Face processing completed. Switching to team processing...\n")
            
        return True

def main():
    connection, channel = connect_to_rabbitmq()
    producer = MessageProducer()
    try:
        print("\033[94m[Producer Started]\033[0m Press Ctrl+C to stop")
        while True:
            # If face processing is complete, only use team routing key
            routing_key = 'team' if producer.face_completed else random.choice(['face', 'team'])
            if not producer.send_message(channel, routing_key):
                print("No images available in dataset")
                break
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\n\033[93m[Producer Stopped]\033[0m")
    finally:
        connection.close()

if __name__ == '__main__':
    main()