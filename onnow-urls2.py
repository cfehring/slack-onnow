##import json
import requests #Digital recommends the request lib to interact w/ apis over http. http://docs.python-requests.org/
##from dateutil.parser import * # for parse() method to convert datetime format
##import pytz # to convert to pacific time
import sys # for sys.argv to pass arguments from command line

# initialize static variables for urls
epg_url = 'http://api.pac-12.com/v3/epg' #production server
event_url = 'http://api.pac-12.com/v3/events'  #production server
onnow_url = 'http://api.pac-12.com/v3/onnow'

#Get arguments from python command line and iterate through the networks
args = sys.argv
if len(args) is 1:
    args.extend(["n", "a", "b", "l", "m", "o", "w"])
    ##print args
for i in range(len(args)):
    if i == 0:
        None # Don't need to do anything with the name of the script, just the arguments

    else:
        net = "%s" % (args[i])

        if net == 'n':
            networks = 88 #Pac-12 Networks
            net_name = "NAT"
        elif net == 'b':
            networks = 86 #Pac-12 Bay Area
            net_name = "BAY"
        elif net == 'a':
            networks = 91 #Pac-12 Arizona
            net_name = "ARZ"
        elif net == 'l':
            networks = 92 #Pac-12 Los Angeles
            net_name = "LAX"
        elif net == 'm':
            networks = 87 #Pac-12 Mountain
            net_name = "MTN"
        elif net == 'o':
            networks = 89 #Pac-12 Oregon
            net_name = "ORG"
        elif net == 'w':
            networks = 90 #Pac-12 Washington
            net_name = "WAS"

        elif net == 'help':
            print "enter the first letter of each network after the script name as shown in the following examples"
            print "python onnow-urls.py n a b l m o w"
            print "python onnow-urls.py n"
            print "python onnow-urls.py b l"
            sys.exit()

        ##print file # indicate which file the date will be written to

        # limit results to just the next event
        pagesize = 1

        # request to p12 api for onnow data
        onnow_get_params = {'pagesize': pagesize , 'networks': networks}
        onnow_get_request  = requests.get(onnow_url, params=onnow_get_params)
        onnow_get_response = onnow_get_request.json()

        # request to p12 api for EPG data
        ##epg_get_params = {'pagesize': pagesize , 'networks': networks}
        ##epg_get_request  = requests.get(epg_url, params=epg_get_params)
        ##epg_get_response = epg_get_request.json()

        # Pull out the override_url from the onnow api
        override_url = onnow_get_response['programs'][0]['override_url']
        if override_url is None:
            return_url = onnow_get_response['programs'][0]['url']
        else:
            return_url = override_url
        print "{}: {}".format(net_name,return_url)
        ##print args
