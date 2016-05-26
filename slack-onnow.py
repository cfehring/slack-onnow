'''
This function handles a Slack slash command and echoes the details back to the user.

Follow these steps to configure the slash command in Slack:

  1. Navigate to https://<your-team-domain>.slack.com/services/new

  2. Search for and select "Slash Commands".

  3. Enter a name for your command and click "Add Slash Command Integration".

  4. Copy the token string from the integration settings and use it in the next section.

  5. After you complete this blueprint, enter the provided API endpoint URL in the URL field.


Follow these steps to encrypt your Slack token for use in this function:

  1. Create a KMS key - http://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html.

  2. Encrypt the token using the AWS CLI.
     $ aws kms encrypt --key-id alias/<KMS key name> --plaintext "<COMMAND_TOKEN>"

  3. Copy the base-64 encoded, encrypted key (CiphertextBlob) to the kmsEncyptedToken variable.

  4. Give your function's role permission for the kms:Decrypt action.
     Example:
       {
         "Version": "2012-10-17",
         "Statement": [
           {
             "Effect": "Allow",
             "Action": [
               "kms:Decrypt"
             ],
             "Resource": [
               "<your KMS key ARN>"
             ]
           }
         ]
       }

Follow these steps to complete the configuration of your command API endpoint

  1. When completing the blueprint configuration select "POST" for method and
     "Open" for security on the Endpoint Configuration page.

  2. After completing the function creation, open the newly created API in the
     API Gateway console.

  3. Add a mapping template for the application/x-www-form-urlencoded content type with the
     following body: { "body": $input.json("$") }

  4. Deploy the API to the prod stage.

  5. Update the URL for your Slack slash command with the invocation URL for the
     created API resource in the prod stage.
'''

import boto3
from base64 import b64decode
from urlparse import parse_qs
import logging
import requests #Digital recommends the request lib to interact w/ apis over http. http://docs.python-requests.org/
import sys # for sys.argv to pass arguments from command line
#import slackweb
# import json
# from urllib2 import Request, urlopen, URLError, HTTPError
# from urllib import urlencode
#import slacker


ENCRYPTED_EXPECTED_TOKEN = "CiDwhvH0HpF1WdM/Qj2SO8kDmtA9FMF7ZIZN8ambj2J3gRKfAQEBAgB48Ibx9B6RdVnTP0I9kjvJA5rQPRTBe2SGTfGpm49id4EAAAB2MHQGCSqGSIb3DQEHBqBnMGUCAQAwYAYJKoZIhvcNAQcBMB4GCWCGSAFlAwQBLjARBAyjjtXp0tXAwOk3J9wCARCAMxstVfCsQUyB8g0ZnEuRs1rb6Fbor5JusgRbHuKJc6HsWDWr2vQGnBU05JowdV1mP0L5yQ==" # Enter the base-64 encoded, encrypted Slack command token (CiphertextBlob)

kms = boto3.client('kms')
expected_token = kms.decrypt(CiphertextBlob = b64decode(ENCRYPTED_EXPECTED_TOKEN))['Plaintext']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    req_body = event['body']
    params = parse_qs(req_body)
    token = params['token'][0]
    if token != expected_token:
        logger.error("Request token (%s) does not match exptected", token)
        raise Exception("Invalid request token")

    user = params['user_name'][0]
    command = params['command'][0]
    channel = params['channel_name'][0]
    command_text = params['text'][0]
#    myurl = onnowUrls()
#    return(myurl)
#    return "%s invoked %s in %s" % (user, command, channel)



    # initialize static variables for urls
    epg_url = 'http://api.pac-12.com/v3/epg' #production server
    event_url = 'http://api.pac-12.com/v3/events'  #production server
    onnow_url = 'http://api.pac-12.com/v3/onnow'

    #Get arguments from python command line and iterate through the networks
    args = command_text.split(' ')
    if len(args) is 0:
        args.extend(["n", "a", "b", "l", "m", "o", "w"])
#        args.extend(["n"])
        ##print args

    ret = {}
    ret["text"] = "Currently airing on Pac-12.com:"
    ret["attachments"] = []

    for i in range(len(args)):
#        if i == 0:
#            None # Don't need to do anything with the name of the script, just the arguments

#        else:
        net = "{}".format(args[i])

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

    #            elif net == 'help':
    #                print "enter the first letter of each network after the script name as shown in the following examples"
    #                print "python onnow-urls.py n a b l m o w"
    #                print "python onnow-urls.py n"
    #                print "python onnow-urls.py b l"
    #                sys.exit()

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
    #    eol = \n

        link = "{}: <{}>".format(net_name,return_url)

    ##############

        # ret = {}
        # ret["text"] = "Currently airing on Pac-12.com:"
        # ret["attachments"] = []
        # ret["attachments"].append({"fallback": "Hmm something didnt work right"})
        # ret["attachments"].append({"color": "#36a64f"})
        ret["attachments"].append({"text": link})

    return ret
