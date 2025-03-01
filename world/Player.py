from world.GameObject import *
from world.Character import *

class Player(Character):
    def __init__(self):
        super().__init__(base_noun="yourself")
        #self.location=None #the location that the player is in

        #self.description="You are a player" #description of the player
        #self.short_description="a player" #short description of the player
        #self.image=None #image of the player

    def get_status_object(self):
        ret={"inventory":[]}
        for obj in self.inventory:
            ret["inventory"].append(obj.get_short_description())
        ret["stats"]=self.stats.get_stat_string()
        return ret
    
    def get_accessible_objects(self):
        ret=super().get_accessible_objects()
        print("player ret is ",ret)
        print("player inventory is ",self.inventory)
        return ret


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
