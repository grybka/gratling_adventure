#from base.ActionTemplate import ActionTemplate,ActionTemplateSlot
from base.AbstractEngine import AbstractEngine,game_engine
from base.TaggedObject import TaggedObject,TagRequirements

global _game_object_classes
_game_object_classes={}
def register_game_object_class(class_name, class_object):
    global _game_object_classes
    _game_object_classes[class_name]=class_object

def get_game_object_class(class_name):
    global _game_object_classes
    if class_name in _game_object_classes:
        return _game_object_classes[class_name]
    else:
        raise Exception("Game object class {} not found".format(class_name))

#Types of words/phrases that I need to generate for objects
#base_noun: a nonspecific way of identifying something. door
#noun_phrase: a relatively unique description:  the east door
#short description: an iron door to the east
#TODO add more if necessary






class GameObject(TaggedObject):
    def __init__(self,base_noun="object",noun_phrase=None,short_description=None,**kwargs):
        super().__init__(**kwargs)
        self.location=None #the location that the object is in
        self.base_noun=base_noun
        self.noun_phrase=noun_phrase
        self.short_description=short_description

    def get_base_noun(self):
        return self.base_noun
        
    def get_noun_phrase(self):
        return self.noun_phrase or self.base_noun
    
    def get_choice_word(self):
        return self.get_noun_phrase()
    
    def get_short_description(self):
        return self.short_description or self.noun_phrase or self.base_noun
        
#    def get_reference(self,specific=False):
#        choice_word=self.get_choice_word()
#        if specific:
#            return "the "+choice_word
#        else:
#            if choice_word[0] in "aeiou":
#                return "an "+choice_word
#            else:
#                return "a "+choice_word
            
    def set_location(self,location):
        self.location=location

    def get_tags(self):
        return self.tags

    
#I'm considering moving to separate the object class, which represents
#game objects, from Implentation type subclasse
#So Container or Carriable might be Implementations because it just guarantees that
#they have certain functions, and an object could be one or the other or both
#but maybe I dont need this and can just have a bit of redundant code
class ContainerInterface(TaggedObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.add_tag("container")
        self.max_inventory_size=kwargs.get("max_inventory_size",10)
        self.inventory=[]

    def deposit_object(self,object:GameObject):
        #TODO REMOVE OBJECT FROM EXISTING LOCATION
        if len(self.inventory)<self.max_inventory_size:
            self.inventory.append(object)
            object.location=self
            return True,""
        else:
            return False,"The container is full"

    def withdraw_object(self,object:GameObject):
        self.inventory.remove(object)
        return True,""

class OpenableInterface(TaggedObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.add_tag("openable")
        self.add_tag("closable")
        self.is_open=False

    def open_action(self,opener:GameObject):
        if self.is_open:
            game_engine().writer.announce_failure("The "+self.get_noun_phrase()+" is already open.")
            return False,0
        game_engine().writer.announce_action("You open the "+self.get_noun_phrase())
        self.is_open=True
        return True,1

    def close_action(self,closer:GameObject):
        if not self.is_open:
            game_engine().writer.announce_failure("The "+self.get_noun_phrase()+" is already closed.")
            return False,0
        game_engine().writer.announce_action("You close the "+self.get_noun_phrase())
        return True,1
        

#The sort of object one might put in their inventory
class Carryable(GameObject):
    def __init__(self,base_noun="item"):
        super().__init__(base_noun=base_noun)
        self.tags.add("carryable")
        self.description="It's a carryable object" #description of the carryable
        #move this to player
        #self.action_templates_function_map.append(ActionTemplate(["take",self],referring_object=self,referring_function=self.take))
    
#The sort of object that can contain other objects
class Container(GameObject,ContainerInterface,OpenableInterface):
    def __init__(self,base_noun="container",is_openable=False,is_carriable=False):
        super().__init__(base_noun=base_noun)
        self.description="It's a container" #description of the container
    

#characters can move around and carry things
class Character(GameObject):
    def __init__(self,base_noun="creature"):
        super().__init__(base_noun=base_noun)
        self.description="It's a creature"
        self.inventory=[] #list of objects in the player's inventory
        self.max_inventory_size=10 #maximum number of objects that the player can carry
        self.known_locations=[] #given as map positions

    def set_location(self,location):
        super().set_location(location)
        self.known_locations.append(location.map_position)


    def add_to_inventory(self,object:Carryable):
        if len(self.inventory)<self.max_inventory_size:
            self.inventory.append(object)
            return True,""
        else:
            return False,"You can't carry any more items"
        
    def remove_from_inventory(self,object:Carryable):
        self.inventory.remove(object)
        return True,""
