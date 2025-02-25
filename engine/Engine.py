from base.AbstractDisplay import AbstractDisplay
from base.AbstractEngine import AbstractEngine
from world.GameObject import *
from world.GameLocation import *
from world.Player import Player
from enum import Enum

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

#separate messages to the player from the engine logic
class TextWriter:
    def __init__(self,display:AbstractDisplay,player_object:Player):
        self.display=display
        self.player_object=player_object

    def announce_action(self,text):
        self.display.update_text("<em>"+text+"</em>\n")

    def announce_failure(self,text):
        self.display.update_text("<strong>"+text+"</strong>\n")

    def player_takes_item(self,item):
        self.announce_action("You take the "+item.get_choice_word()+"\n")

    def npc_takes_item(self,npc,item):
        self.announce_action(npc.get_choice_word()+" takes the "+item.get_choice_word()+"\n")

    def player_drops_item(self,item):
        self.announce_action("You drop the "+item.get_choice_word()+"\n")        

    def npc_drops_item(self,npc,item):
        self.announce_action(npc.get_choice_word()+" drops the "+item.get_choice_word()+"\n")

    def describe_room_on_entrance(self):
        my_text=""
        my_text+=self.player_object.location.get_entrance_text()+"\n"
        my_text+="You see here:\n"
        for obj in self.player_object.location.objects:
            if obj!=self.player_object:  #don't list the player in the room
                my_text+=obj.get_reference()+"\n"
        for obj in self.player_object.location.exits:
            my_text+=obj.get_reference()+"\n"
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

        #self.player_location=None

        #Time
        #time is in rounds, I suppose.  An command might take multiple rounds to execute
        #so lets say that a command must return how many rounds have passed 

        #initialization
        #location_1=GameLocation()
        #location_2=GameLocation()
        #location_3=GameLocation()
        #location_1.exits.append(GameExit(destination=location_2))
        #location_2.exits.append(GameExit(destination=location_3))
        #location_3.exits.append(GameExit(destination=location_1))
        #location_1.objects.append(Carryable())        
        self.world_map=world_map
        #self.assign_object_location(self.player_object,location_1)
        self.assign_object_location(self.player_object,self.world_map.get_starting_room())
        #self.player_location=start_location
        self.present_current_choices()
        #self.display.update_choices([["examine","self"],["examine","room"]])

    def post_text(self,text):
        self.display.update_text(text)

    def choice_made(self,choice):
        #process choice
        # that is to say, figure out which object the player is interacting with
        #Get what should be updated on the display and display it
        #then present the current choices
        pass

    def present_current_choices(self):
        if self.play_mode==PlayMode.EXPLORATION:
            #action_templates=self.player_location.get_action_templates()
            relevant_objects=self.get_relevant_objects()
            action_templates=[]
            for obj in relevant_objects:
                action_templates.extend(obj.get_action_templates())
            #print("relevant objects",relevant_objects)
            #print("aciton templates",action_templates)
            all_templates=[]
            for action_template in action_templates:
                all_templates.extend(action_template.get_filled_templates(relevant_objects))
            #add engine-specific templates
            all_templates.append(ActionTemplate(["debug"],referring_function=self.enter_debug_mode,referring_object=self.player_object))
            #print("all templates",all_templates)
            
        elif self.play_mode==PlayMode.DEBUG:
            all_templates=[]
            all_templates.append(ActionTemplate(["exit debug"],referring_function=self.exit_debug_mode,referring_object=self.player_object))
            all_templates.extend(self.object_factory.get_creation_action_templates(self.player_object))
        word_choices=[]
        
        for filled_template in all_templates:
            word_choices.append(filled_template.to_word_choices())
        #print("word choices",word_choices)
        self.display.update_choices(word_choices)
        self.last_presented_templates=all_templates
            
       

    def get_relevant_objects(self):
        ret=[self.player_object,self.player_object.location]
        ret.extend(self.player_object.location.exits)
        ret.extend(self.player_object.location.objects)
        ret.extend(self.player_object.inventory)
        #get objects in the current location
        #objects=self.player_location.get_objects()
        #get connections in the current location
        #connections=self.player_location.get_connections()
        return ret
    
    def update(self):
        #check if the player has made a choice
        choice_made=self.display.get_waiting_choices()
        if choice_made is not None:
            #print("Choice made:",choice_made)
            #turn the choice into a function
            for template in self.last_presented_templates:
                if template.matches_word_choices(choice_made):
                    #print("Template {} matches choice".format(template))
                    #print("referring object is ",template.referring_object)
                    #rounds_to_process=template.referring_object.execute_action(template)
                    rounds_to_process=template.referring_function(template)
                    #TODO time passes if the action takes time
                    self.present_current_choices()

                    break





    def announce_action(self,text):
        self.writer.announce_action(text)
        #self.display.update_text("<em>"+text+"</em>\n")    

    def assign_object_location(self,object:GameObject,location:GameLocation):
        #So I can make announcemnets
        object.set_location(location)
        location.objects.append(object)
        if object==self.player_object:
            self.display.update_map(self.world_map.get_map_image(location,self.player_object.known_locations)  )     
            self.display.update_map_position(self.world_map.get_map_image_location(location))
            self.writer.describe_room_on_entrance()
        elif location==self.player_object.location:
            self.writer.announce_action(object.get_reference()+" appears in a flash of logic\n")
        else:
            self.writer.announce_action("They've changed something")
                  

    def move_character(self,character,exit):
        self.writer.announce_action("You go through the "+exit.get_choice_word())
        character.location.objects.remove(character) #remove the character from the old location
        self.character_arrives(character,exit.destination)

    def character_arrives(self,character:Character,location:GameLocation):
        character.set_location(location)
        location.objects.append(character)
        if character==self.player_object:        
            self.writer.describe_room_on_entrance()    
            if self.play_mode==PlayMode.DEBUG:
                self.display.update_map(self.world_map.get_map_image(location,None)  )   
            else:    
                self.display.update_map(self.world_map.get_map_image(location,self.player_object.known_locations)  )   
            self.display.update_map_position(self.world_map.get_map_image_location(location))

    def transfer_object_to_inventory(self,object:Carryable,new_owner:Character):
        success,reason=new_owner.add_to_inventory(object)
        if success:
            self.player_object.location.objects.remove(object)     
            if new_owner==self.player_object:
                self.writer.player_takes_item(object)
            else:
                self.writer.npc_takes_item(object)
        else:
            if new_owner==self.player_object:
                self.writer.announce_failure("You can't take the "+object.get_choice_word()+".  "+reason)

    def transfer_object_out_of_inventory(self,object:Carryable,owner:Character,new_location:GameLocation):
        success,reason=owner.remove_from_inventory(object)
        if success:        
            new_location.objects.append(object)        
            if owner==self.player_object:
                self.writer.player_drops_item(object)
            else:
                self.writer.npc_drops_item(owner,object)                
        else:
            if owner==self.player_object:
                self.writer.announce_failure("You can't drop the "+object.get_choice_word()+".  "+reason)

    #----DEBUG MODE FUNCTIONS-----
    def enter_debug_mode(self,template):
        self.play_mode=PlayMode.DEBUG
        self.display.update_map(self.world_map.get_map_image(self.player_object.location,None)  )   

        self.display.update_text("Debug mode activated\n")
        #self.display.update_choices(template.get_debug_choices())

    def exit_debug_mode(self,template):
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
    
