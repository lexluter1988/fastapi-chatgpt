from app.logger import logger
from app.utils.consumers import KafkaTransportConsumer


async def consume_responses_websockets(active_connections: dict):
    consumer = KafkaTransportConsumer(
        topic='chat_responses_generic',
    )
    await consumer.connect()
    logger.info('LLM response Kafka Consumer Connected')

    try:
        async for msg, headers in consumer.consume():
            correlation_id = headers.get('correlation_id')
            if correlation_id in active_connections:
                websocket = active_connections[correlation_id]
                if msg and hasattr(msg, 'choices') and len(msg.choices) > 0:
                    response_text = None
                    if msg.choices[0].delta:
                        response_text = msg.choices[0].delta.content
                    elif msg.choices[0].message:
                        response_text = msg.choices[0].message.content
                    if response_text:
                        await websocket.send_text(response_text)
            else:
                logger.info(f'Received invalid message: {msg}')
    except Exception as e:
        logger.error(f'Error in chat consumer: {e}')
    finally:
        await consumer.close()
