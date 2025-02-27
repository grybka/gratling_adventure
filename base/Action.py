from base.TaggedObject import TaggedObject,TagRequirements

class Action:
    def __init__(self,action_word="unknown action",n_args=0,tag_requirements=[]):
        self.n_args=n_args #number of arguments
        self.tag_requirements=tag_requirements #list of tag requirements for each argument
        self.action_word=action_word #word that represents the action
        #how many object arguments?
        #tag requirements for each object argument
        #I'm assuming that every action has a subject that is doing the action
        #it is treated specially in the arguments

    def get_action_word(self):
        #return the word that represents the action
        return self.action_word

    def get_n_object_arguments(self):
        #return the number of object arguments (aside from the subject)
        return self.n_args
    
    def get_tag_requirements(self):
        #return a list of tag requirements for each object argument
        #i'm ignoring subject requirements.  Maybe add it later as special function
        #must be overriden
        return self.tag_requirements

    def get_possible_fills(self,action_subject:TaggedObject,relevant_objects:list[TaggedObject]):
        #return a list of possible fills for each slot
        #this will be used to generate the action
        #the engine
        #response is in the form [ [slot1,slot2,...],[slot1,slot2,...],...]
        ret=[ [] ]
        tag_requirements=self.get_tag_requirements()
        for i in range(self.get_n_object_arguments()):
            #get the tag requirements for this slot
            #get the possible fills for this slot
            possible_fills=[]
            for obj in relevant_objects:
                #print("does {} match {}".format(obj.tags,tag_requirements[i].required_tags))
                if tag_requirements[i].matches(obj.tags):
                    #print("YES")
                    possible_fills.append(obj)
            #print("possible fills",possible_fills)
            next_ret= []
            for fill in ret:
                for x in possible_fills:
                    next_ret.append(fill+[x])
            ret=next_ret
        #print("ret is {}".format(ret))
        return ret
    
    def to_string_list(self,action_subject:TaggedObject,arguments:list[TaggedObject]): #arguments is a list of objects
        #
        #subject is suppressed, but makes the aruments symmetric
        #return a list of strings that represent the action
        ret=[ self.get_action_word() ]
        #print("arguments are",arguments)
        for arg in arguments:
            if arg is not None:
                ret.append(arg.get_choice_word())
            else:
                ret.append("None")
        return ret


    def is_action_possible(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        #must be overridden
        return True

    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        #needs to have access to the engine for this
        #but I can import it in derived classes
        #must be overridden
        print("Warning: Action.do_action() not implemented")
        ...

global _actions_by_category
_actions_by_category={}
def register_action(category:str, action:Action):
    global _actions_by_category
    if category not in _actions_by_category:
        _actions_by_category[category]=[]
    _actions_by_category[category].append(action)

def get_actions(category:str):
    global _actions_by_category
    if category in _actions_by_category:
        return _actions_by_category[category]
    else:
        raise Exception("Action category {} not found".format(category))