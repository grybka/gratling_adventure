import re
import string
import random

#Produces a string from a grammar
#Rules are given like
#FIGHTER_WEAPON -> SIMPLE_MELEE_WEAPON "\n" MARTIAL_RANGED_WEAPON [1]
#FIGHTER_WEAPON -> MARTIAL_MELEE_WEAPON "\n" SIMPLE_RANGED_WEAPON [1]
#SIMPLE_MELEE_WEAPON -> "Club (1d6)"
#Where quotation marks indicate a terminal, and no quotation marks indicate a nonterminal
#The [1] indicates the weight of the production, which is used to randomly select a production

class Symbol:
    def __init__(self):
        self.rep=""
        self.terminal=True
    def __init__(self,tok,is_term):
        self.rep=tok.replace('\\"','"')
        self.terminal=is_term
    def is_terminal(self):
        return self.terminal
    def __str__(self):
        if self.is_terminal():
            return "'"+self.rep+"'"
        else:
            return self.rep
    def __eq__(self,other):
        if not isinstance(other,Symbol):
            return False
        return self.rep==other.rep and self.terminal==other.terminal
    def __hash__(self):
        if self.is_terminal:
            return hash(self.rep+"T")
        else:
            return hash(self.rep+"F")
    @staticmethod
    def from_string(tok):
        assert(len(tok)>1)
        if tok[0]=='"':
            assert(len(tok)>2)
            return Symbol(tok[1:-1],True)
        else:
            return Symbol(tok,False)




class Production:
    def __init__(self,line):
        self.lhs=""
        self.rhs=[]
        self.weight=1
        tokens=re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', line)
        try:
            assert(len(tokens)>2)
        except:
            print("error reading {}".format(tokens))

        self.lhs=Symbol.from_string(tokens[0])
        for i in range(2,len(tokens)):
            if tokens[i][0]=='[':
                self.weight=float(tokens[i][1:-1])
            else:
                self.rhs.append(Symbol.from_string(tokens[i]))
        print("read production",self)

    def __str__(self):
        return "{} -> {} [{}]".format(self.lhs," ".join([ str(x) for x in self.rhs]),self.weight)


class Grammar:
    def __init__(self):
        self.productions={} # dictionary of symbol -> production
    def load_string(self,s:str):
        for line in s.splitlines():
            if len(line)==0 or line[0]=='#':
                continue
            p=Production(line)
            if p.lhs in self.productions:
                self.productions[p.lhs].append(p)
            else:
                self.productions[p.lhs]=[ p ]

    def produce(self,start_string:str):
        #should I always assume we start with a nonterminal?
        start_symbol=Symbol(start_string,False)
        return self._produce(start_symbol)

    def _produce(self,start_symbol:Symbol):
        out_string=""
        if start_symbol not in self.productions:
            raise Exception("no production for |{}| ({})".format(start_symbol,start_symbol.is_terminal()))
        weights=[ x.weight for x in self.productions[start_symbol] ]
        prod=random.choices(self.productions[start_symbol],weights=weights,k=1)[0]
        for tok in prod.rhs:
            if tok.is_terminal():
                out_string+=tok.rep
            else:
                out_string+=self._produce(tok)
        return out_string






#def tokenize(s):
#    return re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', s)
