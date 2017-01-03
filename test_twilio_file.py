#!/usr/bin/python2

from datetime import datetime
from datetime import time
from time import sleep
import json
import subprocess
# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import TwilioRestClient

# -----------------------------------------------------------------------------
# USER INPUTS
#ACCOUNT_SID = "ACd9a1df064a9e4d939881b1c86adf28ec" # Your Account SID from www.twilio.com/console
ACCOUNT_SID = "ACb9b0739d1604f2c224b0fbd6f961666c" # Your Account SID from www.twilio.com/console
#AUTH_TOKEN  = "f083322a99bd62b673649c97a2bc6381"  # Your Auth Token from www.twilio.com/console
AUTH_TOKEN  = "471323d583ba5a2afdcb0814e50ec9f7"  # Your Auth Token from www.twilio.com/console
TO_NUMBER = "+12069484838"
#FROM_NUMBER = "+14259708696"
FROM_NUMBER = "+12064721749"  #michael.jay.stebbins@gmail.com account

# -----------------------------------------------------------------------------

try:
    # Find these values at https://twilio.com/user/account
    account_sid = ACCOUNT_SID
    auth_token = AUTH_TOKEN
    client = TwilioRestClient(account_sid, auth_token)

    message_body = "testing the Twilio"
    message = client.messages.create(to=TO_NUMBER, from_=FROM_NUMBER, body=message_body)

    print('test SMS sent')
except:
    print ('error sendingr SMS')
