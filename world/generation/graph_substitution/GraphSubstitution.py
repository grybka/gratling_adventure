from world.generation.graph_substitution.Graph import *
import yaml
import uuid

class GraphSubstitution:
    def __init__(self,rule_name:str,find_pattern:GraphPattern,replace_pattern:GraphPattern):
        self.rule_name=rule_name
        self.find_pattern=find_pattern
        self.replace_pattern=replace_pattern
        #TODO info about the substitution
        #like, what variables need to be created

    def to_object(self):
        return {"rule_name":self.rule_name,"find_graph":self.find_pattern.to_object(),"replace_graph":self.replace_pattern.to_object()}

    def match_subgraphs(self,graph:Graph):
        return self.find_pattern.match_subgraphs(graph)
    
    def apply_match(self,graph:Graph,match_dict:dict):
        remove_graph=self.find_pattern.fill(match_dict).to_graph()
        for node in remove_graph.nodes:
            graph.remove_node(node.id)
        for edge in remove_graph.edges:
            graph.remove_edge(edge.head,edge.tail)
        replacement=self.replace_pattern.fill(match_dict)
        #check if any variables are unbound in graphpattern
        unbound_variables=replacement.get_variables()
        newvar_dict={}
        for variable in unbound_variables:
            new_name=uuid.uuid4().hex
            newvar_dict[variable]=new_name
        replacement=replacement.fill(newvar_dict)
        if len(unbound_variables)>0:
            raise Exception("Unbound variables in graph pattern: {}".format(unbound_variables))
        replacement=replacement.to_graph()
        graph.nodes.extend(replacement.nodes)
        graph.edges.extend(replacement.edges)
        return graph

def object_to_graph_substitution(obj):
    rule_name=obj["rule_name"]
    find_pattern=object_to_graph_pattern(obj["find_graph"])
    replace_pattern=object_to_graph_pattern(obj["replace_graph"])
    return GraphSubstitution(rule_name,find_pattern,replace_pattern)

def load_substitutions(fname):
    data=yaml.safe_load(open(fname,'r'))
    substitutions=[]
    for substitution in data["substitution_rules"]:
        substitutions.append(object_to_graph_substitution(substitution))
    return substitutions

if __name__=="__main__":
    #sub_info=yaml.safe_load(open("adventure_maker.yaml",'r'))
    substitutions=load_substitutions("adventure_maker.yaml")
    print("n substitutions",len(substitutions))
    #print(substitutions)
    test_graph={"nodes":[{"id":"start"},{"id":"goal"}],"edges":[{"head":"start","tail":"goal"}]}
    test_graph=object_to_graph(test_graph)
    for substitution in substitutions:
        print("Rule",substitution.rule_name)
        print("Find Graph")
        print(substitution.find_pattern.to_object())
        matches=substitution.match_subgraphs(test_graph)
        print("Matches for rule",substitution.rule_name)
        print("n matches",len(matches)) 
        my_match=matches[0]
        new_graph=substitution.apply_match(test_graph,my_match)
        #print("New Graph")
        #print(new_graph.to_object())
        
        #print("Matches for rule",substitution.rule_name)
        #for match in matches:
        #    print(match)
        #print()