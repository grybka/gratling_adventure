#from world.LocationMap import LocationMap, add_grid_pos, opposite_dir
from world.GameLocation import *
from world.generation.Producer import Grammar
from world.generation.graph_substitution.plot_generator import PlotGenerator
from world.generation.graph_substitution.plot_to_map import PlotToMap
import random
import yaml

class GameLevel:
    def __init__(self):
        self.rooms = {} # room_id -> Room
        self.starting_room=None

    def get_starting_room(self):
        return self.starting_room


def opposite_dir(dir):
    return (-dir[0],-dir[1])

class MapGenerator2:
    def __init__(self):
        self.my_map=GameLevel()

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
        assignment=plot_to_map.plot_to_map(room_graph)
        #normalize the assignment
        """
        min_x=0
        min_y=0
        for key in assignment:
            if assignment[key][0]<min_x:
                min_x=assignment[key][0]
            if assignment[key][1]<min_y:
                min_y=assignment[key][1]
        for key in assignment:
            assignment[key]=(assignment[key][0]-min_x,assignment[key][1]-min_y)
        for node in room_graph.nodes:
            node.data["location"]=assignment[node.id]
        """
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

    def create_exit_pair(self,edge,level,assignment):
        room1=level.rooms[edge.tail]
        room2=level.rooms[edge.head]
        p1=assignment[edge.tail]
        p2=assignment[edge.head]
        direction1=(p2[0]-p1[0],p2[1]-p1[1])
        direction2=(-direction1[0],-direction1[1])
        exit1=GameExit(room2)
        exit2=GameExit(room1)
        exit1.direction=self.dir_to_name(direction1)
        exit1.base_noun="exit "
        exit2.direction=self.dir_to_name(direction2)
        exit2.base_noun="exit "
        exit1.exit_pair=exit2
        exit2.exit_pair=exit1
        room1.add_exit(exit1)
        room2.add_exit(exit2)