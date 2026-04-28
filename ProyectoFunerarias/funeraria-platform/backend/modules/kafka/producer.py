import json
from datetime import datetime
from confluent_kafka import Producer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaEventProducer:
    def __init__(self, bootstrap_servers):
        conf = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'funeraria-backend'
        }
        self.producer = Producer(conf)

    def _delivery_report(self, err, msg):
        if err is not None:
            logger.error(f'Error al enviar evento a Kafka: {err}')
        else:
            logger.info(f'Evento enviado a {msg.topic()} [{msg.partition()}]')

    def publish_event(self, topic, event_type, payload):
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": payload
        }
        try:
            self.producer.produce(
                topic,
                key=event_type.encode('utf-8'),
                value=json.dumps(event).encode('utf-8'),
                callback=self._delivery_report
            )
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Error produciendo evento en {topic}: {e}")

    def flush(self):
        self.producer.flush()

# Singleton placeholder, initialized in app.py
producer_instance = None

def get_producer() -> KafkaEventProducer:
    return producer_instance
