from base.AbstractDisplay import AbstractDisplay
from base.AbstractEngine import AbstractEngine
from world.GameObject import *
from world.Player import Player
from enum import Enum

#Loop
#Choose Action
#Perform Action
#Update World
#Update Display
#repeat

class PlayMode(Enum):
    EXPLORATION=1
    COMBAT=2

class GameEngine(AbstractEngine):
    def __init__(self,display:AbstractDisplay):
        super().__init__()
        self.display=display
        self.display.update_text("Welcome to the game!\n")
        self.play_mode=PlayMode.EXPLORATION
        #Game World
        self.player_object=Player()
        self.player_location=None

        #Time
        #time is in rounds, I suppose.  An command might take multiple rounds to execute
        #so lets say that a command must return how many rounds have passed 

        #initialization
        start_location=GameLocation()
        next_location=GameLocation()
        start_location.objects.append(Carryable())
        door=GameExit(destination=next_location)
        start_location.exits.append(door)
        self.player_location=start_location
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
        #print("all templates",all_templates)
        word_choices=[]
        for filled_template in all_templates:
            word_choices.append(filled_template.to_word_choices())
        #print("word choices",word_choices)
        self.display.update_choices(word_choices)
        self.last_presented_templates=all_templates
       

    def get_relevant_objects(self):
        ret=[self.player_object,self.player_location]
        ret.extend(self.player_location.exits)
        ret.extend(self.player_location.objects)
        #get objects in the current location
        #objects=self.player_location.get_objects()
        #get connections in the current location
        #connections=self.player_location.get_connections()
        return ret
    
    def update(self):
        #check if the player has made a choice
        choice_made=self.display.get_waiting_choices()
        if choice_made is not None:
            print("Choice made:",choice_made)
            #turn the choice into a function
            for template in self.last_presented_templates:
                if template.matches_word_choices(choice_made):
                    print("Template {} matches choice".format(template))
                    print("referring object is ",template.referring_object)
                    #rounds_to_process=template.referring_object.execute_action(template)
                    rounds_to_process=template.referring_function(template)
                    #TODO time passes if the action takes time
                    self.present_current_choices()

                    break

    def announce_action(self,text):
        self.display.update_text("<em>"+text+"</em>\n")

    def move_player(self,exit):
        self.player_enters(exit.destination)
        #self.player_location=exit.destination
        #self.present_current_choices()
        #self.display.update_map(self.player_location)
        #self.display.update_status("You are in the "+self.player_location.get_choice_word())
        #self.display.update_image(self.player_location.image)

    def player_enters(self,location):
        self.player_location=location
        self.display.update_text(location.get_entrance_text())
