from base.Action import Action,register_action
from base.TaggedObject import TaggedObject,TagRequirements
from base.AbstractEngine import AbstractEngine,game_engine
from world.ObjectFactory import ObjectFactory

class ActionEnterDebugMode(Action):
    #enter debug mode
    def __init__(self):
        super().__init__(action_word="Debug Mode",n_args=0)
    
    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        game_engine().enter_debug_mode()
        return 0
register_action("exploration",ActionEnterDebugMode())

class ActionExitDebugMode(Action):
    #enter debug mode
    def __init__(self):
        super().__init__(action_word="Exit Debug Mode",n_args=0)
    
    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        game_engine().exit_debug_mode()
        return 0
register_action("debug",ActionExitDebugMode())

class DebugActionCreate(Action):
    #create (object)
    def __init__(self):
        super().__init__(action_word="create",n_args=1,tag_requirements=[TagRequirements(required_tags=["carryable"])])
    
    def get_possible_fills(self,action_subject:TaggedObject,relevant_objects:list[TaggedObject]):
        #override this.  I don't care about which actions are relevant
        object_factory=game_engine().object_factory
        creatable_objects=object_factory.get_creatable_objects()
        print("creatable objects",creatable_objects)
        possible_fills=[]
        for object in creatable_objects:
            possible_fills.append([TaggedObject(choice_word=object)])
        return possible_fills

    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        obj_name=arguments[0].get_choice_word()
        object_factory=game_engine().object_factory
        obj=object_factory.create_object(obj_name,action_subject.location)
        game_engine().writer.announce_action("You create the "+obj.get_choice_word())
#        action_subject.location.objects.append(obj)
        return 1
register_action("debug",DebugActionCreate())