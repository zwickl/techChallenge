#!/usr/bin/env python3


try:
    natsIP=socket.gethostbyname('nats')
    print("found nats service at %s" % natsIP)
except:
    print("nats service not found, trying localhost:4222"))
    natsIP="127.0.0.1:4222"

await nc.connect(natsIP, loop=loop)



