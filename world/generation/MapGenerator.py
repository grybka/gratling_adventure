from world.LocationMap import LocationMap, add_grid_pos, opposite_dir
from world.GameLocation import *
from world.generation.Producer import Grammar
import random
import yaml
from bs4 import BeautifulSoup

#perhaps the table looks like:
#for a given room type:
#(TODO decorations)
#probability of:
# (exit direction, exit type, room type, weight)

#example 
# (northeast, door, room, 5)


class MapGenerator1:
    def __init__(self):
        self.edge_rooms=[]
        self.my_map=LocationMap()
        with open("world/generation/dungeon_map_weights.yaml") as f:
            self.yaml_data=yaml.load(f,Loader=yaml.FullLoader)
        self.starting_room_type=self.yaml_data["starting_room_type"]

        self.location_description_grammar=Grammar()
        with open("world/generation/location_grammar.grammar") as f:
            self.location_description_grammar.load_string(f.read())

        #----Some configuration----
        #how much more likely are straights than angles
        self.exit_weights={ (-1,-1):1,(-1,0):2,(-1,1):1,(0,-1):2,(0,1):2,(1,-1):1,(1,0):2,(1,1):1}
        self.n_exit_retries=2 #how many times to try to generate an exit before giving up


    def generate_map(self):
        self.edge_rooms.append(self.generate_starting_room())
        while(len(self.edge_rooms)>0):
            room=self.edge_rooms.pop(0)
            self.generate_room(room)


    def generate_room_description(self,room,room_gen_info):
        starting_symbol=room_gen_info["description"]
        description_text=self.location_description_grammar.produce(starting_symbol)
        #print("description text is {}".format(description_text))
        soup=BeautifulSoup(description_text,"html.parser")
        #Short description is the text of the first short tag    
        tags=soup.find_all()    
        print(soup.find_all())
        room_names=soup.find_all('room_name')        
        if len(room_names)>0:
            #print("setting room name")
            room.set_room_name(room_names[0]['value'])            
        else:
            room.set_room_name(starting_symbol)
        #description here 
        #collapse double spaces in text because of the way the grammar works
        description=soup.get_text().replace("  "," ")
        room.set_description(description)
        #image here
        image_options=soup.find_all('image')
        if len(image_options)>0:
            #print("setting image")
            room.set_entrance_image(image_options[0]['value'])


        #print("room name: {}".format(room.get_room_name()))
        #print("room description: {}".format(room.get_description()))

    def generate_room(self,room):
        #Note I assume the room object has already been created in an empty sense
        edge_rooms=[]
        #TODO generate name and description
        room_type=room.generation_data['room_type']
        if room_type not in self.yaml_data['location_types']:
            print("Room type {} not found in yaml data".format(room_type))
            #this error is fatal
        room_gen_info=self.yaml_data['location_types'][room_type]
        if "description" in room_gen_info:
            self.generate_room_description(room,room_gen_info)            
        else:
            room.short_description=room_type
        #TODO generate exits
        n_exits=random.randint(1,4)
        retries=0
        while len(room.exits)<n_exits and retries<self.n_exit_retries:
            if not self.generate_exit(room,room_type):
                retries+=1
        #TODO generate objects
        return edge_rooms
    
    def get_exit_weights(self,room_type):
        exits=[]
        weights=[]
        for entry in self.yaml_data['location_types'][room_type]['exits']:
            if entry[0]=='cross':
                for exit_dir in [ (-1,0),(0,-1),(1,0),(0,1) ]:
                    exits.append( [exit_dir,entry[1],entry[2]] )
                    weights.append(entry[3])
            elif entry[0]=='ex':
                for exit_dir in [ (-1,-1),(-1,1),(1,-1),(1,1) ]:
                    exits.append( [exit_dir,entry[1],entry[2]] )
                    weights.append(entry[3])
        return exits,weights

    
    def generate_exit(self,room,room_type):
        exits,weights=self.get_exit_weights(room_type)
        exit_choice=random.choices(exits,weights=weights,k=1)[0]
        new_dir=exit_choice[0]
        exit_type=exit_choice[1]
        if not self.is_exit_open(room,new_dir):
            return False
        new_coords=(room.map_position[0]+new_dir[0],room.map_position[1]+new_dir[1])
        destination_room=self.my_map.get_room_at_grid_position(new_coords)
        if destination_room is None:
            destination_room=GameLocation("New Room")
            destination_room.generation_data['room_type']=exit_choice[2]
            self.my_map.add_room(destination_room,new_coords)
            self.edge_rooms.append(destination_room)
        self.create_exit_pair(room,destination_room,exit_choice)

        #new_exit=GameExit(choice_word=self.dir_to_name(new_dir))
        #new_exit_back=GameExit(choice_word=self.dir_to_name(opposite_dir(new_dir)))
        #self.decorate_exit_pair(new_exit,new_exit_back,exit_choice[1],new_dir,opposite_dir(new_dir))
        #self.my_map.add_exit(room,destination_room,new_exit)
        #self.my_map.add_exit(destination_room,room,new_exit_back)
        return True
        """
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
        """
        


    def generate_starting_room(self):
        room_type=self.starting_room_type
        starting_room=GameLocation("Starting Room")
        starting_room.generation_data['room_type']=self.starting_room_type

        self.my_map.add_room(starting_room,self.my_map.get_starting_grid_position())
        return starting_room


        #TODO generate name and description
        #n_exit_bounds=self.yaml_data['location_types'][room_type]['n_exits']
        #n_exits=random.randint(n_exit_bounds[0],n_exit_bounds[1])
        #n_exits=random.randint(2,4)
        #for i in range(n_exits):
        #    self.generate_exit(starting_room,room_type)
        #TODO generate exits
        #return starting_room
    
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

#    def decorate_exit_pair(self,exit1,exit2,exit_type,direction1,direction2):
    def create_exit_pair(self,room,destination_room,exit_choice):
        exit_type=exit_choice[1]
        direction1=exit_choice[0]
        direction2=opposite_dir(direction1)
        exit_info=self.yaml_data['exit_types'][exit_type]
        #print("exit info",exit_info)
        if 'class' in exit_info:
            the_class=get_game_object_class(exit_info['class'])
            exit1=the_class()
            exit2=the_class()
        else:
            exit1=GameExit(destination_room)
            exit2=GameExit(room)

        exit1.direction=self.dir_to_name(direction1)
        exit1.base_noun=exit_type
        exit2.direction=self.dir_to_name(direction2)
        exit2.base_noun=exit_type
        exit1.exit_pair=exit2
        exit2.exit_pair=exit1

        #new_exit=GameExit(choice_word=self.dir_to_name(new_dir))
        #new_exit_back=GameExit(choice_word=self.dir_to_name(opposite_dir(new_dir)))
        #self.decorate_exit_pair(new_exit,new_exit_back,exit_choice[1],new_dir,opposite_dir(new_dir))
        self.my_map.add_exit(room,destination_room,exit1)
        self.my_map.add_exit(destination_room,room,exit2)
