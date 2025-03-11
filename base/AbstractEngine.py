import io
import pygame

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
        self.events=[]
        self.image_name=""
        self.exit_info=[]
        self.sub_menus={}
        self.room_features=[]
        self.map_image=None #pygame surface

    def announce_action(self,text): #these go into events        
        self.events.append(text)        

    def announce_failure(self,text): #these go into events
        self.events.append("<strong>"+text+"</strong>")

    def set_room_description(self,text):
        self.room_text=text     

    #def add_exit_info(self,text):
    #    self.exit_info.append(text)

    def set_image(self,image_name):
        self.image_name=image_name

    def add_to_floor(self,text):
        self.items_text+=text+"<br>"

    def add_sub_menu(self,id,menu):
        self.sub_menus[id]=menu

    def get_message_object(self): #will be turned into json
        room_text=self.room_text
        #for exit_info in self.exit_info:
        #    room_text+="<br>"+exit_info
        ret= {"room_text":room_text,
                "status_text":self.status_text,
                "items_text":self.items_text,
                "events":self.events,
                "image_name":self.image_name,
                "menu_info":self.sub_menus,
                "room_features":self.room_features}
        return ret
    
    def get_map_image(self) -> io.BytesIO:
        test_surf=pygame.Surface((256,256))
        test_surf.fill((255,0,0))
        self.map_image=test_surf
        buf = io.BytesIO()
        pygame.image.save(self.map_image, buf)
        buf.seek(0)
        return buf
                

def set_game_engine(engine:AbstractEngine):
    global _game_engine
    _game_engine=engine

def game_engine() -> AbstractEngine:
    global _game_engine
    return _game_engine

#helpers to make html
def submenu_link(menu_id,text):
    return "<a href='javascript:ExpandActionMenu(\""+menu_id.__str__()+"\")'>"+text+"</a>"
