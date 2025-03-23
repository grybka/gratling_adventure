
def add_a_or_an(s:str):    
    #Returns a string with the correct article (a/an) for the given string.    
    if len(s) == 0:
        return s
    if s[0] in "aeiou":
        return "an "+s
    return "a "+s