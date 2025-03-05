from world.GameObject import *
#from base.ActionTemplate import ActionTemplate 
from base.AbstractEngine import AbstractEngine,game_engine
from base.Action import Action,ActionDict,FilledAction
from engine.BasicActions import *
from base.FocusMenu import *

#Needs to have:
#room name  (this is what shows up on the map.  3 words long max)
#description  (what gets read when you enter the room)
class GameLocation(ContainerInterface,GameObject,FocusMenu):
    def __init__(self,base_noun="room"):
        super().__init__(base_noun=base_noun)
        #self.objects=[] #list of objects in the location
        self.exits=[] #list of connections to other locations
        self.room_name="room name"
        self.description="It's a room" #description of the location
        self.generation_data={} #used in generation
        #self.image=None #image of the location

        #for drawing
        self.map_position=(0,0) #position of the location on the map
        self.image_name=None

    def get_exits(self):
        return self.exits

    def get_accessible_objects(self):
        ret=[]
        for obj in self.inventory:
            ret.append(obj)
            ret.extend(obj.get_accessible_objects())
        for exit in self.exits:
            ret.append(exit)
            ret.extend(exit.get_accessible_objects())
        return ret    

    def add_exit(self,exit):
        exit.location=self
        self.exits.append(exit)

    def get_room_name(self):
        return self.room_name
    
    def set_room_name(self,room_name):
        self.room_name=room_name

    def get_objects(self):
        return self.objects
    
    def set_description(self,description):
        self.description=description

    def get_description(self):
        return self.description
    
    def get_entrance_text(self):
        return "<u>"+self.get_room_name()+"</u>\n"+self.description

    def set_entrance_image(self,image_name):
        self.image_name=image_name

    def get_entrance_image(self):
        return self.image_name
    
    def get_focus_html_and_actions(self, subject:TaggedObject, available_objects:list[TaggedObject]) -> FocusMenuInfo:
        ret=FocusMenuInfo()
        ret.html=self.get_entrance_text()+"<br>"        
        for exit in self.exits:
            ret.add_text_and_action(exit.get_exit_html_and_actions(subject,available_objects))    
        if len(self.get_contents())>0:
            ret.html+="<br>Objects in the room:<br>"
        for obj in self.get_contents():
            if obj is not subject:
                ret.add_text_and_action(obj.get_item_html_and_actions(subject,available_objects)) 
        print("actions: "+str(ret.actions))      
        return ret

    
    def get_world_html_and_actions(self,subject:TaggedObject,available_objects:list[GameObject]) -> ActionDict:
        engine=game_engine()
        engine.set_room_description(self.get_entrance_text())
        actions=ActionDict()            
        #for exit in self.exits:
        #    exit_text,exit_actions=exit.get_world_html_and_actions(subject,available_objects)
        #    ret_text+=exit_text+"\n"
        #    actions.add_action_dict(exit_actions)      

        return actions
    
    
class GameExit(GameObject):
    def __init__(self,destination:GameLocation=None,base_noun="exit"):
        super().__init__(base_noun=base_noun)
        self.add_tag("exit")
        self.destination=destination #the location that this exit leads to
        self.exit_pair=None #the door that should share this status

        #use location for origin, already in class
        #stuff for words
        self.direction=None #the direction that this exit leads to
        self.is_considerable=False

    def is_passable(self):
        return True

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
        success=game_engine().transfer_object(goer,self.destination)
        if success:            
            game_engine().announce_action("You go through the "+self.get_noun_phrase())
            return True,1
        return False,0
    
    #called from the room when making its menu
    def get_exit_html_and_actions(self,subject:TaggedObject,available_objects:list[GameObject]):
        #Returns an html string and a list of actions that match the hyperlinks in the slot        
        ret_action=ActionDict()
        go_action=FilledAction(ActionGo(),subject,[self],"Go through the "+self.get_noun_phrase())        
        ret_txt=ret_action.add_action_link(go_action,"Go")+" through the "+self.get_focus_noun_phrase(subject,ret_action)+"."        
        return ret_txt,ret_action

#DoorExits can be open or closed
#if lockable, they can be locked or unlocked with the appropriate key
#they may be broken down with a kick
#locks may be picked with lockpicks
class DoorExit(GameExit,OpenableInterface):
    def __init__(self,destination:GameLocation=None):
        super().__init__(destination=destination,base_noun="door")        
        self.is_open=False
        self.is_stuck=False
        self.lock_id=None
        self.is_locked=False

    def is_passable(self):
        return self.is_open
    
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
            game_engine().announce_failure("The door is closed.")
            return False,0
        
    #def get_exit_html_and_actions(self,subject:TaggedObject,available_objects:list[GameObject]):
        #...
        #if the door is open, then one can go or focus on it
        #if the player believes the door is closed, then they can open it
        #if the player believes the door to be locked, then they can try to unlock it
        #if the player believes the door to be stuck, then they can try to unstick it


    def get_world_html_and_actions(self,subject:TaggedObject,available_objects:list[GameObject]):
        #Returns an html string and a list of actions that match the hyperlinks in the slot        
        ret_txt=""
        ret_actions=ActionDict()
        focus_action=FilledAction(ActionFocus(),subject,[self],"Consider the "+self.get_noun_phrase())
        if self.is_open:
            close_action=FilledAction(ActionClose(),subject,[self],"Close the "+self.get_noun_phrase())
            state_txt="an "+ret_actions.add_action_link(close_action,"open")            
        else:
            open_action=FilledAction(ActionOpen(),subject,[self],"Open the "+self.get_noun_phrase())
            state_txt="a "+ret_actions.add_action_link(open_action,"closed")    
        go_action=FilledAction(ActionGo(),subject,[self],"Go through the "+self.get_noun_phrase())
        ret_txt="There is "+state_txt+" "+ret_actions.add_action_link(focus_action,self.get_base_noun())+" to the "+ret_actions.add_action_link(go_action,self.direction)+"."
        game_engine().add_exit_info(ret_txt)
        #Actions that require submenus                
        #if self.has_focus:
            #ret_actions.add_action_dict(self.get_focus_html_and_actions(subject,available_objects))
            #self.has_focus=False
        return ret_actions       

register_game_object_class("DoorExit",DoorExit)