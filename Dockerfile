FROM python:3-alpine
WORKDIR /usr/src/app
COPY . .
RUN apk --no-cache add build-base librdkafka-dev librdkafka git && pip install --no-cache-dir -r requirements.txt && git log -1 --pretty=format:"hash=%H%ndate=%cd%n" > git_commit && apk del git build-base librdkafka-dev && rm -rf .git
CMD [ "python", "-u", "main.py"]