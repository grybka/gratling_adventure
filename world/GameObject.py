from base.ActionTemplate import ActionTemplate,ActionTemplateSlot,TaggedObject
from base.AbstractEngine import AbstractEngine,game_engine

class GameObject(TaggedObject):
    def __init__(self,choice_word="object"):
        super().__init__(choice_word=choice_word)
        self.location=None #the location that the object is in


        self.description="It's an indescribable object"
        self.action_templates_function_map=[] #list of action templates and their corresponding functions
        self.add_action(["examine",self],self.examine)
        #self.action_templates_function_map=[ActionTemplate(["examine",self],referring_object=self,referring_function=self.examine)]

    def get_reference(self,specific=False):
        choice_word=self.get_choice_word()
        if specific:
            return "the "+choice_word
        else:
            if choice_word[0] in "aeiou":
                return "an "+choice_word
            else:
                return "a "+choice_word
            
    def set_location(self,location):
        self.location=location

    def get_tags(self):
        return self.tags
    
    def add_action(self,at_list,func):
        self.action_templates_function_map.append(ActionTemplate(at_list,referring_object=self,referring_function=func))

    def get_action_templates(self):
        return self.action_templates_function_map
#        return [template for template, function in self.action_templates_function_map]
        #return all the action templates that this object can perform

    def execute_action(self,action_template):
        #find the function that corresponds to the action template
        for template, function in self.action_templates_function_map:
            if template.matches_filled_template(action_template):
                function(action_template)
                return
        raise Exception("Action template not found")
    
    def examine(self,action_template):
        game_engine().announce_action("You examine the "+self.get_choice_word())
        game_engine().post_text(self.description+"\n")
        return 0

    
#The sort of object one might put in their inventory
class Carryable(GameObject):
    def __init__(self,choice_word="item"):
        super().__init__(choice_word=choice_word)
        self.tags.add("carryable")
        self.description="It's a carryable object" #description of the carryable
        #move this to player
        #self.action_templates_function_map.append(ActionTemplate(["take",self],referring_object=self,referring_function=self.take))
    
#characters can move around and carry things
class Character(GameObject):
    def __init__(self,choice_word="creature"):
        super().__init__(choice_word=choice_word)
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
