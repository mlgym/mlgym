import json
from kafka import KafkaProducer

def publish_message(kafka_producer, topic_name, key, value):
    try:
        key_bytes = bytes(key, encoding='utf-8')
        value_bytes = bytes(value, encoding='utf-8')
        kafka_producer.send(topic_name, key=key_bytes, value=value_bytes)
        kafka_producer.flush()
        print('Message published successfully.')
    except Exception as ex:
        print(str(ex))


if __name__ == '__main__':
    kafka_producer = KafkaProducer(bootstrap_servers=['localhost:9092'], api_version=(0, 10))
    employees = [
        {
            "name": "John Smith",
            "id": 1
        }, {
            "name": "Susan Doe",
            "id": 2
        }, {
            "name": "Karen Rock",
            "id": 3
        },
    ]
    for employee in employees:
        publish_message(
            kafka_producer=kafka_producer,
            topic_name='employees',
            key=employee['id'],
            value=json.dumps(employee)
        )
    if kafka_producer is not None:
        kafka_producer.close()