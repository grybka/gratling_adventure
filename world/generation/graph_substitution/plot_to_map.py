from world.generation.graph_substitution.Graph import *
from world.generation.graph_substitution.GraphSubstitution import *
import random
from world.generation.graph_substitution.plot_generator import *

#walk through the plot graph
#it probably doesn't matter which end we start from

#get all nodes that are before challenge number n
def get_nodes_before_challenge(n,plot_graph,start_node):
    visited=set()
    to_visit=[start_node]
    ret=[]
    while len(to_visit)>0:
        current=to_visit.pop(0)
        if current in visited:
            continue
        visited.add(current)
        if "challenge_number" not in plot_graph.get_node(current).data or plot_graph.get_node(current).data["challenge_number"]<n:                    
            ret.append(current)
            for edge in plot_graph.edges:
                if edge.head==current:
                    to_visit.append(edge.tail)
                if edge.tail==current:
                    to_visit.append(edge.head)
    return ret

    


class PlotToMap:
    def __init__(self):
        self.substitutions=load_substitutions("world/generation/graph_substitution/plot_to_map_subs.yaml")

    def choose_next_location(self,location,used_locations):
        x,y=location
        possible_locs=[(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
        locs_to_choose=[ x for x in possible_locs if x not in used_locations]
        if len(locs_to_choose)==0:
            raise Exception("out of locations")
        return random.choice(locs_to_choose)
    
    def get_adjacent_locations(self,location):
        x,y=location
        return {(x+1,y),(x-1,y),(x,y+1),(x,y-1),(x+1,y+1),(x-1,y-1),(x+1,y-1),(x-1,y+1)}
    
    def generate_assignments(self,assignment,graph,node_id):
        #get the node
        node=graph.get_node(node_id)
        print("node id",node_id)
        #It has to be adjacent to each of the edges
        allowed_locations=None
        for edge in graph.edges:
            if edge.head==node_id:
                if edge.tail in assignment:
                    print("on edge ",edge.to_object())
                    if allowed_locations is None:
                        allowed_locations=self.get_adjacent_locations(assignment[edge.tail])
                    else:
                        allowed_locations=allowed_locations.intersection(self.get_adjacent_locations(assignment[edge.tail]))
                    print("allowed locations now ",edge,"  ",allowed_locations)
            if edge.tail==node_id:
                if edge.head in assignment:
                    print("on edge ",edge.to_object())
                    if allowed_locations is None:
                        allowed_locations=self.get_adjacent_locations(assignment[edge.head])
                    else:
                        allowed_locations=allowed_locations.intersection(self.get_adjacent_locations(assignment[edge.head]))
                    print("allowed locations now ",edge,"  ",allowed_locations)

        if allowed_locations is None:
            return []
        #and not in the same location as any other node
        allowed_locations=allowed_locations.difference(set(assignment.values()))
        ret=[]
        for loc in allowed_locations:
            ret.append({node_id:loc})
            
        return ret

    def get_adjancent_nodes(self,node_id,graph):
        open_nodes=set()
        for edge in graph.edges:
            if edge.head==node_id:
                open_nodes.add(edge.tail)
            if edge.tail==node_id:
                open_nodes.add(edge.head)
        return open_nodes
    
    def plot_to_rooms(self,plot_graph):
        for substitution in self.substitutions:
            working=True
            while working:
                working=False
                matches=substitution.match_subgraphs(plot_graph)
                if len(matches)>0:
                    my_match=matches[0]
                    #print("my match",my_match)
                    #print("node before substitution",plot_graph.get_node(list(my_match.values())[0]).to_object())
                    plot_graph=substitution.apply_match(plot_graph,my_match)
                    #print("node after substitution",plot_graph.get_node(list(my_match.values())[0]).to_object())
                    working=True
        return plot_graph

    def assignment_weight(self,assignments,plot_graph):
        min_x=0
        min_y=0
        max_x=0
        max_y=0
        for key,value in assignments.items():
            if value[0]<min_x:
                min_x=value[0]
            if value[0]>max_x:
                max_x=value[0]
            if value[1]<min_y:
                min_y=value[1]
            if value[1]>max_y:
                max_y=value[1]
        max_dim=max(max_x-min_x,max_y-min_y)
        num_assignments=len(assignments)
        num_nodes=len(plot_graph.nodes) #dummy value
        #check how many diagonals there are
        num_diagonals=0
        diagonal_weight=0.75
        for edge in plot_graph.edges:
            if edge.head in assignments and edge.tail in assignments:
                if abs(assignments[edge.head][0]-assignments[edge.tail][0])==1 and abs(assignments[edge.head][1]-assignments[edge.tail][1])==1:
                    num_diagonals+=1
            
        return max_dim+(num_nodes-num_assignments)+num_diagonals*diagonal_weight
        
    def plot_to_map(self,plot_graph):
        self.start_node=None
        for node in plot_graph.nodes:
            if "start_room" in node.data:
                self.start_node=node
        #The notion is to assign a location (x,y) to each node where x and y are integers
        #and have edges that connect location differing by 1 unit (or 2 at most)
        #The algorithm will be:  
        # assign 0,0 to the start node
        # follow each edge and assign an adacent location at random
        # throw hands up and give up if it doesn't fit
        # TODO use A* algorithm to generate the smallest map
        # a map assigment is a dictionary of node id to location
        #First generate the order in which I will place nodes
        #I should do a breadth first walk, but for now its the same as the nodes in order
        node_order=plot_graph.breadth_first_walk(self.start_node.id)
        #without loss of generality, I can always put the first node at 0,0 and teh second at 1,0
        print("node order is ",node_order)
        node_0=node_order.pop(0)
        node_1=node_order.pop(0)
        open_assignments=[{node_0:(0,0),node_1:(1,0)}]

        while len(open_assignments)>0:
            assignment=open_assignments.pop(0)
            print("on assignment",assignment)
            #print("#assignment, #nodes {} , {}".format(len(assignment),len(plot_graph.nodes)))
            if len(assignment)==len(plot_graph.nodes):
                #we're done
                return assignment
            #get the next node to assign
            for node_id in node_order:
                if node_id not in assignment:
                    break
            #print("worging on node",node_id)
            assignments=self.generate_assignments(assignment,plot_graph,node_id)
            for next in assignments:
                open_assignments.append(assignment|next)
            #sort open assignments by weight
            open_assignments.sort(key=lambda x: self.assignment_weight(x,plot_graph))                
            #open_assignments.sort(key=lambda x: -len(x))
        raise Exception("No assignment found")

if __name__=="__main__":
    from VisGraph import *
    random.seed(4)
    pg = PlotGenerator()
    pg.generate_plot()
    #print(pg.graph.to_object())
    plot_to_map=PlotToMap()
    #for sub in plot_to_map.substitutions:
    #    print(sub.to_object())
    #view_graph(pg.graph,"plot_gen_type")
    room_graph=plot_to_map.plot_to_rooms(pg.graph)
    view_graph(room_graph)
    assignment=plot_to_map.plot_to_map(room_graph)
    for node in room_graph.nodes:
        node.data["location"]=assignment[node.id]
    view_graph_grid(room_graph,"location")
    #print(room_graph)



