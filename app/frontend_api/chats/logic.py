import asyncio
import uuid
from typing import AsyncGenerator

from app.logger import logger
from app.utils.dto import ChatCompletionRequest, ChatCompletionResponse
from app.settings import get_settings
from app.state import response_futures
from app.utils.producers import KafkaTransportProducer


settings = get_settings()


async def chat_completions(
    request: ChatCompletionRequest
) -> AsyncGenerator[ChatCompletionResponse, None]:
    producer = KafkaTransportProducer(topic='chat_requests_generic')
    logger.info('LLM request Kafka Generic Producer Connected')
    await producer.connect()

    correlation_id = str(uuid.uuid4())
    headers = {
        'correlation_id': correlation_id,
        'event_type': 'chat.completions.request',
    }

    loop = asyncio.get_event_loop()
    future = loop.create_future()
    response_futures[correlation_id] = future

    await producer.send(event=request, headers=headers)

    return chat_completions_stream_generator(correlation_id)


async def chat_completions_stream_generator(
    correlation_id: str
) -> AsyncGenerator[ChatCompletionResponse, None]:
    """
    Асинхронный генератор для передачи частичных ответов
    от chat.completions в FastAPI StreamingResponse
    """
    while True:
        if correlation_id not in response_futures:
            response_futures[correlation_id] = asyncio.Future()

        future = response_futures[correlation_id]

        try:
            chunk = await asyncio.wait_for(future, timeout=5)
            if chunk is None:
                break
            yield chunk

            response_futures[correlation_id] = asyncio.Future()
        except asyncio.TimeoutError:
            break
        except asyncio.CancelledError:
            logger.error(f'Streaming cancelled for {correlation_id}')
