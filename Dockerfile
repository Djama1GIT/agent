FROM python:3.13

RUN mkdir -p /app/src/

WORKDIR /app/src

COPY src ./

COPY logger.ini /app/

COPY requirements.txt .

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8000

WORKDIR /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]