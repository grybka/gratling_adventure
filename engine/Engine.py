from base.AbstractDisplay import AbstractDisplay
from base.AbstractEngine import AbstractEngine
from world.GameObject import *
from world.GameLocation import *
from world.Player import Player
from enum import Enum

from base.Action import Action,get_actions
from engine.BasicActions import *
from engine.DebugActions import *


from world.LocationMap import LocationMapGrid
from world.ObjectFactory import ObjectFactory

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

#separate messages to the player from the engine logic
class TextWriter:
    def __init__(self,display:AbstractDisplay,player_object:Player):
        self.display=display
        self.player_object=player_object

    def announce_action(self,text):
        self.display.update_text("<em>"+text+"</em>\n")

    def announce_failure(self,text):
        self.display.update_text("<strong>"+text+"</strong>\n")

    def describe_room_on_entrance(self):
        my_text="\n"
        my_text+=self.player_object.location.get_entrance_text()+"\n"
        my_text+="Visible Exits: "
        my_text+=comma_separate_list([add_a(obj.get_short_description()) for obj in self.player_object.location.exits])+"\n"
        if len(self.player_object.location.get_contents())>1:
            my_text+="You see here: "
            for obj in self.player_object.location.get_contentns():
                if obj!=self.player_object:  #don't list the player in the room
                    my_text+=obj.get_short_description()+"\n"
        self.display.update_text(my_text)
        

class GameEngine(AbstractEngine):
    def __init__(self,display:AbstractDisplay,world_map=None):
        super().__init__()
        self.display=display
        self.display.update_text("Welcome to the game!\n")
        self.play_mode=PlayMode.EXPLORATION
        #Game World
        self.object_factory=ObjectFactory()
        self.player_object=Player()
        self.writer=TextWriter(display,self.player_object)

        #special actions
        




        self.world_map=world_map
        #self.assign_object_location(self.player_object,location_1)
        self.assign_object_location(self.player_object,self.world_map.get_starting_room())
        #self.player_location=start_location
        self.present_current_choices()
        #self.display.update_choices([["examine","self"],["examine","room"]])

    def post_text(self,text):
        self.display.update_text(text)

    def present_current_choices(self):
        all_possible_actions=[]
        if self.play_mode==PlayMode.EXPLORATION:
            #Get all of the normal actions that the player can perform
            actions=get_actions("exploration")
            #print("actions",actions)
            #action_templates=self.player_location.get_action_templates()
            relevant_objects=self.get_relevant_objects()
            #print("n relevant objects",len(relevant_objects))
            for action in actions:
                possible_fills=action.get_possible_fills(self.player_object,relevant_objects)
                #TODO test if possible
                for fill in possible_fills:
                    all_possible_actions.append((action,fill))
            #Add any special actions for the engine
            #all_possible_actions.append( (ActionEnterDebugMode(),[]) )
        elif self.play_mode==PlayMode.DEBUG:
            actions=get_actions("debug")
            relevant_objects=self.get_relevant_objects()
            for action in actions:
                possible_fills=action.get_possible_fills(self.player_object,relevant_objects)
                #TODO test if possible
                for fill in possible_fills:
                    all_possible_actions.append((action,fill))




        offered_actions={}
        word_choices=[]
        for action,fill in all_possible_actions:
            choice=action.to_string_list(self.player_object,fill)
            offered_actions[",".join(choice)]=(action,fill)
            word_choices.append(choice)
        self.display.update_choices(word_choices)
        self.last_presented_actions=offered_actions       

    def get_relevant_objects(self):
        objects=[self.player_object.location]
        ret=[self.player_object.location]
        ret.extend(self.player_object.location.get_accessible_objects())
        print("ret is ",ret)
        return ret
    
    def update(self):
        #check if the player has made a choice
        choice_made=self.display.get_waiting_choices()
        if choice_made is not None:
            print("Choice made:",choice_made)
            #turn the choice into a function
            action=self.last_presented_actions[",".join(choice_made)]
            time_elapsed=action[0].do_action(self.player_object,action[1])
            self.display.update_status(self.player_object.get_status_object())
            self.present_current_choices()

    def announce_action(self,text):
        self.writer.announce_action(text)

    def announce_failure(self,text):
        self.writer.announce_failure(text)

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
        #So I can make announcemnets
        #object.set_location(location)
        #location.objects.append(object)
        location.deposit_object(object)
        if object==self.player_object:
            self.player_object.known_locations.add(location.map_position)
            self.display.update_map(self.world_map.get_map_image(location,self.player_object.known_locations)  )     
            self.display.update_map_position(self.world_map.get_map_image_location(location))
            self.writer.describe_room_on_entrance()
            self.display.update_image(location.get_entrance_image())

        elif location==self.player_object.location:
            self.writer.announce_action(add_a(object.get_noun_phrase())+" appears in a flash of logic\n")
        else:
            self.writer.announce_action("They've changed something")

    def character_arrives(self,character:Character,location:GameLocation):                
        if character==self.player_object:     
            self.player_object.known_locations.add(location.map_position)   
            self.writer.describe_room_on_entrance()    
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
        #self.display.update_choices(template.get_debug_choices())

    def exit_debug_mode(self):
        self.play_mode=PlayMode.EXPLORATION
        self.display.update_map(self.world_map.get_map_image(self.player_object.location,self.player_object.known_locations)  )   

        self.display.update_text("Debug mode deactivetd\n")

    
        

    #DONE list of things the engine should handle
    #player picks up an object - transfer_object_to_inventory
    #NPC picks up object transfer_object_to_inventory
    #player moves to a new location - move_character
    #NPC moves to a new location - move_character

    #TODO list of things the engine should handle
    
    
    #player drops an object
    #NPC drops an object
    
