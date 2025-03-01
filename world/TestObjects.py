from world.GameObject import *

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
    
