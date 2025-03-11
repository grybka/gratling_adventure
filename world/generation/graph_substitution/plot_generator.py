from world.generation.graph_substitution.Graph import *
from uuid import uuid4
import random
#A plot is a unidirectional graph representing the challenges and choices that a character faces in a story
#each node represents a challenge or choice
#each edge represents the transition from one challenge or choice to another

#To generate a plot, we start with a single node representing the start of the story
#We then expand this node by adding new nodes and edges to it
#The sorts of rules are:
# - A choice adds several new nodes and edges to the graph
# - A challenge adds a single new node and edge to the graph
# - A union is the opposite of a choice, it merges several nodes and edges into a single node and edge
# - A dead end has no edges leaving it forward (need to make sure one can backtrack though)

#I could do this entirely with graph substitution, and may replace this someday  
class PlotGenerator:
    def __init__(self):
        self.start_node=Node("start",{"plot_gen_type":"start"})
        self.graph = Graph([self.start_node],[])
        self.open_nodes=[]

        n_exits=random.randint(2,3)
        for i in range(n_exits):
            self.open_nodes.append(self.add_open_node(self.start_node))

        self.options=["choice","challenge","union","dead_end","goal"]
        self.option_weights={}
        self.option_weights["choice"]=0.3
        self.option_weights["challenge"]=0.2
        self.option_weights["union"]=0.1
        self.option_weights["dead_end"]=0.1
        self.option_weights["goal"]=0.2
        self.max_paths=4 #this is the maximum number of simultaneous open paths
        #before min_nodes, goal is not an option
        self.min_nodes=10
        #after max nodes, choice and challenge are not an option
        self.max_nodes=20
        self.last_chosen="none"

    def add_open_node(self,start_node):
        new_node = Node("{}".format(len(self.graph.nodes)),{})
        new_edge = Edge(new_node.id, start_node.id,{})
        self.graph.nodes.append(new_node)
        self.graph.edges.append(new_edge)
        return new_node






    def generate_plot(self):
        #breadth or depth first?  Let's do breadth
        while len(self.open_nodes) > 0:
            #print("Open nodes: {}".format(len(self.open_nodes)))
            node = self.open_nodes.pop(0)
            #print("node was {}".format(node.to_object()))
            new_nodes=self.expand_node(node)
            #print("node now is {}".format(node.to_object()))
            
            for new_node in new_nodes:
                #print("adding to open node {}".format(new_node.to_object()))
                self.open_nodes.append(new_node)

    def expand_node(self, node:Node):
        #Still to do: disfavor unions right after choices?  maybe not
        #Maybe disfavor single-point-failure challenges
        my_options=[]
        if len(self.graph.nodes)<self.max_nodes:
            my_options+=["challenge"]
        if len(self.graph.nodes)>self.min_nodes and len(self.open_nodes)==0:
            my_options+=["goal"]
        #if we have less than the max number of paths, we can add a choice
        if len(self.open_nodes)<self.max_paths and len(self.graph.nodes)<self.max_nodes:
            my_options+=["choice"]
        #if we have more than one open node, we can add a union
        if len(self.open_nodes)>0 and self.last_chosen!="choice":
            my_options+=["union"]
        #if we have more than one open node, we can add a dead end
        if len(self.open_nodes)>0:
            my_options+=["dead_end"]
        weights=[self.option_weights[option] for option in my_options]
        #print("Graph size is {}".format(len(self.graph.nodes)))
        #print("Open nodes: {}".format(len(self.open_nodes)))
        #print("Options: {}".format(my_options))
        #print("Weights: {}".format(weights))
        my_chosen=random.choices(my_options,weights=weights,k=1)[0]
        self.last_chosen=my_chosen
        #print("chose    : {}".format(my_chosen))
        if my_chosen=="choice":
            return self.make_choice(node)
        if my_chosen=="challenge":
            return self.make_challenge(node)
        if my_chosen=="union":
            return self.make_union(node)
        if my_chosen=="dead_end":
            return self.make_dead_end(node)
        if my_chosen=="goal":
            return self.make_goal(node)
        
        

    def make_choice(self, node:Node):
        node.data["plot_gen_type"] = "choice"
        new_node_a = self.add_open_node(node)
        new_node_b = self.add_open_node(node)
        return [new_node_a, new_node_b]

    def make_challenge(self, node:Node):
        node.data["plot_gen_type"] = "challenge"
        new_node = Node("{}".format(len(self.graph.nodes)),{})
        new_edge = Edge(new_node.id, node.id,{})
        self.graph.nodes.append(new_node)
        self.graph.edges.append(new_edge)
        return [new_node]

    def make_union(self, node:Node):
        node.data["plot_gen_type"] = "union"
        other_open_nodes = [n for n in self.open_nodes if n != node]
        other_node=random.choice(other_open_nodes)
        print("union with {}".format(other_node.to_object()))
        #So will move this node up and inteprose myself as a union
        for e in self.graph.edges:
            if e.head==other_node.id:
                e.head=node.id
        #the other node should have no edges with it as the tail, so nothing here
        new_edge=Edge(other_node.id,node.id,{})
        self.graph.edges.append(new_edge)
        return []
    
    def make_dead_end(self, node:Node):
        node.data["plot_gen_type"] = "dead_end"
        return []
    
    def make_goal(self, node:Node):
        node.data["plot_gen_type"] = "goal"
        return []
    
if __name__ == "__main__":
    from VisGraph import view_graph
    random.seed(4)
    pg = PlotGenerator()
    pg.generate_plot()
    view_graph(pg.graph,"plot_gen_type")