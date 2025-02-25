from world.GameObject import *
from base.AbstractEngine import AbstractEngine, game_engine
from base.ActionTemplate import ActionTemplate

# This class is used to create objects in the game world.
class ObjectFactory:
    def __init__(self):
        ...

    def get_creation_action_templates(self,creator):
        return [
            ActionTemplate(["create","item"],referring_function=self.create_from_action_template,referring_object=creator)
        ]

    def create_from_action_template(self,action_template):
        if action_template.slots[1].word=="item":
            new_object=GameObject()
            new_object.name="new object"
            new_object.description="a new object"
            new_object.tags.add("debug")
            game_engine().assign_object_location(new_object,action_template.referring_object.location)
        
