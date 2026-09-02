FROM python:3.12-slim

WORKDIR /app

COPY historianos-toolkit/ /app/
COPY historianos-toolkit/example-vaults/zjazd-gnieznienski/ /showcase/zjazd-gnieznienski/

RUN mkdir -p /vault

ENV PYTHONUNBUFFERED=1
ENV HISTORIANOS_VAULT=/vault
ENV HISTORIANOS_SHOWCASE=/showcase/zjazd-gnieznienski
ENV HISTORIANOS_DEFAULT_VAULT=gniezno
ENV HISTORIANOS_DEFAULT_NAME="Zjazd Gnieźnieński 1000"
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=5 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/api/health', timeout=2).read()"

CMD ["python","api_server.py"]
