from base.ActionTemplate import ActionTemplate,ActionTemplateSlot,TaggedObject,TagRequirements
from world.GameObject import *

class Player(GameObject):
    def __init__(self):
        super().__init__(choice_word="yourself")
        #self.location=None #the location that the player is in
        self.description="It's you!"

        self.inventory=[] #list of objects in the player's inventory
        self.max_inventory_size=10 #maximum number of objects that the player can carry

        #self.description="You are a player" #description of the player
        #self.short_description="a player" #short description of the player
        #self.image=None #image of the player
        
        self.add_action(["take",TagRequirements(["carryable"])],self.take)

    def take(self,action_template):
        object=action_template.slots[1].object
        game_engine().announce_action("You take the "+self.get_choice_word())
        game_engine().post_text(self.description+"\n")
        return 0
