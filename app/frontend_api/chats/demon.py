from app.state import response_futures
from app.utils.consumers import KafkaTransportConsumer


async def consume_responses_futures():
    consumer = KafkaTransportConsumer(
        topic='chat_responses_generic',
    )
    await consumer.connect()
    try:
        async for msg, headers in consumer.consume():
            correlation_id = headers.get('correlation_id')

            if correlation_id in response_futures:
                future = response_futures.pop(correlation_id)
                future.set_result(msg)
    finally:
        await consumer.close()
