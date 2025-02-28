from base.Action import Action,register_action
from base.TaggedObject import TaggedObject,TagRequirements
from base.AbstractEngine import AbstractEngine,game_engine

class ActionGo(Action):
    #go (exit)
    def __init__(self):
        super().__init__(action_word="go",n_args=1,tag_requirements=[TagRequirements(required_tags=["exit"])])
    
    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        exit=arguments[0]
        success,time=exit.go_action(action_subject)
        return time
register_action("exploration",ActionGo())

class ActionTake(Action):
    #take (object)
    def __init__(self):
        super().__init__(action_word="take",n_args=1,tag_requirements=[TagRequirements(required_tags=["carryable"])])
    
    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        obj=arguments[0]
        origin=obj.location
        destination=action_subject
        #first verify it is possible        
        success,reason=destination.can_deposit_object(obj)
        if not success:
            game_engine().writer.announce_failure(reason)
            return 0        
        success,reason=origin.can_withdraw_object(obj)
        if not success:
            game_engine().writer.announce_failure(reason)
            return False,0        
        #do the actual move
        origin.withdraw_object(obj)
        destination.deposit_object(obj)
        #make announcements
        game_engine().writer.announce_action("You take the "+obj.get_noun_phrase())        
        return 1
register_action("exploration",ActionTake())

class ActionDrop(Action):
    #drop (object)
    def __init__(self):
        super().__init__(action_word="drop",n_args=1,tag_requirements=[TagRequirements(required_tags=["carryable"])])
    
    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        obj=arguments[0]
        origin=obj.location
        destination=action_subject.location
        #first verify it is possible        
        success,reason=destination.can_deposit_object(obj)
        if not success:
            game_engine().writer.announce_failure(reason)
            return 0        
        success,reason=origin.can_withdraw_object(obj)
        if not success:
            game_engine().writer.announce_failure(reason)
            return False,0        
        #do the actual move
        origin.withdraw_object(obj)
        destination.deposit_object(obj)
        #make announcements
        game_engine().writer.announce_action("You drop the "+obj.get_noun_phrase())        
        return 1
register_action("exploration",ActionDrop())

class ActionOpen(Action):
    #open (door)
    def __init__(self):
        super().__init__(action_word="open",n_args=1,tag_requirements=[TagRequirements(required_tags=["openable"])])
    
    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        door=arguments[0]
        return door.open_action(action_subject)[1]
register_action("exploration",ActionOpen())

class ActionClose(Action):
    #close (door)
    def __init__(self):
        super().__init__(action_word="close",n_args=1,tag_requirements=[TagRequirements(required_tags=["closable"])])
    
    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        door=arguments[0]
        return door.close_action(action_subject)[1]
register_action("exploration",ActionClose())

class ActionDeposit(Action): #put something in a container
    #deposit (object) in (container)
    def __init__(self):
        super().__init__(action_word="deposit",n_args=2,tag_requirements=[TagRequirements(required_tags=["carryable"]),TagRequirements(required_tags=["container"])])
    
    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        obj=arguments[0]
        container=arguments[1]
        success,message=container.deposit_object(obj) #add the object to the container
        if success:
            game_engine().writer.announce_action("You put the "+obj.get_choice_word()+" in the "+container.get_choice_word())
            action_subject.inventory.remove(obj) #remove the object from the player's inventory
        else:
            game_engine().writer.announce_failure(message)
        return 1
register_action("exploration",ActionDeposit())

class ActionWithdraw(Action): #take something out of a container
    #withdraw (object) from (container)
    def __init__(self):
        super().__init__(action_word="withdraw",n_args=2,tag_requirements=[TagRequirements(required_tags=["carryable"]),TagRequirements(required_tags=["container"])])
    
    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        obj=arguments[0]
        container=arguments[1]
        success,message=container.withdraw_object(obj) #remove the object from the container
        if success:
            game_engine().writer.announce_action("You take the "+obj.get_choice_word()+" from the "+container.get_choice_word())
            action_subject.inventory.append(obj) #add the object to the player's inventory
        else:
            game_engine().writer.announce_failure(message)
        return 1
