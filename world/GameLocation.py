from world.GameObject import *
#from base.ActionTemplate import ActionTemplate 
from base.AbstractEngine import AbstractEngine,game_engine


class GameLocation(GameObject,ContainerInterface):
    def __init__(self,base_noun="room"):
        super().__init__(base_noun=base_noun)
        #self.objects=[] #list of objects in the location
        self.exits=[] #list of connections to other locations
        self.description="It's a room" #description of the location
        self.generation_data={} #used in generation
        #self.image=None #image of the location

        #for drawing
        self.map_position=(0,0) #position of the location on the map

    def add_exit(self,exit):
        exit.location=self
        self.exits.append(exit)

    def get_room_name(self):
        return self.get_short_description()

    #def get_objects(self):
        #return self.objects

    def get_description(self):
        return self.description
    
    def get_entrance_text(self):
        return "<u>"+self.get_room_name()+"</u>\n"+self.description

    def get_entrance_image(self):
        return "catacombs"
    
class GameExit(GameObject):
    def __init__(self,destination:GameLocation=None,base_noun="exit"):
        super().__init__(base_noun=base_noun)
        self.add_tag("exit")
        self.destination=destination #the location that this exit leads to
        self.exit_pair=None #the door that should share this status

        #use location for origin, already in class
        #stuff for words
        self.direction=None #the direction that this exit leads to


    def get_noun_phrase(self):
        if self.direction is None:
            return super().get_noun_phrase()
        else:
            return self.direction+" "+super().get_noun_phrase()
        
    def get_short_description(self):
        if self.direction is None:
            return super().get_short_description()
        else:
            return self.get_base_noun()+" to the "+self.direction

    def go_action(self,goer):
        origin=goer.location
        destination=self.destination
        #first verify it is possible
        if destination is None:
            game_engine().writer.announce_failure("You can't go that way.")
            return False,0
        success,reason=destination.can_deposit_object(goer)
        if not success:
            game_engine().writer.announce_failure(reason)
            return False,0        
        success,reason=origin.can_withdraw_object(goer)
        if not success:
            game_engine().writer.announce_failure(reason)
            return False,0        
        #do the actual move
        origin.withdraw_object(goer)
        destination.deposit_object(goer)
        #make announcements
        game_engine().writer.announce_action("You go through the "+self.get_noun_phrase())        
        game_engine().character_arrives(goer,self.destination) #add the character to the new location
        return True,1

#DoorExits can be open or closed
#if lockable, they can be locked or unlocked with the appropriate key
#they may be broken down with a kick
#locks may be picked with lockpicks
class DoorExit(GameExit,OpenableInterface):
    def __init__(self,destination:GameLocation=None):
        super().__init__(destination=destination,base_noun="door")
        self.lockable=False
        self.locked=False
        self.is_open=False
        self.tags.add("openable")
        self.tags.add("closable")
    
    def get_short_description(self):
        if self.direction is None:
            return super().get_short_description()
        else:
            if self.is_open:
                return "open "+self.get_base_noun()+" to the "+self.direction
            else:
                return "closed "+self.get_base_noun()+" to the "+self.direction

    def open_action(self,opener):
        success,time=super().open_action(opener)
        if success:
            self.exit_pair.is_open=True
        return success,time

    def close_action(self,closer):
        success,time=super().close_action(closer)
        if success and self.exit_pair is not None:
            self.exit_pair.is_open=False
        return success,1
    
    def go_action(self,goer):
        if self.is_open:
            return super().go_action(goer)
        else:
            game_engine().writer.announce_failure("The door is closed.")
            return False,0
        return True,1

register_game_object_class("DoorExit",DoorExit)