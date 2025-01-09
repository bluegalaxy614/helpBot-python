FROM python:3.12-slim AS poetry
RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=poetry /app/requirements.txt .
RUN pip install -r requirements.txt
# EXPOSE 8080

# copy docker-entrypoint.sh
# COPY ./docker-entrypoint.sh /docker-entrypoint.sh
# RUN chmod a+x /docker-entrypoint.sh

# copy project
COPY . .

# run docker-entrypoint.sh
# ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

