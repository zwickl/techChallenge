FROM python:3

ADD requestquoteandpublish.py /

RUN pip install aiohttp asyncio-nats-client 

CMD [ "python", "./requestquoteandpublish.py" ]

