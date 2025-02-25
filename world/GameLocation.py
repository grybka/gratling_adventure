from world.GameObject import GameObject
from base.ActionTemplate import ActionTemplate 
from base.AbstractEngine import AbstractEngine,game_engine


class GameLocation(GameObject):
    def __init__(self,short_description="a room"):
        super().__init__(choice_word="room")
        self.objects=[] #list of objects in the location
        self.exits=[] #list of connections to other locations
        self.short_description=short_description #short description of the location
        self.description="It's a room" #description of the location
        #self.image=None #image of the location

        #for drawing
        self.map_position=(0,0) #position of the location on the map

    def add_exit(self,exit):
        exit.location=self
        self.exits.append(exit)

    def get_room_name(self):
        return self.short_description

    def get_objects(self):
        return self.objects

    def get_description(self):
        return self.description
    
    def get_entrance_text(self):
        return "<u>"+self.get_room_name()+"</u>\n"+self.description

    
class GameExit(GameObject):
    def __init__(self,destination:GameLocation=None,choice_word="path",short_description="a path"):
        super().__init__(choice_word=choice_word)
        self.destination=destination #the location that this exit leads to
        #use location for origin, already in class
        self.short_description=short_description #short description of the exit
        self.description="a path" #description of the exit
        self.add_action(["go",self],self.go)
    
    def go(self,action_template):
        game_engine().move_character(game_engine().player_object,self)
        #print("go called")
        ...
