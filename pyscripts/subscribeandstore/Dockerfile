FROM python:3

ADD subscribeandstore.py /

RUN pip install asyncio asyncio-nats-client 

CMD [ "python", "./subscribeandstore.py" ]

