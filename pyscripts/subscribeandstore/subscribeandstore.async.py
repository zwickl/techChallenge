#!/usr/bin/env python3.8

import asyncio
import aiosqlite
import aiodns
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers


def handle_exception(loop, context):
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    print("Caught exception: %s" % msg)
    #logging.error(f"Caught exception: {msg}")
    #logging.info("Shutting down...")
    asyncio.create_task(shutdown(loop))

#some  of this adapted from
#asyncio python-nats-io/basicUsage.py

async def run(loop):

    async def store_quote(character, quote_str):
        '''parse the quote json and store it in an sqlite database'''
        print("trying to store: %s" % quote_str)
        
        dbase_file = "/db/quotes.db"
        #conn = sqlite3.connect(dbase_file)
        conn = await aiosqlite.connect(dbase_file)
        cursor = await conn.cursor()

        table_name = "friends_quotes"

        try:
            cursor.execute('CREATE TABLE if not exists %s (character TEXT, quote TEXT)' % table_name)
        except Exception as err:
            print('execute error on database')
            loop.shutdown_asyncgens()

        print('INSERT OR IGNORE INTO %s VALUES ( "%s", "%s")' % (table_name, quote_str, character ))

        cursor.execute('INSERT OR IGNORE INTO %s VALUES ( "%s", "%s")' % (table_name, quote_str, character ))

        await conn.commit()
        await conn.close()

    async def message_handler(msg):
        '''this is called every time a message is received under the given subscription
           the function that actually stores the quote in the db is called from here, so
           this function doesn't even return anything'''
        print("entering message_handler")
        subject = msg.subject
        data = msg.data.decode()
        print("Received a message on '{subject} : {data}".format(
            subject=subject, data=data))
     
        character = data["character"]
        quote_str = data["quote"]
        await store_quote(character, quote_str)

    try:
        #natsIP= await socket.gethostbyname('nats')
        natsIP = await aiodns.gethostbyname('nats')
        print("found nats service at %s" % natsIP)
    except:
        print("nats service not found, trying localhost:4222")
        natsIP="127.0.0.1:4222"

    nc = NATS()
    print("about to connect to nats")
    await nc.connect(natsIP, loop=loop)


    #after the subscription happens, this should just keep calling the message_handler every time a message comes in
    subject="quotes"
    print("about to subscribe")
    sid = await nc.subscribe(subject, cb=message_handler)
    print("done with subscribe")

    #hang out dealing with messages forever
    while True:
        pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    loop.run_until_complete(run(loop))
    loop.close()

