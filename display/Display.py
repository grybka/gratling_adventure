from pygame import *
import pygame_gui
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements.ui_panel import UIPanel
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_image import UIImage
from base.AbstractDisplay import AbstractDisplay
from pygame_gui.core import ObjectID
import yaml
import os

#a multirow array of text buttons
class ButtonArray(UIContainer):
#class ButtonArray(UIPanel):
    def __init__(self,rect,manager,container=None,anchors=None,button_labels=[],bad_button_labels=[]):
        self.padding=5
        self.button_height=30
        self.ui_manager=manager
        super().__init__(relative_rect=rect,container=container,manager=manager,anchors=anchors)
        #self.button_labels=["a 1","bb 2","ccc 3","dddd 4","eeeee 5","Button 6","Button 7","Button 8","Button 9","Button 10"]
        self.button_labels=button_labels
        self.bad_button_labels=bad_button_labels
        self.buttons=[]
        self._rebuild_buttons()

    #def rebuild_buttons(self,button_labels):
    #    for button in self.buttons:
    #        button.kill()
    ##    self.buttons=[]
    #    self.button_labels=button_labels
    #    self._rebuild_buttons()

    def _rebuild_buttons(self):
        row_start=self.padding
        last_x=0
        last_button=None
        for label in self.button_labels:
            new_button=UIButton(relative_rect=Rect((self.padding+last_x,row_start+self.padding),(-1,self.button_height)),text=label,manager=self.ui_manager,container=self,anchors={"left":"left"},object_id="#word_button")
            last_x=new_button.get_relative_rect()[0]+new_button.get_relative_rect()[2]
            self.buttons.append(new_button)
            last_button=new_button            
            if last_button.get_relative_rect().right>self.rect.width-self.padding:
                row_start+=self.button_height+self.padding
                last_x=0
                last_button.set_relative_position((self.padding,row_start+self.padding))
                last_x=last_button.get_relative_rect()[0]+last_button.get_relative_rect()[2]
        for label in self.bad_button_labels:
            new_button=UIButton(relative_rect=Rect((self.padding+last_x,row_start+self.padding),(-1,self.button_height)),text=label,manager=self.ui_manager,container=self,anchors={"left":"left"},object_id="#bad_word_button")            
            last_x=new_button.get_relative_rect()[0]+new_button.get_relative_rect()[2]
            self.buttons.append(new_button)
            last_button=new_button            
            if last_button.get_relative_rect().right>self.rect.width-self.padding:
                row_start+=self.button_height+self.padding
                last_x=0
                last_button.set_relative_position((self.padding,row_start+self.padding))
                last_x=last_button.get_relative_rect()[0]+last_button.get_relative_rect()[2]

        ...

    def get_pressed_button_text(self,element):
        for button in self.buttons:
            if button == element:
                return button.text
        return None

class InputPanel(UIPanel):
    def __init__(self,relative_rect,manager=None,container=None,anchors=None):
        self.ui_manager=manager
        super().__init__(relative_rect=relative_rect,manager=manager,container=container,anchors=anchors)
        self.words_part=None
        self.button_part=None
        self.padding=10
        self.update_info("Words here",["Button 1","Button 2","Button 3","Button 4","Button 5","Button 6","Button 7","Button 8","Button 9"])
        back_button_width=100
        self.back_button=UIButton(relative_rect=Rect((self.get_relative_rect().width-back_button_width-2*self.padding,self.padding),(back_button_width,40)),text="Back",manager=self.ui_manager,container=self,anchors={"top":"top","left":"left"})
        
    def update_info(self,words,button_labels,bad_button_labels=[]):
        rect=self.get_relative_rect()
        if self.words_part is not None:
            self.words_part.kill()
        if self.button_part is not None:
            self.button_part.kill()
        self.words_part=UILabel(relative_rect=Rect((self.padding,self.padding),(-1,-1)),text=words,manager=self.ui_manager,container=self,anchors={"top":"top","left":"left"})
        button_part_xstart=self.padding*2+self.words_part.rect.width
        back_button_width=100
        button_part_width=rect.width-button_part_xstart-back_button_width-2*self.padding

        self.button_part=ButtonArray(Rect((button_part_xstart,self.padding),(button_part_width,rect.height)),container=self,manager=self.ui_manager,anchors={"top":"top","left":"left"},button_labels=button_labels,bad_button_labels=bad_button_labels)

    def process_event(self,event):
        return False
        if event.type==pygame_gui.UI_BUTTON_PRESSED:
            if self.back_button == event.ui_element:
                print("Back button pressed")
                return True
            array_button_pressed=self.button_part.get_pressed_button_text(event.ui_element)
            if array_button_pressed is not None:
                print("Button pressed:",array_button_pressed)
                return True
        return super().process_event(event)

