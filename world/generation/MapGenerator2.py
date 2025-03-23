#from world.LocationMap import LocationMap, add_grid_pos, opposite_dir
from world.GameLocation import *
from world.generation.graph_substitution.plot_generator import PlotGenerator
from world.generation.graph_substitution.plot_to_map import PlotToMap
import random
import yaml
from world.generation.graph_substitution.VisGraph import *
from world.TestObjects import *
from world.generation.RoomFrameGenerator import RoomFrameGenerator
from world.generation.FrameToText import FrameToTextRuleset


#show_graphs=True
show_graphs=False

class GameLevel:
    def __init__(self):
        self.rooms = {} # room_id -> Room
        self.starting_room=None

    def get_starting_room(self):
        return self.starting_room


def opposite_dir(dir):
    return (-dir[0],-dir[1])

class ItemNeed:
    def __init__(self,needed_by,needed_class,in_room,data):
        self.room=in_room #id of room that I will put the item
        self.needed_by=needed_by #the exit or room that requires this item
        self.needed_class=needed_class#the class of the item needed TODO this will need more info
        self.data=data
        
class MapGenerator2:
    def __init__(self):
        self.my_map=GameLevel()
        self.needed_items=[]
        self.room_frame_generator=RoomFrameGenerator(yaml.safe_load(open("data/room_gen_data.yaml"))["rooms"])
        self.exit_frame_generator=RoomFrameGenerator(yaml.safe_load(open("data/room_gen_data.yaml"))["exits"])
        self.room_frame_to_text=FrameToTextRuleset()
        self.room_frame_to_text.load_rules("data/room_frame_to_text_rules.yaml")
        self.exit_frame_to_text=FrameToTextRuleset()
        self.exit_frame_to_text.load_rules("data/exit_frame_to_text_rules.yaml")
     
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
            return "northeast"
        elif dir==(1,0):
            return "east"
        elif dir==(1,1):
            return "southeast"
        else:
            return "unknown direction"

    def generate_map(self):
        pg = PlotGenerator()
        pg.generate_plot()
        plot_to_map=PlotToMap("data/plot_to_map_subs.yaml")
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
            exit=self.create_exit_pair(edge,ret,assignment)     
            #check if this exit is a challenge, and assign a needed item
            if "before_challenge" in edge.data:
                #pick a room to stock the item in
                print(list(edge.data["before_challenge"]))
                room_id=random.choice(list(edge.data["before_challenge"]))
                print("adding item need for room {}".format(room_id))
                self.needed_items.append(ItemNeed(None,"key",room_id,{"door_to_unlock": exit}))
        self.my_map=ret
        self.stock_level()


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
            #self.needed_items.append(ItemNeed(exit1,"key"))                 
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
        return exit1

    def stock_level(self):
        #write room descriptions
        for room in self.my_map.rooms.values():
            #print("generate frame")
            room_frame=self.room_frame_generator.generate()
            #print("frame is {}".format(room_frame))
            descs=self.room_frame_to_text.apply(room_frame)
            roomnames=self.room_frame_to_text.apply(room_frame,"ROOMNAME")
            roomname=str(random.choice(roomnames))
            #capitize first letter of room name
            print([s.capitalize() for s in roomname.split(" ")])
            roomname=" ".join([s.capitalize() for s in roomname.split(" ")])
            room.set_room_name(roomname)
            if len(descs)==0:
                raise Exception("no descriptions generated for room frame {}".format(room_frame))
            room.set_description(str(random.choice(descs)).capitalize())
            for exit in room.exits:                     
                exit_frame=self.exit_frame_generator.generate()
                exit_frame["direction"]=exit.direction
                #print("exit frame is {}".format(exit_frame))
                exit_descs=self.exit_frame_to_text.apply(exit_frame)
                exit_nounphrase=str(random.choice(exit_descs))
                exit.set_noun_phrase(exit_nounphrase)
                ...
        


        #first check which challenges need items
        counter=1
        for item_need in self.needed_items:
            #stock the item in the room that needs it
            #TODO need to know what class of item to stock
            item_need.data["door_to_unlock"].exit_pair.set_lock_id(counter) #set the lock id for the exit pair
            item=BasicKey("key {}".format(counter),counter)
            self.my_map.rooms[item_need.room].deposit_object(item)
            item_need.data["door_to_unlock"].set_description("There is a large number {} painted on the door".format(counter))
            counter+=1