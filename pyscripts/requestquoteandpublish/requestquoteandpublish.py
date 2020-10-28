#!/usr/bin/env python3

#import requests
import asyncio
import aiohttp
import socket
import time
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

#some  of this adapted from
#asyncio python-nats-io/basicUsage.py


'''
async def fetch_page(session, url):
    with aiohttp.Timeout(10):
        async with session.get(url) as response:
            assert response.status == 200
            return await response.read()

loop = asyncio.get_event_loop()
with aiohttp.ClientSession(loop=loop) as session:
    content = loop.run_until_complete(
        fetch_page(session, 'http://python.org'))
    print(content)
loop.close()
'''

async def run(loop):
    async def getFriendsQuote(num=1):
        '''request quote from web service
           returns requests.response object '''
        service_url="https://friends-quotes-api.herokuapp.com/quotes"
        if num > 1:
            quote_url="%s/%d" % (service_url, num)
        else:
            quote_url="%s/random" % service_url
        #try:
        async with aiohttp.ClientSession(loop=loop) as sess:
            async with sess.get(quote_url) as resp:
                assert resp.status == 200
                text = await resp.text()
                print("got response %s" % text)
                return text
        #except Exception as err:
        #    raise SystemExit(err)

    async def publishToNats(subject, content):
        try:
            natsIP=socket.gethostbyname('nats')
            print("found nats service at %s" % natsIP)
        except:
            natsIP="127.0.0.1:4222"

        nc = NATS()
        await nc.connect(natsIP)

        subject="quotes"
        await nc.publish(subject, content)
        
        # Terminate connection to NATS.
        await nc.close()

    while True :
        response = await getFriendsQuote()
        await asyncio.sleep(5)
        print(response)
        await publishToNats("quotes", response.encode('utf-8'))
        await asyncio.sleep(5)


if __name__ == '__main__':
    num_quotes = 10
    loop = asyncio.get_event_loop()
    for q in range(num_quotes):
        print("loop  %d" % q)
        try:
            loop.run_until_complete(run(loop))
        except Exception as err:
            raise SystemExit(err)

