#https://github.com/seatgeek/fuzzywuzzy
#https://pypi.python.org/pypi/fuzzywuzzy/0.4.0

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

choices = ["trending now",
          "top organizations",
          "top contributors",
          "top repositories",
          "top new repositories"]

def compare(input):
    #print "comparing ....", input
    r = process.extract(input, choices,limit=5)
    suggestionList = ""
    #Pick top 3 if more than 75% exact
    if (r[0][1] >= 75):
        suggestionList += "<p class=\"text-info\">Did you mean:</p><ul>"
        cnt = 1
        for row in r:
            if (row[1] >= 75 and cnt <= 3):
                cnt = cnt + 1
                suggestionList += "<li><a href=\"/?q=" + str(row[0]) + "&amp;action=Search\">" + str(row[0]) + "</a></li>"
            else:
                break
        suggestionList += "</ul>"
    #Pick one if no exact       
    elif (r[0][1] >= 0):
        suggestionList += "<p class=\"text-info\">Suggestion:</p><a href=\"/?q=" + str(r[0][0]) + "&amp;action=Search\">" + str(r[0][0]) + "</a>"
    
    #print suggestionList
    return suggestionList
