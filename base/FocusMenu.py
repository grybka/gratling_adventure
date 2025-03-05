from base.TaggedObject import TaggedObject
from base.Action import ActionDict

class FocusMenuInfo:
    def __init__(self):
        self.actions=ActionDict()
        self.html=""
        self.image=""
        self.options=[]        

    def add_text_and_action( self,text_action_tuple ):
        text=text_action_tuple[0]
        action=text_action_tuple[1]
        self.html+=text+"<br>"
        self.actions.add_action_dict(action)

class FocusMenu:
    def __init__(self):
        ...

    #The player's focus is on one menu.
    #This generates the menu html and the associated actiondict
    def get_focus_html_and_actions(self, subject:TaggedObject, available_objects:list[TaggedObject]) -> FocusMenuInfo:
        return "focus menu text missing",ActionDict()