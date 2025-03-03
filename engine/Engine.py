from base.AbstractDisplay import AbstractDisplay
from base.AbstractEngine import AbstractEngine,add_a,comma_separate_list
from world.GameObject import *
from world.GameLocation import *
from world.Player import Player
from world.TestObjects import *
from enum import Enum
import yaml
from base.Action import Action,get_actions
from engine.BasicActions import *
from engine.DebugActions import *


from world.LocationMap import LocationMapGrid
from world.ObjectFactory import ObjectFactory

import uuid
import os
#Loop
#Choose Action
#Perform Action
#Update World
#Update Display
#repeat

class PlayMode(Enum):
    EXPLORATION=1
    DEBUG=2


class GameEngine(AbstractEngine):
    def __init__(self,world_map=None):
        super().__init__()        
        self.reset_game_state_text()
        self.play_mode=PlayMode.EXPLORATION
        self.npcs=[] #list of all NPCs in the game
        #image file listing
        self.image_file_map=yaml.safe_load(open("static/images/images.yaml"))
        #Game World
        self.object_factory=ObjectFactory()
        self.player_object=Player()

        self.world_map=world_map
        self.assign_object_location(self.player_object,self.world_map.get_starting_room())

        orb_of_debug=OrbOfDebug()
        self.assign_object_location(orb_of_debug,self.world_map.get_starting_room())
        #test_npc=BasicNPC("test_npc")
        #self.npcs.append(test_npc)
        #self.assign_object_location(test_npc,self.world_map.get_starting_room())

        #command handling
        self.possible_actions=ActionDict()
        #game init
        self.turn_number=0              

    def player_turn_start(self):   
        relevant_objects=self.get_relevant_objects()
        self.possible_actions=ActionDict()
        for obj in relevant_objects:
            actions=obj.get_world_html_and_actions(self.player_object,relevant_objects)
            #print("adding possible action from {}".format(obj))
            self.possible_actions.add_action_dict(actions)        
            #print("possible actions is now {}".format(self.possible_actions.keys()))
        if self.play_mode==PlayMode.DEBUG:
            actions=get_debug_actions(self.player_object,relevant_objects)
            self.possible_actions.add_action_dict(actions)

        #get the image file
        #print("image file is ",self.player_object.location.get_entrance_image())
        #print("image file map is ",self.image_file_map)
        image_file=self.image_file_map["images"].get(self.player_object.location.get_entrance_image())
        #print("image file is",image_file)
        if image_file is not None:
            self.set_image("/static/images/"+image_file['file'])

    def get_relevant_objects(self):
        objects=[self.player_object.location]
        ret=[self.player_object.location]
        ret.extend(self.player_object.location.get_accessible_objects())
        #print("relevant objects are ",ret)        
        return ret
    
    def action_chosen(self,action_id):
        #Special cases.  A few special commands use a flat_out string instead of a uuid.  I can't see how this could go wrong.
        if action_id=="toggle_debug":
            if self.play_mode==PlayMode.DEBUG:
                self.exit_debug_mode()
            else:
                self.enter_debug_mode()
            self.player_turn_start()
            return
            



        my_key=uuid.UUID(action_id)
        action_fill=self.possible_actions.get_action(my_key)
        if action_fill is None:
            print("Choice made:",my_key)
            print("possible actions: ",self.possible_actions.keys())
            raise Exception("impossible action chosen.  how to debug?")
        #Reset text right here, before the action is executed
        self.reset_game_state_text()
        time_elapsed=action_fill.execute()                                        
        if time_elapsed>0:
            self.turn_number+=time_elapsed
            for npc in self.npcs:                 #other mobs take their turn
                npc.take_turn()
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


    #----DEBUG MODE FUNCTIONS-----
    def enter_debug_mode(self):
        self.play_mode=PlayMode.DEBUG
        self.announce_action("Debug mode activated")        

    def exit_debug_mode(self):
        self.play_mode=PlayMode.EXPLORATION
        self.announce_action("Debug mode deactivated")        
        
    def get_debug_actions(self,relevant_objects):
        print("This function isn't finished")
        
