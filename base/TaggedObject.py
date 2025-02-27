class TaggedObject:
    def __init__(self,choice_word="TaggeObject"):
        self.tags=set() #set of strings
        self.choice_word=choice_word #word that represents the object

    def add_tag(self,tag):
        self.tags.add(tag)

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