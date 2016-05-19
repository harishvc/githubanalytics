import datetime
from time import gmtime, strftime
import pytz

#Humanize time in milliseconds
#Reference: http://stackoverflow.com/questions/26276906/python-convert-seconds-from-epoch-time-into-human-readable-time
def HTM(a, context):
    #print "Processing ....", a
    b = int(datetime.datetime.now().strftime("%s"))
    #print "Time NOW ...", b
    c = b - a
    #print "Time elapsed ...", c
    days = c // 86400
    hours = c // 3600 % 24
    minutes = c // 60 % 60
    seconds = c % 60
    if (days > 0): return ( str(days) + " days " + context)
    elif (hours > 0): return (str(hours) + " hours " + context)
    elif (minutes > 0): return ( str(minutes) + " minutes " + context)
    elif (seconds > 1): return (str(seconds) + " seconds " + context)
    elif (seconds == 1): return (str(seconds) + " second " + context)
    elif (seconds == 0): return ("< 1 second")
    else: return ("Now ")  #Error

#Humanize time in hours
def HTH(a):
    b = int(datetime.datetime.now().strftime("%s"))
    c = b - a
    days = c // 86400
    hours = c // 3600 % 24
    return hours

#My Timestamp used in logfile 
def MT():
    fmt = '%Y-%m-%d %H:%M:%S'
    return (datetime.datetime.now(pytz.timezone("America/Los_Angeles")).strftime(fmt))

#My Timestamp for filename
def FT():
    fmt = '%d%b%Y-%H%M%S'
    return ( datetime.datetime.now(pytz.timezone("America/Los_Angeles")).strftime(fmt) )

#Time now in epoch milliseconds
def TNEM():
    return (int(datetime.datetime.now().strftime("%s")) * 1000)

#Time then (back in minutes) is epoch milliseconds
def TTEM(Back):
    return (int(datetime.datetime.now().strftime("%s")) * 1000 - (Back * 60 * 1000))
