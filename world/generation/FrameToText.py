from .tools.DictMatch import DictPattern,read_pattern_from_object
from .tools.Producer import Production
from .tools.FullProducer import SearchProducer
#from world.generation.tools.DictMatch import *
#from world.generation.tools.Producer import Production
#from world.generation.tools.FullProducer import SearchProducer
#from graph_substitution.DictMatch import read_pattern_from_object,DictPattern
#from Producer import Production
#from graph_substitution.FullProducer import SearchProducer 
import yaml



class FrameToTextRule:
    def __init__(self,pattern:DictPattern,rule:Production):
        self.object_pattern=pattern
        #suppose that we map only to nonterminals
        self.cfg_rule=rule
        self.cfg_rule.max_usage=1

    def apply(self,frame:dict):
        #returns a [list of CFG rules],[list of matched dicts]
        matches=self.object_pattern.match(frame)
        ret_patterns=[]
        ret_rules=[]
        for match in matches:
            ret_patterns.append(self.object_pattern.fill(match))
            ret_rules.append(self.cfg_rule)
        return ret_rules,ret_patterns
    
class FrameToTextRuleset:
    def __init__(self):
        self.default_productions=[]
        self.rules=[]

    def load_rules(self,rule_file:str):
        with open(rule_file,'r') as f:
            rule_data=yaml.load(f,Loader=yaml.FullLoader)
        for rule in rule_data["default_productions"]:
            self.default_productions.append(Production(rule))
        for rule in rule_data["match_productions"]:
            self.rules.append(FrameToTextRule(read_pattern_from_object(rule['frame']),Production(rule['rule'])))

    def get_cfg_rules(self,frame:dict):
        #returns a list of CFG rules
        my_cfg_rules=self.default_productions.copy()
        for rule in self.rules:
            ret_rules,ret_patterns=rule.apply(frame)
            my_cfg_rules.extend(ret_rules)
        return my_cfg_rules
    
    def apply(self,frame:dict,start_symbol="START"):
        #returns a list of CFG rules
        cfg_rules=self.get_cfg_rules(frame)
        #print("building grammer from rules")
        my_grammar=SearchProducer(cfg_rules)
        #for rule in my_grammar.productions:
            #print(rule)
        #print("calling produce all")
        resp=my_grammar.produce_all(start_symbol)
        return resp

        
        
if __name__=="__main__":
    rules=FrameToTextRuleset()
    rules.load_rules("data/room_frame_to_text_rules.yaml")
    #print(rules.default_productions)
    #for rule in rules.rules:
    #    print(rule.object_pattern,rule.cfg_rule)
    test_data={"wall_material":"stone","floor_material":"wood","room_shape":"square","room_size":"large","smell":"musty","temperature":"cold","sound":"silence","light":"dim"}
    resp=rules.apply(test_data)
    for r in resp:
        print(str(r))