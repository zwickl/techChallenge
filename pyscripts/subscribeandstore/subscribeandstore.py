#!/usr/bin/env python3.8

import asyncio
import aiosqlite
import socket
import json
import sqlite3
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

async def run(natsIP, loop):

    async def store_quote_async(character, quote_str):
        '''parse the quote json and store it in an sqlite database'''
        print("trying to store: %s" % quote_str)
        
        dbase_file = "/db/quotes.db"
        #dbase_file = "quotes.db"
        #conn = sqlite3.connect(dbase_file)
        try:
            conn = await aiosqlite.connect(dbase_file)
        except aiosqlite.OperationalError as err:
            print(err)
            return
        cursor = await conn.cursor()

        table_name = "friends_quotes"

        try:
            cursor.execute('CREATE TABLE if not exists %s (character TEXT, quote TEXT)' % table_name)
            command = 'INSERT OR IGNORE INTO %s VALUES ( "%s", "%s")' % (table_name, quote_str, character )
            cursor.execute(command)

        except Exception as err:
            print('execute error on database')
            print(err)
        finally:
            await conn.commit()
            await conn.close()

    def store_quote(character, quote_str):
        '''parse the quote json and store it in an sqlite database'''
        print("trying to store: %s" % quote_str)
        
        dbase_file = "quotes.db"
        try:
            conn = sqlite3.connect(dbase_file)
        except sqlite3.OperationalError as err:
            print(err)
            return
        cursor = conn.cursor()

        table_name = "friends_quotes"

        try:
            cursor.execute('CREATE TABLE if not exists %s (character TEXT, quote TEXT)' % table_name)
            command = 'INSERT OR IGNORE INTO %s VALUES ( "%s", "%s")' % (table_name, quote_str, character )
            cursor.execute(command)
        except Exception as err:
            print('execute error on database')
            print(err)
        finally:
            conn.commit()
            conn.close()

    async def message_handler(msg):
        '''this is called every time a message is received under the given subscription
           the function that actually stores the quote in the db is called from here, so
           this function doesn't even return anything'''
        print("entering message_handler")
        subject = msg.subject
        data = msg.data.decode()
        print("Received a message on '{subject} : {data}".format(
            subject=subject, data=data))

        try:
            data = json.loads(data)
        except JSONDecodeError as err:
            print("problem interpreting json")

        character = data["character"]
        quote_str = data["quote"]
        
        lock = asyncio.Lock()
        async with lock:
            store_quote(character, quote_str)
        #async with lock:
        #    store_quote_async(character, quote_str)

    nc = NATS()
    print("cconnectting to nats")
    await nc.connect(natsIP, loop=loop)

    #after the subscription happens, this should just keep calling the message_handler every time a message comes in
    subject="quotes"
    sid = await nc.subscribe(subject, cb=message_handler)

    #hang out dealing with messages forever
    while True:
        #if we don't await somewhere, control never seems to go back to the message handler
        await asyncio.sleep(1)

if __name__ == '__main__':
    #making the socket call to look up the service IP within the async loop
    #caused problems, and I couldn't get the aiodns version to work
    #right, so pass IP as arg to run()
    natsIP = get_nats_ip()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    loop.run_until_complete(run(natsIP, loop))
    loop.close()

