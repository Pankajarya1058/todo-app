
# Stage-1
FROM python:3.11 AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --user -r requirements.txt

# Stage-2
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY . .

ENV PATH=/root/.local:$PATH

EXPOSE 5000

CMD ["python","app.py"]
