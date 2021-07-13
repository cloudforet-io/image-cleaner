FROM python:3.8

WORKDIR /usr/src/

COPY requirements.txt ./

COPY ./src/image_cleaner.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./image_cleaner.py" ]