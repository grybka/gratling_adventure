#from world.LocationMap import LocationMap, add_grid_pos, opposite_dir
from world.GameLocation import *
from world.generation.Producer import Grammar
from world.generation.graph_substitution.plot_generator import PlotGenerator
from world.generation.graph_substitution.plot_to_map import PlotToMap
import random
import yaml
from world.generation.graph_substitution.VisGraph import *


show_graphs=True

class GameLevel:
    def __init__(self):
        self.rooms = {} # room_id -> Room
        self.starting_room=None

    def get_starting_room(self):
        return self.starting_room


def opposite_dir(dir):
    return (-dir[0],-dir[1])

class ItemNeed:
    def __init__(self,needed_by,needed_class):
        self.needed_by=needed_by #the exit or room that requires this item
        self.needed_class=needed_class#the class of the item needed TODO this will need more info
        
class MapGenerator2:
    def __init__(self):
        self.my_map=GameLevel()
        self.needed_items=[]

    def dir_to_name(self,dir):
        if dir==(-1,-1):
            return "northwest"
        elif dir==(-1,0):
            return "west"
        elif dir==(-1,1):
            return "southwest"
        elif dir==(0,-1):
            return "north"
        elif dir==(0,1):
            return "south"
        elif dir==(1,-1):
            return "northheast"
        elif dir==(1,0):
            return "east"
        elif dir==(1,1):
            return "southeast"
        else:
            return "unknown direction"

    def generate_map(self):
        pg = PlotGenerator()
        pg.generate_plot()
        plot_to_map=PlotToMap()
        room_graph=plot_to_map.plot_to_rooms(pg.graph)
        if show_graphs:
            view_graph(room_graph)
        assignment=plot_to_map.plot_to_map(room_graph)
        if show_graphs:
            for node in room_graph.nodes:
                node.data["location"]=assignment[node.id]
            view_graph_grid(room_graph,"location")
        
        ret=GameLevel()
        for node in room_graph.nodes:
            room_id=node.id
            location=assignment[node.id]
            new_room=GameLocation("{}".format(room_id))
            new_room.set_room_name("Room {}".format(room_id))
            new_room.set_description("Room {}".format(room_id))
            ret.rooms[room_id]=new_room
        ret.starting_room=ret.rooms[plot_to_map.start_node.id]

        for edge in room_graph.edges:
            self.create_exit_pair(edge,ret,assignment)            
        self.my_map=ret
        self.stock_dungeon()

    def stock_dungeon(self):
        #first identify any items that are required by challenges       
        for need in self.needed_items:
            #figure out what rooms it could go in
            #The idea is that  
        ...    

    def create_exit_pair(self,edge,level,assignment):        
        room1=level.rooms[edge.tail]
        room2=level.rooms[edge.head]
        p1=assignment[edge.tail]
        p2=assignment[edge.head]
        direction1=(p2[0]-p1[0],p2[1]-p1[1])
        direction2=(-direction1[0],-direction1[1])
        if "edge_class" in edge.data:
            the_class=get_game_object_class(edge.data['edge_class'])
            exit1=the_class(room2)
            exit2=the_class(room1)       
            #test code
            self.needed_items.append(ItemNeed(exit1,"key"))                 
        else:
            exit1=GameExit(room2)
            exit2=GameExit(room1)        
            exit1.base_noun="exit"
            exit2.base_noun="exit"
        exit1.direction=self.dir_to_name(direction1)        
        exit2.direction=self.dir_to_name(direction2)        
        exit1.exit_pair=exit2
        exit2.exit_pair=exit1
        room1.add_exit(exit1)
        room2.add_exit(exit2)