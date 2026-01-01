FROM python:3.11-slim

# set workdir
WORKDIR /app

# system deps for PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends             gcc build-essential libmupdf-dev libx11-6 libfreetype6-dev libjpeg-dev zlib1g-dev             && rm -rf /var/lib/apt/lists/*

# copy
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src
WORKDIR /app/src

EXPOSE 8080
ENV PYTHONPATH=/app/src

CMD ["uvicorn", "docustruct.api:app", "--host", "0.0.0.0", "--port", "8080"]
