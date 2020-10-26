FROM python:3

ADD requestquoteandpublish.py /

RUN pip install requests asyncio asyncio-nats-client 

CMD [ "python", "./requestquoteandpublish.py" ]

