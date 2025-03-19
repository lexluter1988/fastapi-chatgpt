# FastAPI server with Kafka and fastapi-users

This is FastAPI application with LLM worker daemon running separately.

Services are communicating via Kafka messaging bus.

Chat is implemented by chainlit

## Author

Author: Alexey Suponin <lexxsmith@gmail.com>

## Version

0.1.0

## License

License: MIT

## Quick start

```
python3.10 -m venv venv
source venv/bin/activate
pip install pip-tools
make deps

mv .env.example .env
```

Now write your base url, token, model into `.env`

#### Run full stack

Run `docker-compose up -d --build`


#### Local development

If you want to run FastAPI locally, comment the `main` service in `docker-compose.yml`

Run `docker-compose up -d --build`
Start dev server `uvicorn --host 0.0.0.0 --port 8000 --reload app.main:application`

## Kafka

UI is accessible on http://127.0.0.1:8080/


## SwaggerUI

Visit the http://127.0.0.1:8000/api/docs


## Chainlit AI Chat

Visit the http://127.0.0.1:8000/api/chat/
