from world.generation.graph_substitution.DictMatch import *

class Node:
    def __init__(self,id,data={}):
        self.id=id
        self.data=data

    def to_object(self):
        return {"id":self.id,"data":self.data}

def object_to_node(obj):
    if "data" not in obj:
        return Node(obj["id"],{})
    return Node(obj["id"],obj["data"])

class Edge:
    def __init__(self,head,tail,data={}):
        self.data=data
        self.head=head #This should be a node id
        self.tail=tail #This should be a node id

    def to_object(self):
        return {"head":self.head,"tail":self.tail,"data":self.data}

def object_to_edge(obj):
    if "data" not in obj:
        return Edge(obj["head"],obj["tail"],{})
    return Edge(obj["head"],obj["tail"],obj["data"])

class Graph:
    def __init__(self,nodes=[],edges=[]):
        self.nodes=nodes
        self.edges=edges

    def get_node(self,node_id):
        for node in self.nodes:
            if node.id==node_id:
                return node
        return None

    def remove_node(self,node_id):
        #ignores data
        self.nodes=[node for node in self.nodes if node.id != node_id]

    def remove_edge(self,head,tail):
        #ignores data
        self.edges=[edge for edge in self.edges if edge.head != head or edge.tail != tail]

    def to_object(self):
        nodes=[{"id":node.id,"data":node.data} for node in self.nodes]
        edges=[{"head":edge.head,"tail":edge.tail,"data":edge.data} for edge in self.edges]
        return {"nodes":nodes,"edges":edges}
    
    #returns a list of nodes in a breadth first walk starting at start_node
    def breadth_first_walk(self,start_node):
        visited=set()
        to_visit=[start_node]
        ret=[]
        while len(to_visit)>0:
            current=to_visit.pop(0)
            if current in visited:
                continue
            visited.add(current)
            ret.append(current)
            for edge in self.edges:
                if edge.head==current:
                    to_visit.append(edge.tail)
                if edge.tail==current:
                    to_visit.append(edge.head)
        return ret
    
def object_to_graph(obj):
    graph=Graph()
    for node in obj["nodes"]:
        graph.nodes.append(object_to_node(node))
    for edge in obj["edges"]:
        graph.edges.append(object_to_edge(edge))
    return graph

class NodePattern:
    def __init__(self,id:str,data_pattern:DictPattern):
        if id.startswith("$"):
            self.is_id_capture=True
            self.id=id[1:]
        else:
            self.is_id_capture=False
            self.id=id
        self.data=data_pattern

    def to_object(self):
        if self.is_id_capture:
            return {"id":"$"+self.id,"data_pattern":self.data.to_object()}
        else:
            return {"id":self.id,"data_pattern":self.data.to_object()}
        
    def get_variables(self):
        variables=set()
        if self.is_id_capture:
            variables.add(self.id)
        variables.update(self.data.get_variables())
        return variables
    
    def fill(self,match_dict:dict):
        if self.is_id_capture:
            if self.id in match_dict:
                return NodePattern(match_dict[self.id],self.data.fill(match_dict))
            else:
                return NodePattern("$"+self.id,self.data.fill(match_dict))
        else:
            return NodePattern(self.id,self.data.fill(match_dict))
        
    def to_node(self):
        #warning, any patterns will just be converted to objects
        return Node(self.id,self.data.to_object())

    def match(self,node:Node):
        if not self.is_id_capture:
            if self.id != node.id:
                return []
            matches=[{}]
        else:
            matches=[{self.id:node.id}]
        data_matches=self.data.match(node.data)
        #print("my data ",self.data.to_object())
        #print("its data ",node.data)
        #print("data matches",data_matches)
        matches=product(matches,data_matches)
        return matches
    
    def match_nodes(self,nodes): #perform match on a list of nodes
        ret=[]
        for node in nodes:
            ret.extend(self.match(node))
        return ret
    
def object_to_node_pattern(obj):
    if "data_pattern" in obj:
        return NodePattern(obj["id"],read_pattern_from_object(obj["data_pattern"]))
    else:
        return NodePattern(obj["id"],read_pattern_from_object({}))
    
