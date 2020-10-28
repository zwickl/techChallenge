#!/usr/bin/env python3

#import requests
import asyncio
import aiohttp
import socket
import time
import json
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

def get_nats_ip():
    try:
        natsIP=socket.gethostbyname('nats')
        print("found nats service at %s" % natsIP)
    except socket.gaierror as err:
        print(err)
        natsIP="127.0.0.1:4222"
        print("could not find nats service, using address %s" % natsIP)
    return natsIP

def handle_exception(loop, context):
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    print("Caught exception: %s" % msg)
    #logging.error(f"Caught exception: {msg}")
    #logging.info("Shutting down...")
    asyncio.create_task(shutdown(loop))


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

async def run(natsIP, loop):
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

    async def publishToNats(nc, subject, content):
        await nc.publish(subject, content)

    nc = NATS()
    try:
        print("connecting to nats")
        await nc.connect(natsIP, loop=loop)
    except ConnectionRefusedError as err:
        print("could not connect to nats")

    while True :
        time.sleep(5)
        response = await getFriendsQuote()
        print(response)
        await publishToNats(nc, "quotes", response.encode())
        await asyncio.sleep(5)

if __name__ == '__main__':
    #making the socket call to look up the service IP within the async loop
    #caused problems, and I couldn't get the aiodns version to work
    #right, so pass IP as arg to run()
    natsIP = get_nats_ip()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    loop.run_until_complete(run(natsIP, loop))
    loop.close()

