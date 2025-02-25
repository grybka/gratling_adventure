from world.LocationMap import LocationMap, add_grid_pos, opposite_dir
from world.GameLocation import *
import random

class MapGenerator1:
    def __init__(self):
        self.edge_rooms=[]
        self.my_map=LocationMap()
        #----Some configuration----
        #how much more likely are straights than angles
        self.exit_weights={ (-1,-1):1,(-1,0):2,(-1,1):1,(0,-1):2,(0,1):2,(1,-1):1,(1,0):2,(1,1):1}
        self.n_exit_retries=2 #how many times to try to generate an exit before giving up


    def generate_map(self):
        self.generate_starting_room()
        while(len(self.edge_rooms)>0):
            room=self.edge_rooms.pop(0)
            self.generate_room(room)

    def generate_room(self,room):
        #Note I assume the room object has already been created in an empty sense
        edge_rooms=[]
        #TODO generate name and description
        #TODO generate exits
        n_exits=random.randint(1,4)
        retries=0
        while len(room.exits)<n_exits and retries<self.n_exit_retries:
            if not self.generate_exit(room):
                retries+=1
        #TODO generate objects
        return edge_rooms
    
    def generate_exit(self,room):
        #exit_dirs=self.get_open_exit_dirs(room)
        exit_dirs=self.get_exit_dirs()
        #TODO maybe a self.get exit weight function?
        weights=[ self.exit_weights[x] for x in exit_dirs ]
        new_dir=random.choices(exit_dirs,weights=weights,k=1)[0]
        if not self.is_exit_open(room,new_dir):
            return False
        new_coords=(room.map_position[0]+new_dir[0],room.map_position[1]+new_dir[1])
        destination_room=self.my_map.get_room_at_grid_position(new_coords)
        if destination_room is None:
            destination_room=GameLocation("New Room")
            self.my_map.add_room(destination_room,new_coords)
            self.edge_rooms.append(destination_room)
        new_exit=GameExit(choice_word=self.dir_to_name(new_dir))
        new_exit_back=GameExit(choice_word=self.dir_to_name(opposite_dir(new_dir)))

        self.my_map.add_exit(room,destination_room,new_exit)
        self.my_map.add_exit(destination_room,room,new_exit_back)
        return True
        


    def generate_starting_room(self):
        starting_room=GameLocation("Starting Room")
        self.my_map.add_room(starting_room,self.my_map.get_starting_grid_position())
        n_exits=random.randint(2,4)
        for i in range(n_exits):
            self.generate_exit(starting_room)
        #TODO generate exits
        return starting_room
    
    def get_exit_dirs(self):
        return [ (-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

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
        
    def is_exit_open(self,room:GameLocation,exit_dir):
        room_coords=room.map_position
        new_coords=add_grid_pos(room.map_position,exit_dir)
        #remove off-map positions
        if not self.my_map.is_valid_grid_position(new_coords):
            return False
        #remove existing exits
        for exit in room.exits:
            dir=self.my_map.get_exit_key_direction(exit)
            #print("dir {} exit {}".format(dir,exit))
            if dir==exit_dir:
                return False
        return True




    def get_open_exit_dirs(self,room):
        room_coords=room.map_position
        exit_dirs=self.get_exit_dirs()
        #remove exits off edge of map
        for exit in self.get_exit_dirs():
            new_coords=add_grid_pos(room.map_position,exit)
            if not self.my_map.is_valid_grid_position(new_coords):
                exit_dirs.remove(exit)
        #remove exits that would cross or make xs
        #TODO This requires two-way exits.  Easy to reverse
        if ((room_coords[0],room_coords[1]+1),(room_coords[0]+1,room_coords[1])) in self.my_map.exits:
            if (1,1) in exit_dirs: exit_dirs.remove( (1,1) )
        if ((room_coords[0]-1,room_coords[1]),(room_coords[0],room_coords[1]+1)) in self.my_map.exits:
            if (-1,1) in exit_dirs: exit_dirs.remove( (-1,1) )
        if ((room_coords[0],room_coords[1]-1),(room_coords[0]+1,room_coords[1])) in self.my_map.exits:
            if (1,-1) in exit_dirs: exit_dirs.remove( (1,-1) )
        if ((room_coords[0]-1,room_coords[1]),(room_coords[0],room_coords[1]-1)) in self.my_map.exits:
            if (-1,-1) in exit_dirs: exit_dirs.remove( (-1,-1) )
        
        
        
        
        for exit in room.exits:
            dir=self.my_map.get_exit_key_direction(exit)
            if dir in exit_dirs: exit_dirs.remove(dir)
        return exit_dirs
