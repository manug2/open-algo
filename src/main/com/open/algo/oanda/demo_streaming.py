"""
Demonstrates streaming feature in OANDA open api

To execute, run the following command:

python streaming.py [options]

To show heartbeat, replace [options] by -b or --displayHeartBeat

install 'requests' package using 'pip install requests'

"""

import requests
import json
import datetime

from optparse import OptionParser

def connect_to_stream():
    """

    Environment           <Domain>
    fxTrade               https://stream-fxtrade.oanda.com
    fxTrade Practice      https://stream-fxpractice.oanda.com
    sandbox               http://stream-sandbox.oanda.com
    """

    # Replace the following variables with your personal ones
    domain = 'http://stream-sandbox.oanda.com'
    access_token = 'ACCESS-TOKEN'
    account_id = '1234567'
    instruments = "EUR_USD,USD_CAD"

    try:
        s = requests.Session()
        url = domain + "/v1/prices"
        headers = {'Authorization' : 'Bearer ' + access_token,
                   # 'X-Accept-Datetime-Format' : 'unix'
                  }
        params = {'instruments' : instruments, 'accountId' : account_id}
        req = requests.Request('GET', url, headers = headers, params = params)
        pre = req.prepare()
        resp = s.send(pre, stream = True, verify = False)
        return resp
    except Exception as e:
        s.close()
        print ("Caught exception when connecting to stream\n" + str(e) )

def demo(displayHeartbeat):
    my_tick = datetime.datetime.now().isoformat()
    print ('creating streaming connection', my_tick)

    response = connect_to_stream()

    my_tick_end = datetime.datetime.now().isoformat()
    print ('received response', my_tick_end)

    if response.status_code != 200:
        print (response.text)
        return
    for line in response.iter_lines(1):
        my_tick_end = datetime.datetime.now().isoformat()
        if line:
            try:
                msg = json.loads(line.decode("utf-8"))
            except Exception as e:
                print ("Caught exception when converting message into json\n" + str(e))
                return
            
            if displayHeartbeat:
                print (my_tick_end, line)
            else:
                if "instrument" in msg or "tick" in msg:
                    print (my_tick_end, line)

def main():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-b", "--displayHeartBeat", dest = "verbose", action = "store_true", 
                        help = "Display HeartBeat in streaming data")
    displayHeartbeat = False

    (options, args) = parser.parse_args()
    if len(args) > 1:
        parser.error("incorrect number of arguments")
    if options.verbose:
        displayHeartbeat = True
    demo(displayHeartbeat)


if __name__ == "__main__":
    main()


