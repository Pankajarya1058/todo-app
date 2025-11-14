
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local:$PATH
EXPOSE 5000
CMD ["python","app.py"]
