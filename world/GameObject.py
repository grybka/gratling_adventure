#from base.ActionTemplate import ActionTemplate,ActionTemplateSlot
from base.AbstractEngine import AbstractEngine,game_engine
from base.TaggedObject import TaggedObject,TagRequirements
from base.Action import *
from engine.BasicActions import *

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
            
    def get_accessible_objects(self):
        return []
    
    def set_location(self,location):
        self.location=location

    def get_tags(self):
        return self.tags
    
    def examine_action(self,subject:TaggedObject):
        game_engine().announce_action("There isn't anything special about the "+self.get_noun_phrase())
        return 0
    
    #This gets called for every 'relevant' object each turn
    #They get a chance to update the information presented to the user (in the AbstractEngine class)
    #and return an ActionDict, which is a map of uuids to actions that the user can select from
    #subject is the entity the player is controlling
    #available objects are 'relevant' objects to the subject
    def get_world_html_and_actions(self,subject:TaggedObject,available_objects:list[TaggedObject]) -> ActionDict:
        #Returns an html string and a list of actions that match the hyperlinks in the slot
        #remember to present extra actions if objects.has_focus is True 
        return ActionDict()
    
    def generate_action_submenus(self,submenu_id,subject:TaggedObject,available_objects:list[TaggedObject]):
        ret_actions=ActionDict()
        examine_txt=ret_actions.add_action_link(FilledAction(ActionExamine(),subject,[self]),"examine")
        return ret_actions,[examine_txt]
    
    
    
#I'm considering moving to separate the object class, which represents
#game objects, from Implentation type subclasse
#So Container or Carriable might be Implementations because it just guarantees that
#they have certain functions, and an object could be one or the other or both
#but maybe I dont need this and can just have a bit of redundant code

#Everything that can store things is a container.  A chest is a container, a location is a container
#Moving process goes as so:
#source -> can it be removed?
#destination -> can it be added?
#move happens

