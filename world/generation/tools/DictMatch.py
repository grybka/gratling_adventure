import json
#Structural matching of dicts, lists, strings, and numbers
#dicts are only matched over their defined keys, capturing dict keys in not supported

def product(dictlist1,dictlist2):
    #Returns the cartesian product of two lists of dicts
    #Each dict in the first list is combined with each dict in the second list
    #The result is a list of dicts
    result=[]
    for d1 in dictlist1:
        for d2 in dictlist2:
            common_keys = set(d1.keys()).intersection(set(d2.keys()))
            #they are only equal if they are equal on the common keys
            #or if they have no common keys
            equality = [ d1[key]==d2[key] for key in common_keys ]
            if len(common_keys)==0 or all(equality):
                d={}
                d.update(d1)
                d.update(d2)
                result.append(d)
    return result

class LiteralPattern:
    def __init__(self, value):
        self.value=value

    def to_object(self):
        return self.value
    
    def get_variables(self):
        return set()
    
    def fill(self, match_dict:dict):
        return self

    def match(self, value):
        if self.value==value:
            return [{}]
        else:
            return []

class CapturePattern:
    def __init__(self):
        self.name=None

    def to_object(self):
        return "$"+self.name
    
    def get_variables(self):
        return {self.name}
    
    def fill(self, match_dict:dict):
        if self.name in match_dict:
            return LiteralPattern(match_dict[self.name])
        return self

    def match(self, value):
        return [{self.name:value}]

#TODO Sequence pattern, Or pattern

class ListPattern:
    def __init__(self, patterns):
        self.patterns=patterns

    def to_object(self):
        return [pattern.to_object() for pattern in self.patterns]
    
    def get_variables(self):
        variables=set()
        for pattern in self.patterns:
            variables.update(pattern.get_variables())
        return variables
    
    def fill(self, match_dict:dict):
        return ListPattern([pattern.fill(match_dict) for pattern in self.patterns])
    
    def match(self, value):
        if not isinstance(value,list):
            return []
        if len(value)!=len(self.patterns):
            return []
        matches=[{}]
        for i in range(len(self.patterns)):
            submatches=self.patterns[i].match(value[i])
        matches=product(matches,submatches)
        return matches

class DictPattern:
    def __init__(self, patterns):
        self.patterns=patterns

    def to_object(self):
        return {key:pattern.to_object() for key,pattern in self.patterns.items()}
    
    def get_variables(self):
        variables=set()
        for pattern in self.patterns.values():
            variables.update(pattern.get_variables())
        return variables
    
    def fill(self, match_dict:dict):
        return DictPattern({key:pattern.fill(match_dict) for key,pattern in self.patterns.items()})
    
    def match(self, value):
        if not isinstance(value,dict):
            return []
        matches=[{}]
        for key in self.patterns:
            if key in value:
                submatch=self.patterns[key].match(value[key])
                matches=product(matches,submatch)
            else:
                return []
        return matches
    
def read_pattern_from_string(x):
    obj=json.loads(x)
    return read_pattern_from_object(obj)

def read_pattern_from_object(obj):
    if isinstance(obj,dict):
        patterns={}
        for key in obj:
            patterns[key]=read_pattern_from_object(obj[key])
        return DictPattern(patterns)
    elif isinstance(obj,list):
        patterns=[]
        for item in obj:
            patterns.append(read_pattern_from_object(item))
        return ListPattern(patterns)
    elif isinstance(obj,str):
        if obj.startswith('$'):
            pattern=CapturePattern()
            pattern.name=obj[1:]
            return pattern
        else:
            return LiteralPattern(obj)
    else:
        return LiteralPattern(obj)
    
if __name__=="__main__":
    #Test the matching
    pattern=read_pattern_from_string('{"a": "b", "c": ["d", "$e"]}')
    value={"a":"b", "c":["d","f"]}
    matches=pattern.match(value)
    print("Matches:")
    for match in matches:
        print(match)