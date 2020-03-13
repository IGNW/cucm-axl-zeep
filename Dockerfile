FROM python:3.8-slim-buster

WORKDIR /usr/src/app

RUN apt-get update && apt-get upgrade
RUN apt-get install -y python3-lxml

# RUN apk add --update --no-cache gcc libc-dev libxslt-dev
# RUN apk add --no-cache libxslt

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run"]