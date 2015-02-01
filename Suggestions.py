import random

def RandomQuerySuggestions():
   foo =    ["<a href=\'/?q=active+repositories&action=Search\'>active repositories</a>",
            "<a href=\'/?q=active+users&action=Search\'>active users</a>",
            "<a href=\'/?q=total+commits&action=Search\'>total commits</a>",
            "<a href=\'/?q=trending+now&action=Search\'>trending now</a>",
            "<a href=\'/?q=top+active+repositories+by+contributors&action=Search\'>top active repositories by contributors</a>",
            "<a href=\'/?q=top+active+repositories+by+commits&action=Search\'>top active repositories by commits</a>",
            "<a href=\'/?q=top+active+repositories+by+branches&action=Search\'>top active repositories by branches</a>"
            ]
   return("Suggestion: " + random.choice(foo))


