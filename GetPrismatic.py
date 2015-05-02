#Source: http://neo4j.com/blog/neo4j-building-topic-graph-prismatic-interest-graph-api/
#Reference: https://github.com/Prismatic/interest-graph#topic-tagging

import time
import requests
import json
import os
 
def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.clock() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.clock()
            return ret
        return rateLimitedFunction
    return decorate
 
@RateLimited(0.3)
def topics(body):
    payload = { 
                'body': body,
                'api-token': os.environ['prismatickey']} 
    return (requests.post("http://interest-graph.getprismatic.com/text/topic", data=payload))