class EdgePattern:
    def __init__(self,head:str,tail:str,data_pattern:DictPattern):
        self.data=data_pattern
        if head.startswith("$"):
            self.head=head[1:]
            self.is_head_capture=True
        else:
            self.head=head
            self.is_head_capture=False
        if tail.startswith("$"):
            self.tail=tail[1:]
            self.is_tail_capture=True
        else:
            self.tail=tail
            self.is_tail_capture=False

    def to_object(self):
        head_name="$"+self.head if self.is_head_capture else self.head
        tail_name="$"+self.tail if self.is_tail_capture else self.tail
        ret={"data":self.data.to_object(),"head":head_name,"tail":tail_name}
        return ret
    
    def get_variables(self):
        variables=set()
        if self.is_head_capture:
            variables.add(self.head)
        if self.is_tail_capture:
            variables.add(self.tail)
        variables.update(self.data.get_variables())
        return variables
    
    def fill(self,match_dict:dict):
        if self.is_head_capture:
            if self.head in match_dict:
                head=match_dict[self.head]
            else:
                head="$"+self.head
        else:
            head=self.head

        if self.is_tail_capture:
            if self.tail in match_dict:
                tail=match_dict[self.tail]
            else:
                tail="$"+self.tail
        else:
            tail=self.tail
        return EdgePattern(head,tail,self.data.fill(match_dict))
    
    def to_edge(self):
        return Edge(self.head,self.tail,self.data.to_object())

    def match(self,edge:Edge):
        ret=[{}]
        if self.is_head_capture:
            ret=product(ret,[{self.head:edge.head}])
        else:
            if self.head!=edge.head:
                return []
        if self.is_tail_capture:
            ret=product(ret,[{self.tail:edge.tail}])
        else:
            if self.tail!=edge.tail:
                return []
        data_matches=self.data.match(edge.data)
        ret=product(ret,data_matches)
        return ret
    
    def match_edges(self,edges): #perform match on a list of edges
        ret=[]
        for edge in edges:
            ret.extend(self.match(edge))
        return ret
    
def object_to_edge_pattern(obj):
    if "data_pattern" in obj:
        return EdgePattern(obj["head"],obj["tail"],read_pattern_from_object(obj["data_pattern"]))
    else:
        return EdgePattern(obj["head"],obj["tail"],read_pattern_from_object({}))
    


class GraphPattern:
    def __init__(self,nodes=[],edges=[]):
        self.nodes=nodes #NodePatterns
        self.edges=edges #EdgePatterns

    def to_object(self):
        nodes=[node.to_object() for node in self.nodes]
        edges=[edge.to_object() for edge in self.edges]
        return {"nodes":nodes,"edges":edges}
    
    def get_variables(self):
        variables=set()
        for node in self.nodes:
            variables.update(node.get_variables())
        for edge in self.edges:
            variables.update(edge.get_variables())
        return variables
    
    def fill(self,match_dict:dict):
        return GraphPattern([node.fill(match_dict) for node in self.nodes],[edge.fill(match_dict) for edge in self.edges])
    
    def to_graph(self):
        return Graph([node.to_node() for node in self.nodes],[edge.to_edge() for edge in self.edges])
    
    def match_subgraphs(self,graph):
        #match edges first because I think that's more topological
        matches=[{}]
        for edge in self.edges:
            sub_matches=edge.match_edges(graph.edges)
            matches=product(matches,sub_matches)
        if len(matches)==0:
            return []
        for node in self.nodes:
            sub_matches=node.match_nodes(graph.nodes)
            matches=product(matches,sub_matches)
        return matches

def object_to_graph_pattern(obj):
    if "nodes" in obj:
        nodes=[object_to_node_pattern(node) for node in obj["nodes"]]
    else:
        nodes=[]
    if "edges" in obj:
        edges=[object_to_edge_pattern(edge) for edge in obj["edges"]]
    else:
        edges=[]
    return GraphPattern(nodes,edges)

def execute_substitution(graph:Graph,find_pattern:GraphPattern,match_dict:dict,substitution:GraphPattern):
    remove_graph=find_pattern.fill(match_dict).to_graph()
    for node in remove_graph.nodes:
        graph.remove_node(node.id)
    for edge in remove_graph.edges:
        graph.remove_edge(edge.head,edge.tail)
    replacement=substitution.fill(match_dict)
    #TODO check if any variables are unbound in graphpattern
    unbound_variables=replacement.get_variables()
    if len(unbound_variables)>0:
        raise Exception("Unbound variables in graph pattern: {}".format(unbound_variables))
    replacement=replacement.to_graph()
    graph.nodes.extend(replacement.nodes)
    graph.edges.extend(replacement.edges)
    return graph


if __name__== "__main__":
    #Test cases
    graph=Graph()
    graph.nodes.append(Node("A",{"color":"red"}))
    graph.nodes.append(Node("B",{"color":"blue"}))
    graph.nodes.append(Node("C",{"color":"green"}))
    graph.edges.append(Edge("A","B",{"weight":1}))
    graph.edges.append(Edge("B","C",{"weight":2}))
    graph.edges.append(Edge("C","A",{"weight":3}))
    graph.edges.append(Edge("A","C",{"weight":4}))
    graph.edges.append(Edge("B","A",{"weight":5}))
    graph.edges.append(Edge("C","B",{"weight":6}))
    #print("Graph: {}".format(graph.to_object()))
    pattern=object_to_graph_pattern({"nodes":[{"id":"$idvar1","data_pattern":{"color":"red"}},{"id":"$idvar2","data_pattern":{"color":"blue"}}],"edges":[{"head":"$idvar1","tail":"$idvar2","data_pattern":"$pattern"}]})
    #print("Pattern: {}".format(pattern.to_object()))
    print(pattern.match_subgraphs(graph))

