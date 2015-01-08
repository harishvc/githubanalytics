import datetime

#Humanize time in milliseconds
#Reference: http://stackoverflow.com/questions/26276906/python-convert-seconds-from-epoch-time-into-human-readable-time
def HTM(aa):
    a = int(aa)
    b = int(datetime.datetime.now().strftime("%s"))
    c = b - a
    days = c // 86400
    hours = c // 3600 % 24
    minutes = c // 60 % 60
    seconds = c % 60
    ago = "ago"
    if (days > 0): return ( str(days) + " days " + ago)
    elif (hours > 0): return (str(hours) + " hours " + ago)
    elif (minutes > 0): return ( str(minutes) + " minutes " + ago)
    elif (seconds > 0): return (str(seconds) + " seconds " + ago)
    else: return (a)  #Error


#http://www.epochconverter.com/
#1/6/2015, 8:19:34 AM PST  -> 23 hours ago
#print HTM(1420561174000/1000)
