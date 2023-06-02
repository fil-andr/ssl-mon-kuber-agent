FROM python:3-alpine

COPY app /app
RUN apk update \
    && apk add openssl

RUN pip install -r /app/requirements.txt

ENTRYPOINT ["python"]

CMD ["/app/script.py"]
