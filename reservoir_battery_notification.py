"""
Script tries to obtain current reservoir level and battery voltage.
If either is below a set threshold (based on date and time), an SMS is sent.
A sent notification file is created so that SMS's are only sent every so often if the warning is being ignored.
"""

from datetime import datetime
from datetime import time
from time import sleep
import json
import subprocess
import os.path
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
FROM_NUMBER = "+12064721749" # michael.jay.stebbins@gmail.com account

DELAY_SECONDS = 60
ATTEMPTS = 12
VOLTAGE_THRESHOLD = 1.36
SCHOOLNIGHT_TIME_THRESHOLD = time(20,0)  #(hour(24), minute)
RESERVOIR_WARN = 50
RESERVOIR_URGENT = 30
NOTIFICATION_ELASPED_TIME_HOURS = 4

# -----------------------------------------------------------------------------
# CONSTANTS FOR TESTING
textfileTESTING = False
RESERVOIR_TEST_VALUE = 15
timedateTESTING = False
TIME_TEST_VALUE = time(23,19)
WEEKDAY_TEST_VALUE = 0


def send_reservoir_sms(reservoir_level):
    try:
        # Find these values at https://twilio.com/user/account
        account_sid = ACCOUNT_SID
        auth_token = AUTH_TOKEN
        client = TwilioRestClient(account_sid, auth_token)

        message_body = "reservoir = "+str(reservoir_level)+" units"
        message = client.messages.create(to=TO_NUMBER, from_=FROM_NUMBER, body=message_body)

        print('reservoir SMS sent')
    except:
        print ('error sending reservoir SMS')


def send_battery_sms(voltage):
    try:
        # Find these values at https://twilio.com/user/account
        account_sid = ACCOUNT_SID
        auth_token = AUTH_TOKEN
        client = TwilioRestClient(account_sid, auth_token)

        message_body = "battery voltage = "+str(voltage)+" volts"
        message = client.messages.create(to=TO_NUMBER, from_=FROM_NUMBER, body=message_body)

        print('battery SMS sent')
    except:
        print ('error sending battery SMS')


def update_reservoir_sent_file():
    try:
        output = subprocess.Popen(["touch","sent-reservoir-sms"], stdout=subprocess.PIPE).communicate()[0]
        print('sent file updated')
    except:
        print('error updating reservoir sent file')


def update_battery_sent_file():
    try:
        output = subprocess.Popen(["touch","sent-battery-sms"], stdout=subprocess.PIPE).communicate()[0]
        print('battery sent file updated')
    except:
        print('error updating battery sent file')


def check_for_sms_sent_file(NOTIFICATION_ELASPED_TIME_HOURS,reservoir_level):
    try:  # if there is a reservoir sent notification file present
        last_touched_in_secs_since_epoch = subprocess.Popen(["stat", "-c", "%Y","sent-reservoir-sms"], stdout=subprocess.PIPE).communicate()[0]
        now_in_secs_since_epoch = subprocess.Popen(["printf '%(%s)T\n' -1"], stdout=subprocess.PIPE).communicate()[0]
        elapsed_secs = now_in_secs_since_epoch - last_touched_in_secs_since_epoch

        # if so, see how much time has elapsed since last SMS sent
        if elapsed_secs >= (NOTIFICATION_ELASPED_TIME_HOURS*3600):
            # send another SMS and update the reservoir sent notification file
            send_reservoir_sms(reservoir_level)
            update_reservoir_sent_file()
        else:
            print('not enough time has elapsed')
    except:
        # send an SMS and create/update the reservoir sent notification file
        send_reservoir_sms(reservoir_level)
        update_reservoir_sent_file()

