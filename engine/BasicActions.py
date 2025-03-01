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
        if success:
            game_engine().character_arrives(game_engine().player_object,exit.destination)
        return time
register_action("exploration",ActionGo())

class ActionTake(Action):
    #take (object) off the ground
    def __init__(self):
        super().__init__(action_word="take",n_args=1,tag_requirements=[TagRequirements(required_tags=["carryable"])])
    
    def is_action_possible(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        item=arguments[0]
        #I can only take objects in my room
        if action_subject.location != item.location:
            return False
        #I cannot take myself
        if action_subject==item:
            return False
        return True

    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        success=game_engine().transfer_object(arguments[0],action_subject)
        if success:
            game_engine().writer.announce_action("You take the "+arguments[0].get_noun_phrase())     
        return 1
register_action("exploration",ActionTake())

class ActionDrop(Action):
    #drop (object) on the ground
    def __init__(self):
        super().__init__(action_word="drop",n_args=1,tag_requirements=[TagRequirements(required_tags=["carryable"])])
    
    def is_action_possible(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        item=arguments[0]
        #I cannot drop things I do not have
        if item.location!=action_subject:
            return False
        return True


    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        success=game_engine().transfer_object(arguments[0],action_subject.location)
        if success:
            game_engine().writer.announce_action("You drop the "+arguments[0].get_noun_phrase())        
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
        super().__init__(action_word="deposit",n_args=2,tag_requirements=[TagRequirements(required_tags=["carryable"]),TagRequirements(required_tags=["container","accepts_deposit"])])
    
    
    def is_action_possible(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        item=arguments[0]
        container=arguments[1]
        #I cannot deposit things I do not have
        if item.location!=action_subject:
            return False
        return True


    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        obj=arguments[0]
        container=arguments[1]
        success=game_engine().transfer_object(arguments[0],arguments[1])
        if success:
            game_engine().writer.announce_action("You put the "+obj.get_choice_word()+" in the "+container.get_choice_word())
        return 1
register_action("exploration",ActionDeposit())

class ActionWithdraw(Action): #take something out of a container
    #withdraw (object) from (container)
    def __init__(self):
        super().__init__(action_word="withdraw",n_args=2,tag_requirements=[TagRequirements(required_tags=["carryable"]),TagRequirements(required_tags=["container","accepts_widthdraw"])])
    
    def is_action_possible(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        item=arguments[0]
        container=arguments[1]
        #I cannot withdraw things from where they are not
        if item.location!=container:
            return False
        return True
    
    def do_action(self,action_subject:TaggedObject,arguments:list[TaggedObject]):
        obj=arguments[0]
        container=arguments[1]
        success=game_engine().transfer_object(arguments[0],action_subject)
        if success:
            game_engine().writer.announce_action("You take the "+obj.get_choice_word()+" from the "+container.get_choice_word())
        return 1
register_action("exploration",ActionWithdraw())
