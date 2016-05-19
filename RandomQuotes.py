import random

def RandomYodaQuotes():
    foo = ['<i>Always pass on what you have learned.<br/>-Yoda</i>',
            '<i>May the force be with you.<br/>-Yoda</i>', 
            '<i>When you look at the dark side, careful you must be. For the dark side looks back.<br/>-Yoda</i>', 
            '<i>You must unlearn what you have learned.<br/>-Yoda</i>',
            '<i>Do or do not. There is no try.<br/>-Yoda</i>'
            ]
    return("<p>You've got me stumped!</p><br/>" + random.choice(foo))