def check_for_sms_sent_file_battery(NOTIFICATION_ELASPED_TIME_HOURS,voltage):
    try:  # if there is a battery sent notification file present
        last_touched_in_secs_since_epoch = subprocess.Popen(["stat", "-c", "%Y","sent-battery-sms"], stdout=subprocess.PIPE).communicate()[0]
        now_in_secs_since_epoch = subprocess.Popen(["printf '%(%s)T\n' -1"], stdout=subprocess.PIPE).communicate()[0]
        elapsed_secs = now_in_secs_since_epoch - last_touched_in_secs_since_epoch

        # if so, see how much time has elapsed since last SMS sent
        if elapsed_secs >= (NOTIFICATION_ELASPED_TIME_HOURS*3600):
            # send another SMS and update the reservoir sent notification file
            send_battery_sms(voltage)
            update_battery_sent_file()
        else:
            print('not enough time has elapsed')
    except:
        # send an SMS and create/update the reservoir sent notification file
        send_battery_sms(voltage)
        update_battery_sent_file()


if textfileTESTING == False:
    attempts = 0
    while attempts < ATTEMPTS:
        try:  # open the reservoir level file
            # from http://stackoverflow.com/questions/2860153/how-do-i-get-the-parent-directory-in-python and http://askubuntu.com/questions/350458/file-location-python
            temp = os.path.join(os.path.dirname(os.getcwd()),"monitor","reservoir.json")
            with open(temp) as data_file:
                reservoir_level = json.load(data_file)
            break
        except:
            attempts = attempts + 1
            print(attempts)
            sleep(DELAY_SECONDS)
    if attempts >= ATTEMPTS:
        reservoir_level = -99
        print ("error loading monitor/reservoir.json")
else:
    reservoir_level = RESERVOIR_TEST_VALUE

print(reservoir_level)

if timedateTESTING == False:
    # Figure out time and day of the week right NOW (http://stackoverflow.com/questions/415511/how-to-get-current-time-in-python,
    # http://stackoverflow.com/questions/1831410/python-time-comparison)
    now = datetime.now()
    now_time = now.time()
    print("now_time =",now_time)
    weekday = now.weekday()  # Get day of the week of Now (Return the day of the week as an integer, where Monday is 0 and Sunday is 6.)
    print("weekday =",weekday)
else:
    now_time = TIME_TEST_VALUE
    weekday = WEEKDAY_TEST_VALUE

# If it's (past 8pm the night before a work day and the reservoir is < 30 units) or (the reservoir is < 15 units)
if (weekday >= 0 and weekday < 4) or (weekday == 6):  # School nights
    if now_time >= SCHOOLNIGHT_TIME_THRESHOLD:
        if reservoir_level <= RESERVOIR_WARN:  # send the SMS
            print('reservoir warning: YES')
            check_for_sms_sent_file(NOTIFICATION_ELASPED_TIME_HOURS,reservoir_level)
        else:
            print('reservoir warning: NO')
    else:
        print('schoolnight time warning: NO')
        if reservoir_level <= RESERVOIR_URGENT: # send the SMS
            print('reservoir urgent: YES')
            check_for_sms_sent_file(NOTIFICATION_ELASPED_TIME_HOURS,reservoir_level)

else:
    if reservoir_level <= RESERVOIR_URGENT: # send the SMS
        print('reservoir urgent: YES')
        check_for_sms_sent_file(NOTIFICATION_ELASPED_TIME_HOURS,reservoir_level)

if reservoir_level > (RESERVOIR_WARN + 20):  # remove the sent file
    try:
        output = subprocess.Popen(["rm", "-f", "Scripts/sent-reservoir-sms"], stdout=subprocess.PIPE).communicate()[0]
    except:
        print ('error deleting sent reservoir SMS file')


# Try to grab battery voltage
try:  # open the battery level file
    temp = os.path.join(os.path.dirname(os.getcwd()),"monitor","battery.json")
    with open(temp) as data_file:
        battery_level = json.load(data_file)
    voltage = battery_level["voltage"]
    print ("voltage =",voltage)
except:
    sleep(DELAY_SECONDS)
    try:
        with open('/home/pi/openapsdev/monitor/battery.json') as data_file:
            battery_level = json.load(data_file)
        voltage = battery_level["voltage"]
        print ("voltage =",voltage)
    except:
        print ("error loading monitor/battery.json")

if voltage <= VOLTAGE_THRESHOLD:
    print('battery warning: YES')
    check_for_sms_sent_file_battery(NOTIFICATION_ELASPED_TIME_HOURS,voltage)
else:
    print('battery warning: NO')
