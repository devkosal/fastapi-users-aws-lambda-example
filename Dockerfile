FROM python:3.8
COPY requirements.txt .
RUN pip install -r requirements.txt -t python
RUN apt-get update && apt-get install zip
RUN zip -r fastapi-mysql.zip python
RUN rm -rf python
