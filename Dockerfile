FROM python:3.12-slim

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP=microblog.py

EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]
