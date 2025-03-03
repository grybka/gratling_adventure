from world.GameObject import *
from world.Character import *
import random

#The sort of object that can contain other objects
class BasicContainer(ContainerInterface,OpenableInterface,GameObject):
    def __init__(self,base_noun="container",is_openable=False,is_carriable=False):
        super().__init__(base_noun=base_noun)
        self.description="It's a container" #description of the container
        self.add_tag("accepts_deposit")
        self.add_tag("accepts_widthdraw")
        print("my tags are ",self.tags)

#The sort of object one might put in their inventory
class Carryable(GameObject):
    def __init__(self,base_noun="item"):
        super().__init__(base_noun=base_noun)
        self.tags.add("carryable")
        self.description="It's a carryable object" #description of the carryable
        #move this to player
        #self.action_templates_function_map.append(ActionTemplate(["take",self],referring_object=self,referring_function=self.take))
    
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
    