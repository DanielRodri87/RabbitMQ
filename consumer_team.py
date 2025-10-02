import pika
import json
import time
from datetime import datetime
import os
import cv2

def connect_to_rabbitmq():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='image_exchange', exchange_type='topic')
    result = channel.queue_declare(queue='', exclusive=True, durable=True)
    queue_name = result.method.queue
    
    # Bind to 'team' routing key
    channel.queue_bind(exchange='image_exchange', queue=queue_name, routing_key='team')
    return connection, channel, queue_name

class TeamDetector:
    def __init__(self):
        # Create results and teams directory
        if not os.path.exists('/results'):
            os.makedirs('/results')
        os.makedirs('/results/teams', exist_ok=True)

    def predict(self, message):
        # Read image
        img = cv2.imread(message['image_path'])
        if img is None:
            print(f"Error loading image: {message['image_path']}")
            return None
        
        # Draw team name on image
        team = message['team']
        
        # Parameters for 512x512 images
        font_scale = 2.0
        thickness = 3
        font = cv2.FONT_HERSHEY_DUPLEX
        
        # Get text size
        (text_width, text_height), _ = cv2.getTextSize(team, font, font_scale, thickness)
        
        # Position text at bottom
        text_x = (img.shape[1] - text_width) // 2
        text_y = img.shape[0] - 20
        
        # Draw background rectangle
        padding = 10
        cv2.rectangle(img, 
                     (text_x - padding, text_y - text_height - padding),
                     (text_x + text_width + padding, text_y + padding),
                     (0, 0, 0),
                     cv2.FILLED)
        
        # Draw text
        cv2.putText(img, team,
                   (text_x, text_y),
                   font,
                   font_scale,
                   (255, 255, 255),
                   thickness)
        
        # Save processed image
        result_path = f"/results/teams/{message['id']}.png"
        cv2.imwrite(result_path, img)
        
        return team

def process_team(message):
    detector = TeamDetector()
    result = detector.predict(message)
    
    # Save result
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_path = f"/results/teams/{timestamp}_{message['id']}.json"
    
    with open(result_path, 'w') as f:
        json.dump({
            'id': message['id'],
            'team': result,
            'timestamp': timestamp
        }, f)
    
    return result

def callback(ch, method, properties, body):
    message = json.loads(body)
    result = process_team(message)
    print(f"[Team] id={message['id']} -> predicted team: {result}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection, channel, queue_name = connect_to_rabbitmq()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    print('\033[94m[Team Consumer Started]\033[0m Press Ctrl+C to stop')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n\033[93m[Consumer Stopped]\033[0m")
    finally:
        connection.close()

if __name__ == '__main__':
    main()
