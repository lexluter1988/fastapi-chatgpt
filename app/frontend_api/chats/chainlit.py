import chainlit as cl
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer

from app.utils.dto import ChatCompletionRequest
from app.settings import get_settings
from app.frontend_api.chats.logic import chat_completions

settings = get_settings()


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.on_chat_resume
async def on_chat_resume(thread):
    pass


@cl.data_layer
def get_data_layer():
    return SQLAlchemyDataLayer(
        conninfo=settings.database_url,
    )


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")

    request = ChatCompletionRequest(
        model=settings.openai_model_name,
        messages=message_history,
        stream=True,
    )
    stream = await chat_completions(
        request=request
    )

    async for part in stream:
        if part and hasattr(part, 'choices') and len(part.choices) > 0:
            response_text = None
            if part.choices[0].delta.content:
                response_text = part.choices[0].delta.content
            elif part.choices[0].message:
                response_text = part.choices[0].message.content
            if response_text:
                await msg.stream_token(response_text)

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()
