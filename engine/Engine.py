from base.AbstractDisplay import AbstractDisplay
from base.AbstractEngine import AbstractEngine
from world.GameObject import *
from world.GameLocation import *
from world.Player import Player
from world.TestObjects import *
from enum import Enum

from base.Action import Action,get_actions
from engine.BasicActions import *
from engine.DebugActions import *


from world.LocationMap import LocationMapGrid
from world.ObjectFactory import ObjectFactory

import uuid

#Loop
#Choose Action
#Perform Action
#Update World
#Update Display
#repeat

class PlayMode(Enum):
    EXPLORATION=1
    DEBUG=2

def comma_separate_list(items):
    if len(items)==0:
        return ""
    elif len(items)==1:
        return items[0]
    elif len(items)==2:
        return items[0]+" and "+items[1]
    else:
        return ", ".join(items[:-1])+", and "+items[-1]
    
def add_a(word):
    if word[0] in "aeiou":
        return "an "+word
    else:
        return "a "+word

#this class stores the state of the game - in particular actions that have happened since the last report
#it is used to update the display
class GameState:
    def __init__(self):
        self.room_text="test room text"
        self.status_text="test status text"
        self.items_text="test inventory text"
        self.event_text="test event text"
    
    def reset_game_state_text(self):
        self.room_text=""
        self.status_text=""
        self.items_text=""
        self.event_text=""

    def announce_action(self,text): #these go into events
        print("announce action: ",text)
        self.event_text+=text+"\n"

    def get_message_object(self): #will be turned into json
        return {"room_text":self.room_text,
                "status_text":self.status_text,
                "items_text":self.items_text,
                "event_text":self.event_text}        

class GameEngine(AbstractEngine,GameState):
    def __init__(self,world_map=None):
        super().__init__()        
        self.reset_game_state_text()
        self.play_mode=PlayMode.EXPLORATION
        self.npcs=[] #list of all NPCs in the game
        #Game World
        self.object_factory=ObjectFactory()
        self.player_object=Player()
        #self.writer=TextWriter(display,self.player_object)

        self.world_map=world_map
        self.assign_object_location(self.player_object,self.world_map.get_starting_room())

        test_npc=BasicNPC("test_npc")
        self.npcs.append(test_npc)
        self.assign_object_location(test_npc,self.world_map.get_starting_room())

        #command handling
        self.possible_actions=ActionDict()
        #start game
        self.turn_number=0
        status=self.player_object.get_status_object()
        status["turn_number"]=self.turn_number
        #self.display.update_status(status)        
        #self.present_current_choices()
        self.player_turn_start()

    def player_turn_start(self):
        ...
        #text,actions=self.player_object.location.get_world_html_and_actions(self.player_object,self.get_relevant_objects())
        #self.possible_actions=actions
        #self.display.update_text(text)        

    def get_relevant_objects(self):
        objects=[self.player_object.location]
        ret=[self.player_object.location]
        ret.extend(self.player_object.location.get_accessible_objects())
        #print("ret is ",ret)
        return ret
    
    def update(self):
        #check if the player has made a choice
        choice_made=self.display.get_waiting_choices()
        if choice_made is not None:
            my_key=uuid.UUID(choice_made)
            print("Choice made:",my_key)
            action_fill=self.possible_actions.get_action(my_key)
            if action_fill is None:
                print("possible actions: ",self.possible_actions)
                raise Exception("impossible action chosen.  how to debug?")
            time_elapsed=action_fill.execute()                                        
            if time_elapsed>0:
                self.turn_number+=time_elapsed
                for npc in self.npcs:
                    npc.take_turn()
                #other mobs take their turns
                ...
            
            status=self.player_object.get_status_object()
            status["turn_number"]=self.turn_number
            self.display.update_status(status)
            self.player_turn_start()                       

    def transfer_object(self,object:GameObject,destination:GameLocation):
        origin=object.location
        #first verify it is possible        
        success,reason=destination.can_deposit_object(object)
        if not success:
            self.writer.announce_failure(reason)
            return False      
        success,reason=origin.can_withdraw_object(object)
        if not success:
            self.writer.announce_failure(reason)
            return False        
        #do the actual move
        origin.withdraw_object(object)
        destination.deposit_object(object)
        #make announcements (handle that elsewhere
        return True

    def assign_object_location(self,object:GameObject,location:GameLocation):        
        location.deposit_object(object)
        if object==self.player_object:
            self.player_object.known_locations.add(location.map_position)           
        elif location==self.player_object.location:
            print("announcing action")
            self.announce_action(add_a(object.get_noun_phrase())+" appears in a flash of logic")
        else:
            print("announcing action2")
            self.announce_action("They've changed something")

    def character_arrives(self,character:Character,location:GameLocation):                
        if character==self.player_object:     
            self.player_object.known_locations.add(location.map_position)   
            #self.writer.describe_room_on_entrance()    
            if self.play_mode==PlayMode.DEBUG:
                self.display.update_map(self.world_map.get_map_image(location,None)  )   
            else:    
                self.display.update_map(self.world_map.get_map_image(location,self.player_object.known_locations)  )   
            self.display.update_map_position(self.world_map.get_map_image_location(location))
            self.display.update_image(location.get_entrance_image())


    #----DEBUG MODE FUNCTIONS-----
    def enter_debug_mode(self):
        self.play_mode=PlayMode.DEBUG
        self.display.update_map(self.world_map.get_map_image(self.player_object.location,None)  )   

        self.display.update_text("Debug mode activated\n")

    def exit_debug_mode(self):
        self.play_mode=PlayMode.EXPLORATION
        self.display.update_map(self.world_map.get_map_image(self.player_object.location,self.player_object.known_locations)  )   

        self.display.update_text("Debug mode deactivetd\n")

    
    def get_main_text(self):
        all_possible_actions,word_choices,word_bad_choices,offered_actions=self.get_all_possible_choices()
        my_text="\n"
        my_text+=self.player_object.location.get_entrance_text()+"\n"
        my_text+="Visible Exits: "
        my_text+=comma_separate_list([add_a(obj.get_short_description()) for obj in self.player_object.location.exits])+"\n"
        
