from world.GameObject import *
from world.Character import *
from base.Action import Action,ActionDict,FilledAction
from engine.DebugActions import *
from engine.BasicActions import *
from base.FocusMenu import *
import random
import uuid

#The sort of object that can contain other objects
class BasicContainer(ContainerInterface,OpenableInterface,GameObject):
    def __init__(self,base_noun="container",is_openable=False,is_carriable=False):
        super().__init__(base_noun=base_noun)
        self.description="It's a container" #description of the container
        self.add_tag("accepts_deposit")
        self.add_tag("accepts_widthdraw")
        print("my tags are ",self.tags)

class BasicItem(CarryableInterface,GameObject):
    def __init__(self,base_noun="item"):
        super().__init__(base_noun=base_noun)
        self.description="It's the most generic item you can think of" #description of the carryable
        self.is_considerable=True

    def get_focus_menu_items(self,subject:TaggedObject,available_objects:list[TaggedObject],actiondict:ActionDict):
        options=[]
        options.extend(CarryableInterface.get_focus_menu_items(self,subject,available_objects,actiondict))
        return options





class OrbOfDebug(GameObject):
    def __init__(self,base_noun="orb",noun_phrase="Orb of Debug"):
        super().__init__(base_noun=base_noun,noun_phrase=noun_phrase)
        self.tags.add("carryable")
        self.description="It's an orb of debug" #description of the orb
        self.is_considerable=True

    def get_focus_html_and_actions(self, subject:TaggedObject, available_objects:list[TaggedObject]) -> FocusMenuInfo:
        ret=FocusMenuInfo()        
        text="The Orb of Debug pulses with energy.<br>"
        possible_create_actions,_=DebugActionCreate().get_possible_fills(subject,available_objects)        
        text+="<ul>"
        for action in possible_create_actions:            
            text+="<li>Create a "+ret.actions.add_action_link(FilledAction(DebugActionCreate(),subject,action),action[0].get_noun_phrase())+"</li>"        
        text+="<li>"+ret.actions.add_action_link(FilledAction(ActionReturnFocus(),subject,[],"Return to what you were doing")        ,"Return to what you were doing.")+"</li>"
        text+="</ul>"
        ret.html=text
        return ret                



    
class BasicNPC(Character):
    def __init__(self,base_noun="npc",is_carriable=False):
        super().__init__(base_noun=base_noun)
        self.description="It's a non player character" #description of the npc

    def take_turn(self):
        #this is where the npc takes its turn
        print("turn taken")
        ...
        #example.  Move about randomly
        self.move_randomly()

    def move_randomly(self):
        #TODO THIS NEEDS TO BE REWORKED
        old_location=self.location
        exits=self.location.get_exits()
        if len(exits)==0:
            return
        #pick a random exit
        exit=random.choice(exits)
        success=game_engine().transfer_object(self,exit.destination)
        if success:
            if old_location==game_engine().player_object.location:
                game_engine().writer.announce_action(self.get_noun_phrase()+" leaves the room through the "+exit.get_noun_phrase())
            elif self.location==game_engine().player_object.location:
                if exit.exit_pair is not None:
                    game_engine().writer.announce_action(self.get_noun_phrase()+" enters the room from the "+exit.exit_pair.get_noun_phrase())
                else:
                    game_engine().writer.announce_action(self.get_noun_phrase()+" enters the room")
        else:
            game_engine().writer.announce_failure(self.get_noun_phrase()+" fails to leave the room")

class BasicKey(KeyInterface,GameObject):
    def __init__(self,base_noun="key"):
        super().__init__(base_noun=base_noun)
        self.description="It's a key" #description of the key
        self.my_lock_id=1
    