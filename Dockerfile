FROM python:3.10

WORKDIR /app

RUN pip install --no-cache poetry

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD alembic upgrade head && fastapi run --host 0.0.0.0