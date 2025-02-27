from world.GameObject import *
from base.AbstractEngine import AbstractEngine, game_engine

# This class is used to create objects in the game world.
class ObjectFactory:
    def __init__(self):
        ...

    def get_creatable_objects(self):
        #return a list of objects that can be created
        return ["item"]

    def create_object(self,object_type,location):
        new_object=Carryable()
        new_object.name="new object"
        new_object.description="a new object"
        new_object.tags.add("debug")
        game_engine().assign_object_location(new_object,location)
        return new_object
        
