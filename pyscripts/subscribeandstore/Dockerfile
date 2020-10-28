FROM python:3

ADD subscribeandstore.py /

RUN pip install aiosqlite asyncio-nats-client  aiodns

CMD [ "python", "./subscribeandstore.py" ]

