
class TaggedObject:
    def __init__(self,choice_word="unknown"):
        self.tags=set() #set of strings
        self.choice_word=choice_word

    def get_choice_word(self):
        return self.choice_word


class TagRequirements:
    def __init__(self,required_tags=[],forbidden_tags=[]):
        self.required_tags=required_tags #and 
        self.forbidden_tags=forbidden_tags #and
        self.or_requirements=None

    def matches(self,tags):
        if self.or_requirements is not None:
            if self.or_requirements.matches(tags):
                return True
        #check if the tags match the requirements
        #if there are any forbidden tags, return false
        for tag in self.forbidden_tags:
            if tag in tags:
                return False
        #if there are any required tags, return false
        for tag in self.required_tags:
            if tag not in tags:
                return False
        return True


class ActionTemplateSlot:
    #a slot is a single word or phrase that can be filled in
    #by the user or by the engine
    def __init__(self,object=None,required_tags=None,word=None):
        self.object=object
        self.required_tags=required_tags
        self.word=word
        #print("generated {}".format(self.__repr__()))

    def is_filled(self):
        return self.object is not None or self.word is not None
    
    def my_shallow_copy(self):
        ret=ActionTemplateSlot(object=self.object,required_tags=self.required_tags,word=self.word)
        return ret
        #return ActionTemplateSlot(object=self.object,required_tags=self.required_tags,word=self.word)
    
    def __repr__(self):
        if self.word is not None:
            return "Word("+self.word+")"
        if self.object is not None:
            return "Obj("+self.object.get_choice_word()+")"
        else:
            return "Req("+str(self.required_tags)+")"


class ActionTemplate:
    def __init__(self,slots=[],referring_object=None,referring_function=None):
        self.referring_object=referring_object #TODO Remove this
        self.referring_function=referring_function
        
        self.slots=[]
        for element in slots:
            if isinstance(element,str):
                self.slots.append(ActionTemplateSlot(word=element))
            elif not isinstance(element,TagRequirements):
                self.slots.append(ActionTemplateSlot(object=element))
            else:
                self.slots.append(ActionTemplateSlot(required_tags=element))

    def __repr__(self):
        return "ActionTemplate("+str(self.slots)+")"
    
    def my_shallow_copy(self):
        ret=ActionTemplate(referring_object=self.referring_object,referring_function=self.referring_function)
        for slot in self.slots:
            ret.slots.append(slot.my_shallow_copy())
        return ret

    def is_filled(self):
        #check if all the slots are filled
        for slot in self.slots:
            if not slot.is_filled():
                return False
        return True
    
    def to_word_choices(self):
        ret=[]
        for slot in self.slots:
            if slot.word is not None:
                ret.append(slot.word)
            elif slot.object is not None:
                ret.append(slot.object.get_choice_word())
            else:
                ret.append("?")
        return ret
    
    def matches_word_choices(self,word_choices):
        my_words=self.to_word_choices()
        if len(my_words)!=len(word_choices):
            return False
        #print("my words",my_words)
        #print("word choices",word_choices)
        for my_word,word_choice in zip(my_words,word_choices):
            if my_word!=word_choice:
                return False
        #print("match")
        return True

    def matches_filled_template(self,filled_template):
        #check if the filled template matches this template
        #by checking if the objects in the slots are the same
        for slot,filled_slot in zip(self.slots,filled_template.slots):
            if slot.object!=filled_slot.object:
                return False
        return True
    
    def get_filled_templates(self,objects):
        partial_fills=[ ActionTemplate(referring_object=self.referring_object,referring_function=self.referring_function) ]
        for slot in self.slots:
            next_partial_fills=[]
            if not slot.is_filled():
                for object in objects:
                    if slot.required_tags.matches(object.get_tags()):
                        for partial_fill in partial_fills:
                            new_partial_fill=partial_fill.my_shallow_copy()
                            new_partial_fill.slots.append(ActionTemplateSlot(object=object))
                            next_partial_fills.append(new_partial_fill)
            else:
                next_partial_fills=partial_fills
                for partial in next_partial_fills:
                    if slot.word is not None:
                        partial.slots.append(ActionTemplateSlot(word=slot.word))
                    else:
                        partial.slots.append(ActionTemplateSlot(object=slot.object))
            partial_fills=next_partial_fills
        return partial_fills
    
global _action_templates_by_category
_action_templates_by_category={}
def register_action_template(category:str, action_template:ActionTemplate):
    global _action_templates_by_category
    if category not in _action_templates_by_category:
        _action_templates_by_category[category]=[]
    _action_templates_by_category[category].append(action_template)

def get_action_templates(category:str):
    global _action_templates_by_category
    if category in _action_templates_by_category:
        return _action_templates_by_category[category]
    else:
        raise Exception("Action template category {} not found".format(category))