def string_list_matches_so_far(choice,words_picked):
    if len(choice)<len(words_picked):
        return False
    for i in range(len(words_picked)):
        if words_picked[i]!=choice[i]:
            return False
    return True

class MapImage(UIImage):
    def __init__(self,relative_rect,manager=None,container=None,anchors=None):
        self.map_image_dims=(relative_rect.width,relative_rect.height)
        self.submap_image=surface.Surface(self.map_image_dims)
        super().__init__(image_surface=self.submap_image,relative_rect=relative_rect,manager=manager,container=container,anchors=anchors)
        self.map_image=None
        self.map_position=(0,0)
        self.target_map_position=None
        self.scroll_speed=4
        
        
        self.map_dirty=True #need to redraw

    def update_map_image(self,map_image):
        self.map_image=map_image
        self.map_dirty=True        

    def update_map_position(self,position): #position is an x,y tuple in pixels on the map image
        if self.target_map_position is None:
            self.map_position=position
        self.target_map_position=position    
        self.map_dirty=True

    def update_map_display(self): 
        if self.map_image is None:
            return   
        blit_pos=(-self.map_position[0]+self.submap_image.width//2,-self.map_position[1]+self.submap_image.height//2)
        self.submap_image.fill((255,255,255))
        self.submap_image.blit(self.map_image,blit_pos)
        self.set_image(self.submap_image)      

    def update(self,time_delta: float):
        if self.target_map_position is not None and self.map_position!=self.target_map_position:
            dx=self.target_map_position[0]-self.map_position[0]
            dy=self.target_map_position[1]-self.map_position[1]
            dist=(dx**2+dy**2)**0.5
            if dist<=self.scroll_speed:
                self.map_position=self.target_map_position
            else:
                self.map_position=(self.map_position[0]+dx/dist*self.scroll_speed,self.map_position[1]+dy/dist*self.scroll_speed)
            self.map_dirty=True
        if self.map_dirty:
            self.update_map_display()
            self.map_dirty=False
        super().update(time_delta)

class ImagePanel(UIPanel):
    def __init__(self,relative_rect,manager=None,container=None,anchors=None):
        super().__init__(relative_rect=relative_rect,manager=manager,container=container,anchors=anchors)
        self.image_dims=(relative_rect.width,relative_rect.height)
        self.image_surface=surface.Surface(self.image_dims)
        self.image_shown=UIImage(relative_rect=Rect((0,0),(relative_rect.width,relative_rect.height)),manager=manager,container=self,image_surface=self.image_surface)               
        with open("images/images.yaml","r") as f:
            self.image_info=yaml.load(f,Loader=yaml.FullLoader)
        self.base_path=self.image_info["base_path"]
        self.loaded_images={}

    def show_image(self,image_name):
        if image_name not in self.image_info["images"]:
            print("Image {} not found".format(image_name))
            return
        if image_name not in self.loaded_images:
            print(image.get_extended())
            target_file=os.path.join(self.base_path,self.image_info["images"][image_name]["file"])
            #print("loading image "+target_file)
            if os.path.exists(target_file):
                self.loaded_images[image_name]=image.load(target_file)
            else:
                print("Image file {} not found".format(target_file))
                return
        image_size=self.loaded_images[image_name].get_size()
        target_size=self.image_surface.get_size()
        self.image_surface.fill((255,255,255))
        if target_size[0]/image_size[0]<target_size[1]/image_size[1]:
            scaled_surface=transform.scale(self.loaded_images[image_name],(int(target_size[0]),int(image_size[1]*target_size[0]/image_size[0])))
            y_pos=(target_size[1]-scaled_surface.get_size()[1])//2
            self.image_surface.blit(scaled_surface,(0,y_pos))

        else:
            scaled_surface=transform.scale(self.loaded_images[image_name],(int(image_size[0]*target_size[1]/image_size[1]),int(target_size[1])))
            x_pos=(target_size[0]-scaled_surface.get_size()[0])//2
            self.image_surface.blit(scaled_surface,(x_pos,0))

            

        #scaled_surface=transform.scale(self.loaded_images[image_name],self.image_surface.get_size())
        
        self.image_shown.set_image(self.image_surface)
        #self.set_image(self.image_surface)
        


    


class DisplayInterface(UIPanel,AbstractDisplay):
    def __init__(self, screen, manager):
        super().__init__(relative_rect=Rect((0, 0), (screen.width, screen.height)), manager=manager)
        padding=10
        sub_padding=4
        col_width=(screen.width-4*padding)/3
        height_1=(screen.height-4*padding)*0.4
        height_2=(screen.height-4*padding)*0.4
        height_3=(screen.height-4*padding)*0.2

        #image space
        #self.image_panel = UIPanel(relative_rect=Rect((padding, padding), (col_width, height_1)), manager=manager, container=self)
        self.image_panel = ImagePanel(relative_rect=Rect((padding, padding), (col_width, height_1)), manager=manager, container=self)
        #status space
        self.status_panel = UITextBox(relative_rect=Rect((padding, padding), (col_width, height_1)), manager=manager, html_text="", container=self,anchors={"left_target": self.image_panel}) 
        #self.map_image_dims=(self.status_panel.rect.width,self.status_panel.rect.height)
        #self.map_position=(0,0)
        #self.submap_image=surface.Surface(self.map_image_dims)
        #self.map_image_element=UIImage(relative_rect=Rect((0, 0), self.map_image_dims), image_surface=self.submap_image, manager=self.ui_manager, container=self.status_panel)               
        self.map_panel = UIPanel(relative_rect=Rect((padding, padding), (col_width, height_1)), manager=manager, container=self,anchors={"left_target": self.status_panel}) 

        self.map_image_element=MapImage(relative_rect=Rect((sub_padding, sub_padding), (self.status_panel.rect.width-2*sub_padding,self.status_panel.rect.height-2*sub_padding)), manager=self.ui_manager, container=self.map_panel)
        #description space
        self.description_panel = UITextBox(relative_rect=Rect((padding, padding), (screen.width-2*padding, height_2)), manager=manager,html_text="", container=self,anchors={"top_target": self.image_panel})

        #input space
        self.input_panel = InputPanel(relative_rect=Rect((padding, padding), (screen.width-2*padding, height_3)), manager=manager, container=self, anchors={"top_target": self.description_panel})
        self.choices=[] #choices that will be possible
        self.bad_choices=[] #choices that will be impossible but you might want to know why
        self.words_picked=[]
        self.choice_to_engine=None


    def update_text(self,text):
        self.description_panel.append_html_text(text)
        if self.description_panel.scroll_bar is not None:
            self.description_panel.scroll_bar.set_scroll_from_start_percentage(1.0)

    def update_choices(self,choices,bad_choices=[]):
        #reset choices and words picked
        self.input_panel.back_button.hide()
        self.words_picked=[]
        self.choices=choices
        self.bad_choices=bad_choices
        self.update_words()

    def update_image(self,image):
        self.image_panel.show_image(image)        

    def update_status(self,status):
        my_text="Turn: "+str(status["turn_number"])+"\n"
        my_text+="Inventory:\n"
        for item in  status["inventory"]:
            my_text+=item+"\n"
        self.status_panel.clear()     
        self.status_panel.append_html_text(my_text )
        #print("status panel is ",str(status))
        ...

    def update_map(self,map_image):
        self.map_image_element.update_map_image(map_image)
        #self.map_image=map_image
        #self.update_map_display()                        

    def update_map_position(self,position): #position is an x,y tuple in pixels on the map image
        self.map_image_element.update_map_position(position)
        #self.map_position=position
        #self.update_map_display()

    def update_map_display(self):
        print("self.map_position",self.map_position)  
        blit_pos=(-self.map_position[0]+self.submap_image.width//2,-self.map_position[1]+self.submap_image.height//2)
        self.submap_image.fill((0,0,0))
        #self.map_image.blit(self.submap_image,blit_pos)                     
        self.submap_image.blit(self.map_image,blit_pos)
#        sub_image=self.map_image.subsurface(Rect(self.map_position,self.map_image_dims))
        self.map_image_element.set_image(self.submap_image)
        #self.map_image_element.set_image(self.map_image)

    def get_remaining_choices(self):
        #print("words picked ",self.words_picked)
        #print("choices ",self.choices)
        #print("bad choices ",self.bad_choices)
        remaining_choices=[]
        for choice in self.choices:
            if string_list_matches_so_far(choice,self.words_picked):
                remaining_choices.append(choice)
        remaining_bad_choices=[]
        for choice in self.bad_choices:
            if string_list_matches_so_far(choice,self.words_picked):
                remaining_bad_choices.append(choice)
        #print("returning ",remaining_choices," and ",remaining_bad_choices)
        return remaining_choices,remaining_bad_choices

    def word_picked(self,word_chosen):
        self.input_panel.back_button.show()
        self.words_picked.append(word_chosen)
        remaining_choices,remaining_bad_choices=self.get_remaining_choices()       
        all_choices=remaining_choices+remaining_bad_choices         
        #print("remaining choices",remaining_choices," and ",remaining_bad_choices)
        #print("len remaining choices")
        #if we've selected a choice,  we're done
        if len(all_choices[0])==len(self.words_picked):
            #print("Action chosen",self.words_picked)
            self.choice_to_engine=self.words_picked
            self.update_choices([])
        self.update_words()


    def update_words(self):
        word_choices,word_bad_choices=self.get_remaining_choices()        

        #find all choices for which the words are the same sa words_picked        
        first_words=set()
        for choice in word_choices:
            first_words.add(choice[len(self.words_picked)])
        first_words_bad=set()
        for choice in word_bad_choices:
            first_words_bad.add(choice[len(self.words_picked)])
        first_words_bad=first_words_bad-first_words

        #print("first words",first_words)
        picked_words=str.join(" ",self.words_picked)
        self.input_panel.update_info(picked_words,list(first_words),list(first_words_bad))


        
    def process_event(self,event):
        #uhg, lets just do all the processing here
        if event.type==pygame_gui.UI_BUTTON_PRESSED:
            if self.input_panel.back_button == event.ui_element:
                if len(self.words_picked)>0:
                    self.words_picked.pop()
                    self.update_words()
#                print("Back button pressed")
                return True
            array_button_pressed=self.input_panel.button_part.get_pressed_button_text(event.ui_element)
            if array_button_pressed is not None:
                self.word_picked(array_button_pressed)
                return True
        return super().process_event(event)

    def get_waiting_choices(self):
        if self.choice_to_engine is not None:
            ret=self.choice_to_engine
            self.choice_to_engine=None
            return ret
        return None