class ContainerInterface(TaggedObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.add_tag("container")
        self.max_inventory_size=kwargs.get("max_inventory_size",None)
        self.inventory=[]

    def get_contents(self):
        ret=[]
        ret.extend(self.inventory)
        return ret
    
    def get_accessible_objects(self):
        ret=[]
        for obj in self.inventory:
            ret.append(obj)
            ret.extend(obj.get_accessible_objects())
        return ret

    def can_deposit_object(self,object:GameObject):
        if self.max_inventory_size is None or len(self.inventory)<self.max_inventory_size:
            return True,""
        return False,"The "+self.get_noun_phrase()+" is full."
        
    def can_withdraw_object(self,object:GameObject):
        return True,""

    def deposit_object(self,object:GameObject):        
        self.inventory.append(object)
        object.location=self        

    def withdraw_object(self,object:GameObject):
        self.inventory.remove(object)        

class KeyInterface(GameObject):
    def __init__(self,base_noun="key"):
        super().__init__(base_noun=base_noun)
        self.add_tag("key")
        self.add_tag("carryable")
        self.description="It's a key" #description of the key
        self.my_lock_id=None #the lock that this key opens    

class LockableInterface(TaggedObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.add_tag("lockable")
        self.add_tag("unlockable")
        self.is_locked=False
        self.lock_id=None #if it is none, there is no lock, and this class is dormant

    def lock_exists(self):
        return self.lock_id is not None

    def can_lock(self,closer:GameObject,key:KeyInterface):
        if self.is_locked:
            return False,"The "+self.get_noun_phrase()+" is already locked."        
        if key.my_lock_id!=self.lock_id:
            return False,"The "+key.get_noun_phrase()+" does not fit the lock."
        return True,""
    
    def can_unlock(self,opener:GameObject,key:KeyInterface):
        if not self.is_locked:
            return False,"The "+self.get_noun_phrase()+" is not locked."
        if key.my_lock_id!=self.lock_id:
            return False,"The "+key.get_noun_phrase()+" does not fit the lock."
        return True,""
    
    def unlock_action(self,opener:GameObject,key:KeyInterface):
        if not self.is_locked:
            game_engine().announce_failure("The "+self.get_noun_phrase()+" is not locked.")
            return False,0
        if key.my_lock_id!=self.lock_id:
            game_engine().announce_failure("The "+key.get_noun_phrase()+" does not fit the lock.")
            return False,0
        game_engine().announce_action("You unlock the "+self.get_noun_phrase())
        self.is_locked=False
        return True,1
    
    def lock_action(self,closer:GameObject,key:KeyInterface):
        if self.is_locked:
            game_engine().announce_failure("The "+self.get_noun_phrase()+" is already locked.")
            return False,0
        if key.my_lock_id!=self.lock_id:
            game_engine().announce_failure("The "+key.get_noun_phrase()+" does not fit the lock.")
            return False,0
        game_engine().announce_action("You lock the "+self.get_noun_phrase())
        self.is_locked=True
        return True,1
    
    def generate_action_submenus(self,submenu_id,subject:TaggedObject,available_objects:list[TaggedObject]):
        verb_list=[]
        ret_actions=ActionDict()
        if self.is_locked:
            #check if any of the relevant objects can be used to unlock me
            unlocking_objects=[]
            for object in available_objects:
                if isinstance(object,KeyInterface) and self.can_unlock(subject,object)[0]:
                    unlocking_objects.append(object)
            if len(unlocking_objects)>0: #if something can unlock me
                #Make a key submenu
                key_menu_id=uuid.uuid4()
                key_menu_txt="Unlock with: "
                for key in unlocking_objects:
                    #Make an entry for each key
                    key_txt=ret_actions.add_action_link(FilledAction(ActionUnlock(),subject,[self,key]),key.get_noun_phrase())
                    key_menu_txt+=key_txt+", "
                game_engine().add_sub_menu(key_menu_id.__str__(),{"text":key_menu_txt})
                #add unlock to the submenu
                unlock_txt="<a href='javascript:ExpandActionMenu(\""+key_menu_id.__str__()+"\")'>unlock</a>"
                verb_list.append(unlock_txt)
        return ret_actions,verb_list
    
    

#do I put locks and traps here?  Or do I have a
#LockedOpenableInterface?  Lets suppose it all goes here.
#An openable object can also be:
# - stuck
# - locked (needs lock object)
# - trapped (needs trap object)
class OpenableInterface(LockableInterface,TaggedObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.add_tag("openable")
        self.add_tag("closable")
        self.add_tag("kickable")
        self.is_open=False
        self.is_stuck=False
        self.is_locked=False
        self.lock_id=None #if it is none, there is no lock
        self.is_trapped=False

    def can_open(self,opener:GameObject):
        if self.is_open:
            return False,"The "+self.get_noun_phrase()+" is already open."
        if self.is_stuck:
            return False,"The "+self.get_noun_phrase()+" is stuck."
        if self.is_locked:
            return False,"The "+self.get_noun_phrase()+" is locked."
        #print("open,locked,stuck",self.is_open,self.is_locked,self.is_stuck)
        return True,""
    
   
    
    def kick_action(self,opener:GameObject):
        if not self.has_tag("kickable"):
            game_engine().announce_failure("You can't kick the "+self.get_noun_phrase())
            return False,0
        game_engine().announce_action("You kick the "+self.get_noun_phrase())
        self.is_stuck=False
        return True
    
    

    def open_action(self,opener:GameObject):            
        possible,message=self.can_open(opener)        
        if not possible:
            game_engine().writer.announce_failure(message)
            return False,0
        game_engine().announce_action("You open the "+self.get_noun_phrase())
        self.is_open=True
        return True,1

    def close_action(self,closer:GameObject):
        if not self.is_open:
            game_engine().announce_failure("The "+self.get_noun_phrase()+" is already closed.")
            return False,0
        game_engine().announce_action("You close the "+self.get_noun_phrase())
        self.is_open=False
        return True,1
        
class LockObject(GameObject):
    def __init__(self,base_noun="lock"):
        super().__init__(base_noun=base_noun)
        self.description="It's a lock" #description of the lock
        self.my_key_id=None #the key that opens this lock
