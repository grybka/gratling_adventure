import pygame
from world.GameLocation import *

def add_grid_pos(a,b):
    return (a[0]+b[0],a[1]+b[1])

def opposite_dir(dir):
    return (-dir[0],-dir[1])

#This stores rooms on a grid, generates images of the map
class LocationMap:
    def __init__(self):
        #self.rooms=[]

        #Grid parameters
        self.max_grid_size=10
        self.room_grid=[]
        for i in range(self.max_grid_size):
            self.room_grid.append([])
            for j in range(self.max_grid_size):
                self.room_grid[i].append(None)
        self.exits={} #this is a map from a pair of grid parameters to a list of exits

        #drawing parameters
        self.room_width=100
        self.room_height=30
        self.room_spacing=20
        self.my_font=pygame.font.Font(None,20)

    def get_room_at_grid_position(self,grid_position):
        if not self.is_valid_grid_position(grid_position):
            return None
        return self.room_grid[grid_position[0]][grid_position[1]]

    def is_valid_grid_position(self,grid_position):
        if grid_position[0]<0 or grid_position[0]>=self.max_grid_size:
            return False
        if grid_position[1]<0 or grid_position[1]>=self.max_grid_size:
            return False
        return True

    def get_exit(self,from_room,to_room):
        key=( (from_room.map_position[0],from_room.map_position[1]),(to_room.map_position[0],to_room.map_position[1]))
        if key in self.exits:
            return self.exits[key]
        else:
            return None
        
    def get_exit_key(self,exit):
        for key in self.exits:
            if self.exits[key]==exit:
                return key
        return None
    
    def get_exit_key_direction(self,exit):
        key=self.get_exit_key(exit)
        if key is not None:
            return (key[1][0]-key[0][0],key[1][1]-key[0][1])
        else:
            return None
        #return (exit.destination.map_position[0]-exit.location.map_position[0],exit.destination.map_position[1]-exit.location.map_position[1])
        
    def add_exit(self,from_room,to_room,exit):
        key=( (from_room.map_position[0],from_room.map_position[1]),(to_room.map_position[0],to_room.map_position[1]))
        from_room.add_exit(exit)
        exit.destination=to_room
        self.exits[key]=exit

    def get_starting_grid_position(self):
        return (self.max_grid_size//2,self.max_grid_size//2)
    
    def get_starting_room(self):
        return self.room_grid[self.get_starting_grid_position()[0]][self.get_starting_grid_position()[1]]
    
    def add_room(self,room:GameLocation,grid_position):
        #print("adding room",room)
        #self.rooms.append(room)
        self.room_grid[grid_position[0]][grid_position[1]]=room
        room.map_position=grid_position
        #print("added room",room)

    def grid_position_to_map_position(self,grid_position):
        x=int((0.5+grid_position[0])*(self.room_width+self.room_spacing))
        y=int((0.5+grid_position[1])*(self.room_height+self.room_spacing))
        return (x,y)

    def get_map_image(self,location,known_locations=None):
        print("known locations {}".format(known_locations))
        width=(self.room_width+self.room_spacing)*self.max_grid_size+self.room_spacing
        height=(self.room_width+self.room_spacing)*self.max_grid_size+self.room_spacing
        my_surface=pygame.surface.Surface((width,height))
        my_surface.fill((255,255,255))
        for i in range(self.max_grid_size):
            for j in range(self.max_grid_size):
                if self.room_grid[i][j] is not None and (known_locations is None or self.room_grid[i][j].map_position in known_locations):
                    room=self.room_grid[i][j]

                    for exit in self.room_grid[i][j].exits:
                        pos=self.grid_position_to_map_position(room.map_position)
                        exit_pos=self.grid_position_to_map_position(exit.destination.map_position)
                        pygame.draw.line(my_surface,(0,0,0),pos,exit_pos)
        for i in range(self.max_grid_size):
            for j in range(self.max_grid_size):
                if self.room_grid[i][j] is not None and (known_locations is None or self.room_grid[i][j].map_position in known_locations):
                #if self.room_grid[i][j] is not None:
                    room=self.room_grid[i][j]
                    room_rect=pygame.Rect(0,0,self.room_width,self.room_height)
                    room_rect.center=self.grid_position_to_map_position(room.map_position)
                    pygame.draw.rect(my_surface,(255,255,255),room_rect) 
                    pygame.draw.rect(my_surface,(0,0,0),room_rect,1) 
                    room_text=self.my_font.render(room.get_room_name(),True,(0,0,0))
                    #if room text doesn't fit in room rect, scale it down
                    if room_text.get_width()>room_rect.width:
                        scale=0.95*room_rect.width/room_text.get_width()                        
                        room_text=pygame.transform.scale(room_text,(int(room_text.get_width()*scale),int(room_text.get_height()*scale)))
                    rect = room_text.get_rect(center=room_rect.center)
                    my_surface.blit(room_text,rect)
                    
        return my_surface

    def get_map_image_location(self,location):
        return self.grid_position_to_map_position(location.map_position)
        

class LocationMapGrid(LocationMap):
    def __init__(self):
        super().__init__()
        for i in range(self.max_grid_size):
            for j in range(self.max_grid_size):
                self.add_room(GameLocation("Room {},{}".format(i,j)),(i,j))
        for i in range(self.max_grid_size-1):
            for j in range(self.max_grid_size-1):
                self.add_exit(self.room_grid[i][j],self.room_grid[i+1][j],GameExit(choice_word="path east"))
                self.add_exit(self.room_grid[i+1][j],self.room_grid[i][j],GameExit(choice_word="path west"))
                self.add_exit(self.room_grid[i][j],self.room_grid[i][j+1],GameExit(choice_word="path south"))
                self.add_exit(self.room_grid[i][j+1],self.room_grid[i][j],GameExit(choice_word="path north"))
                #self.room_grid[i][j].exits.append(GameExit(destination=self.room_grid[i+1][j],choice_word="path east"))
                #self.room_grid[i+1][j].exits.append(GameExit(destination=self.room_grid[i][j],choice_word="path west"))
                #self.room_grid[i][j].exits.append(GameExit(destination=self.room_grid[i][j+1],choice_word="path south"))
                #self.room_grid[i][j+1].exits.append(GameExit(destination=self.room_grid[i][j],choice_word="path north"))


    

class LocationMapGrid3:
    def __init__(self):
        self.rooms=[]

        #drawing parameters
        self.room_width=100
        self.room_height=30
        self.my_font=pygame.font.Font(None,16)

        #test grid
        self.room_grid=[]
        room_spacing=20
        for i in range(4):
            self.room_grid.append([])
            for j in range(4):
                room=GameLocation("Room {},{}".format(i,j))
                self.room_grid[i].append(room)
                room.map_position=(i*(self.room_width+room_spacing)+self.room_width/2,j*(self.room_height+room_spacing)+self.room_height/2)
                self.rooms.append(room)
        for i in range(3):
            for j in range(3):
                self.room_grid[i][j].exits.append(GameExit(destination=self.room_grid[i+1][j],choice_word="path east"))
                self.room_grid[i+1][j].exits.append(GameExit(destination=self.room_grid[i][j],choice_word="path west"))
                self.room_grid[i][j].exits.append(GameExit(destination=self.room_grid[i][j+1],choice_word="path south"))
                self.room_grid[i][j+1].exits.append(GameExit(destination=self.room_grid[i][j],choice_word="path north"))


    def get_map_image(self,location):
        print("getmapimage")
        width=512
        height=512
        my_surface=pygame.surface.Surface((width,height))
        my_surface.fill((255,255,255))
        for room in self.rooms:
            for exit in room.exits:
                pygame.draw.line(my_surface,(0,0,0),room.map_position,exit.destination.map_position)
        for room in self.rooms:            
            room_rect=pygame.Rect(0,0,self.room_width,self.room_height)
            room_rect.center=room.map_position
          
            pygame.draw.rect(my_surface,(255,255,255),room_rect) 
            pygame.draw.rect(my_surface,(0,0,0),room_rect,1) 
            room_text=self.my_font.render(room.get_room_name(),True,(0,0,0))
            #if the room text doesnt fit inside room rect, then scale it down
            print("room text width",room_text.get_width())
            print("room rect width",room_rect.width)
            if room_text.get_width()>room_rect.width:
                print("scaling down")
                scale=room_rect.width/room_text.get_width()
                print("scale")
                room_text=pygame.transform.scale(room_text,(int(room_text.get_width()*scale),int(room_text.get_height()*scale)))



            rect = room_text.get_rect(center=room.map_position)
            my_surface.blit(room_text,rect)
            
        return my_surface

    def get_map_image_location(self,location):
        room=location
        return (room.map_position[0],room.map_position[1])
        
class LocationMap2:
    def __init__(self):
        side_size=4
        self.rooms=[]
        for i in range(side_size):
            self.rooms.append([])
            for j in range(side_size):
                self.rooms[i].append(GameLocation("Room {},{}".format(i,j)))
        for i in range(side_size):
            for j in range(side_size):
                if i+1<side_size:
                    self.rooms[i][j].exits.append(GameExit(destination=self.rooms[i+1][j],choice_word="path east"))
                    self.rooms[i+1][j].exits.append(GameExit(destination=self.rooms[i][j],choice_word="path west"))
                if j+1<side_size:
                    self.rooms[i][j].exits.append(GameExit(destination=self.rooms[i][j+1],choice_word="path south"))
                    self.rooms[i][j+1].exits.append(GameExit(destination=self.rooms[i][j],choice_word="path north"))
        #
        self.room_width=100
        self.room_height=30
        self.room_spacing=20
        self.my_font=pygame.font.Font(None,20)

    def get_map_image(self,location):
        width=512
        height=512
        my_surface=pygame.surface.Surface((width,height))
        my_surface.fill((255,255,255))
        for i in range(len(self.rooms)):
            for j in range(len(self.rooms[i])):
                pygame.draw.rect(my_surface,(0,0,0),pygame.Rect(i*(self.room_width+self.room_spacing),j*(self.room_height+self.room_spacing),self.room_width,self.room_height),1) 
                room_text=self.my_font.render(self.rooms[i][j].get_room_name(),True,(0,0,0))
                center=(i*(self.room_width+self.room_spacing)+self.room_width/2,j*(self.room_height+self.room_spacing)+self.room_height/2)
                rect = room_text.get_rect(center=center)
                my_surface.blit(room_text,rect)
    
        return my_surface
    
    def get_map_image_location(self,location):
        room_spacing=self.room_spacing
        for i in range(len(self.rooms)):
            for j in range(len(self.rooms[i])):
                if self.rooms[i][j]==location:
                    return (i*(self.room_width+room_spacing)+self.room_width/2,j*(self.room_height+room_spacing)+self.room_height/2)
        return (0,0)

