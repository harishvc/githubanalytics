import random

def RandomQuerySuggestions():
   foo =    ["<a href=\'/?q=active+repositories&action=Ask+GitHub\'>active repositories</a>",
            "<a href=\'/?q=active+users&action=Ask+GitHub\'>active users</a>",
            "<a href=\'/?q=total+commits&action=Ask+GitHub\'>total commits</a>",
            ]
   return("Suggestion: " + random.choice(foo))
