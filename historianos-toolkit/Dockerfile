FROM python:3.12-slim
WORKDIR /app
COPY historianos-toolkit/ /app/
COPY historianos-toolkit/example-vaults/zjazd-gnieznienski/ /vault/
ENV PYTHONUNBUFFERED=1
ENV HISTORIANOS_VAULT=/vault
EXPOSE 8080
CMD ["python","api_server.py"]
