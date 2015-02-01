import random

def RandomQuerySuggestions():
   foo =    ["<a href=\'/?q=active+repositories&action=Ask+GitHub\'>active repositories</a>",
            "<a href=\'/?q=active+users&action=Ask+GitHub\'>active users</a>",
            "<a href=\'/?q=total+commits&action=Ask+GitHub\'>total commits</a>",
            "<a href=\'/?q=trending+now&action=Ask+GitHub\'>trending now</a>",
            "<a href=\'/?q=top+active+repositories+by+contributors&action=Ask+GitHub\'>top active repositories by contributors</a>",
            "<a href=\'/?q=top+active+repositories+by+commits&action=Ask+GitHub\'>top active repositories by commits</a>",
            "<a href=\'/?q=top+active+repositories+by+branches&action=Ask+GitHub\'>top active repositories by branches</a>"
            ]
   return("Suggestion: " + random.choice(foo))


