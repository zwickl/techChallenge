#!/usr/bin/env python3

import requests
import asyncio
import socket
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

def getFriendsQuote(sess, num=1):
    '''request quote from web service
       returns requests.response object '''
    serviceURL="https://friends-quotes-api.herokuapp.com/quotes"
    if num > 1:
        quote_url="%s/%d" % (serviceURL, num)
    else:
        quote_url="%s/random" % serviceURL
    try:
        resp = sess.get(quote_url)
        return resp
    except requests.ConnectionErrorr as err:
        raise SystemExit(err)

with requests.Session() as sess:
    response = getFriendsQuote(sess)

quoteJSON = (response.json())
print(quoteJSON)

try:
    natsIP=socket.gethostbyname('nats')
    print("found nats service at %s" % natsIP)
except:
    natsIP="127.0.0.1:4222"

await nc.connect(natsIP, loop=loop)

subject="quotes"

await nc.publish(subject, quoteJSON)


