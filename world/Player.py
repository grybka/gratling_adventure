from base.ActionTemplate import ActionTemplate,ActionTemplateSlot,TaggedObject,TagRequirements
from world.GameObject import *

class Player(Character):
    def __init__(self):
        super().__init__(choice_word="yourself")
        #self.location=None #the location that the player is in
        self.description="It's you!"

        #self.description="You are a player" #description of the player
        #self.short_description="a player" #short description of the player
        #self.image=None #image of the player
        
        self.add_action(["take",TagRequirements(["carryable"],forbidden_tags=["carried_by_player"])],self.take)
        self.add_action(["drop",TagRequirements(["carried_by_player"])],self.drop)

    def take(self,action_template):
        object=action_template.slots[1].object
        game_engine().transfer_object_to_inventory(object,self)        
        return 0
    
    def drop(self,action_template):
        object=action_template.slots[1].object
        game_engine().transfer_object_out_of_inventory(object,self,self.location)
        
        
    def add_to_inventory(self,object:Carryable):
        success,reason=super().add_to_inventory(object)
        if success:
            object.tags.add("carried_by_player")
        return success,reason
    
    def remove_from_inventory(self,object:Carryable):
        success,reason=super().remove_from_inventory(object)
        if success:
            object.tags.remove("carried_by_player")
        return success,reason
