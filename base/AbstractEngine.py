def comma_separate_list(items):
    if len(items)==0:
        return ""
    elif len(items)==1:
        return items[0]
    elif len(items)==2:
        return items[0]+" and "+items[1]
    else:
        return ", ".join(items[:-1])+", and "+items[-1]
    
def add_a(word):
    if word[0] in "aeiou":
        return "an "+word
    else:
        return "a "+word


#this class stores the state of the game - in particular actions that have happened since the last report
#it is used to update the display
class AbstractEngine:
    def __init__(self):
        self.reset_game_state_text()
    
    def reset_game_state_text(self):
        self.room_text=""
        self.status_text=""
        self.items_text=""
        self.event_text=""
        self.image_name=""
        self.exit_info=[]

    def announce_action(self,text): #these go into events        
        self.event_text+=text+"<br>"

    def announce_failure(self,text): #these go into events
        self.event_text+="<strong>"+text+"</strong>"+"<br>"

    def set_room_description(self,text):
        self.room_text=text 

    def add_exit_info(self,text):
        print("adding exit info",text)
        self.exit_info.append(text)

    def set_image(self,image_name):
        self.image_name=image_name

    def add_to_floor(self,text):
        self.items_text+=text+"<br>"

    def get_message_object(self): #will be turned into json
        room_text=self.room_text
        for exit_info in self.exit_info:
            room_text+="<br>"+exit_info
        ret= {"room_text":room_text,
                "status_text":self.status_text,
                "items_text":self.items_text,
                "event_text":self.event_text,
                "image_name":self.image_name}
        return ret
                

def set_game_engine(engine:AbstractEngine):
    global _game_engine
    _game_engine=engine

def game_engine() -> AbstractEngine:
    global _game_engine
    return _game_engine