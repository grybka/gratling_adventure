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

    
class GameLocation(GameObject):
    def __init__(self):
        super().__init__(choice_word="room")
        self.objects=[] #list of objects in the location
        self.exits=[] #list of connections to other locations
        self.short_description="a room" #short description of the location
        self.description="It's a room" #description of the location
        #self.image=None #image of the location

    def get_objects(self):
        return self.objects

    def get_connections(self):
        return self.connections

    def get_description(self):
        return self.description
    
    def get_entrance_text(self):
        return "You enter the "+self.short_description+"\n"+self.description+"\n"

    
class GameExit(GameObject):
    def __init__(self,destination=None):
        super().__init__(choice_word="path")
        self.destination=destination #the location that this exit leads to
        self.description="a path" #description of the exit
        self.add_action(["go",self],self.go)
    
    def go(self,action_template):
        game_engine().move_player(self)
        #print("go called")
        ...

#The sort of object one might put in their inventory
class Carryable(GameObject):
    def __init__(self):
        super().__init__(choice_word="item")
        self.tags.add("carryable")
        self.description="It's a carryable object" #description of the carryable
        #move this to player
        #self.action_templates_function_map.append(ActionTemplate(["take",self],referring_object=self,referring_function=self.take))
    
    
