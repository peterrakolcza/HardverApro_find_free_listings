FROM python:3.7-alpine
WORKDIR /web
RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "flask", "run", "--host=0.0.0.0"]
