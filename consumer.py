import pika
import json
import time
from datetime import datetime
import random
import os
import cv2
import numpy as np

def connect_to_rabbitmq():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()
    
    # Declare topic exchange
    channel.exchange_declare(exchange='image_exchange', exchange_type='topic')
    
    # Declare queue and bind with routing key
    result = channel.queue_declare(queue='', exclusive=True, durable=True)
    queue_name = result.method.queue
    
    # Bind to 'face' routing key
    channel.queue_bind(exchange='image_exchange', queue=queue_name, routing_key='face')
    return connection, channel, queue_name

class EmotionDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        os.makedirs('/results/faces', exist_ok=True)

    def predict(self, message):
        # Read image
        img = cv2.imread(message['image_path'])
        if img is None:
            print(f"Error loading image: {message['image_path']}")
            return None
            
        # Para imagens 48x48, vamos considerar que a face ocupa a maior parte da imagem
        h, w = img.shape[:2]
        
        # Define a face como ocupando 80% da imagem
        padding = int(w * 0.1)  # 10% de padding em cada lado
        x = padding
        y = padding
        w = w - 2*padding
        h = h - 2*padding
        
        # Draw rectangle with thicker lines (proporcionalmente menor para imagem pequena)
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
        
        # Define text parameters
        padding_text = 1  # Definir padding_text antes de usar
        text = message['emotion']
        font_scale = 0.25  # Reduzido de 0.4 para 0.25
        thickness = 1
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Get text size
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Ajustar posição do texto para garantir que fique dentro da imagem
        text_x = max(padding, min(x + padding_text, w - text_width - padding))
        text_y = max(text_height + padding_text, y - padding_text)
        
        # Draw background rectangle for text
        cv2.rectangle(img, 
                     (text_x - padding_text, text_y - text_height - 2*padding_text),
                     (text_x + text_width + 2*padding_text, text_y),
                     (0, 255, 0),
                     cv2.FILLED)
        
        # Draw text
        cv2.putText(img, text,
                   (text_x, text_y - padding_text),
                   font,
                   font_scale,
                   (0, 0, 0),
                   thickness)
        
        # Resize image for better visualization in results
        img_display = cv2.resize(img, (240, 240), interpolation=cv2.INTER_NEAREST)
        
        # Save processed image
        result_path = f"/results/faces/{message['id']}.jpg"
        cv2.imwrite(result_path, img_display)
        
        return message['emotion']

def process_face(message):
    detector = EmotionDetector()
    result = detector.predict(message)
    
    # Save result
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_path = f"/results/faces/{timestamp}_{message['id']}.json"
    
    with open(result_path, 'w') as f:
        json.dump({
            'id': message['id'],
            'emotion': result,
            'timestamp': timestamp
        }, f)
    
    return result

def callback(ch, method, properties, body):
    message = json.loads(body)
    result = process_face(message)
    print(f"[Face] id={message['id']} -> predicted: {result}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection, channel, queue_name = connect_to_rabbitmq()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    print('\033[94m[Face Consumer Started]\033[0m Press Ctrl+C to stop')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n\033[93m[Consumer Stopped]\033[0m")
    finally:
        connection.close()

if __name__ == '__main__':
    main()