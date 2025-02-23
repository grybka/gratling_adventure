from pygame import *
import pygame_gui
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.elements.ui_panel import UIPanel
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.elements.ui_button import UIButton
from base.AbstractDisplay import AbstractDisplay

#a multirow array of text buttons
class ButtonArray(UIContainer):
#class ButtonArray(UIPanel):
    def __init__(self,rect,manager,container=None,anchors=None,button_labels=[]):
        self.padding=5
        self.button_height=30
        self.ui_manager=manager
        super().__init__(relative_rect=rect,container=container,manager=manager,anchors=anchors)
        #self.button_labels=["a 1","bb 2","ccc 3","dddd 4","eeeee 5","Button 6","Button 7","Button 8","Button 9","Button 10"]
        self.button_labels=button_labels
        self.buttons=[]
        self._rebuild_buttons()

    def rebuild_buttons(self,button_labels):
        for button in self.buttons:
            button.kill()
        self.buttons=[]
        self.button_labels=button_labels
        self._rebuild_buttons()

    def _rebuild_buttons(self):
        row_start=self.padding
        last_x=0
        last_button=None
        for label in self.button_labels:
            new_button=UIButton(relative_rect=Rect((self.padding+last_x,row_start+self.padding),(-1,self.button_height)),text=label,manager=self.ui_manager,container=self,anchors={"left":"left"})
            last_x=new_button.get_relative_rect()[0]+new_button.get_relative_rect()[2]
            self.buttons.append(new_button)
            last_button=new_button
            #print("last button rect=",last_button.get_relative_rect())
            #print("last button rect=",last_button.get_relative_rect().right)

            #print("self.width=",self.rect.width)

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
        
    def update_info(self,words,button_labels):
        rect=self.get_relative_rect()
        if self.words_part is not None:
            self.words_part.kill()
        if self.button_part is not None:
            self.button_part.kill()
        self.words_part=UILabel(relative_rect=Rect((self.padding,self.padding),(-1,-1)),text=words,manager=self.ui_manager,container=self,anchors={"top":"top","left":"left"})
        button_part_xstart=self.padding*2+self.words_part.rect.width
        back_button_width=100
        button_part_width=rect.width-button_part_xstart-back_button_width-2*self.padding

        self.button_part=ButtonArray(Rect((button_part_xstart,self.padding),(button_part_width,rect.height)),container=self,manager=self.ui_manager,anchors={"top":"top","left":"left"},button_labels=button_labels)

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

class DisplayInterface(UIPanel,AbstractDisplay):
    def __init__(self, screen, manager):
        super().__init__(relative_rect=Rect((0, 0), (screen.width, screen.height)), manager=manager)
        padding=10
        col_width=(screen.width-3*padding)/2
        height_1=(screen.height-4*padding)*0.4
        height_2=(screen.height-4*padding)*0.4
        height_3=(screen.height-4*padding)*0.2

        #image space
        self.image_panel = UIPanel(relative_rect=Rect((padding, padding), (col_width, height_1)), manager=manager, container=self)
        #status space
        self.status_panel = UIPanel(relative_rect=Rect((padding, padding), (col_width, height_1)), manager=manager, container=self,anchors={"left_target": self.image_panel})
        #description space
        self.description_panel = UITextBox(relative_rect=Rect((padding, padding), (screen.width-2*padding, height_2)), manager=manager,html_text="", container=self,anchors={"top_target": self.image_panel})

        #input space
        self.input_panel = InputPanel(relative_rect=Rect((padding, padding), (screen.width-2*padding, height_3)), manager=manager, container=self, anchors={"top_target": self.description_panel})
        self.choices=[]
        self.words_picked=[]
        self.choice_to_engine=None


    def update_text(self,text):
        self.description_panel.append_html_text(text)
        if self.description_panel.scroll_bar is not None:
            self.description_panel.scroll_bar.set_scroll_from_start_percentage(1.0)

    def update_choices(self,choices):
        #reset choices and words picked
        self.words_picked=[]
        self.choices=choices
        self.update_words()

    def update_image(self,image):
        ...

    def update_status(self,status):
        ...

    def update_map(self,map):
        ...

    def get_remaining_choices(self):
        remaining_choices=[]
        for choice in self.choices:
            if string_list_matches_so_far(choice,self.words_picked):
                remaining_choices.append(choice)
        return remaining_choices

    def word_picked(self,word_chosen):
        self.words_picked.append(word_chosen)
        remaining_choices=self.get_remaining_choices()
        #if we're done, we're done
        if len(remaining_choices)==1:
            if len(remaining_choices[0])==len(self.words_picked):
                #print("Action chosen",self.words_picked)
                self.choice_to_engine=self.words_picked
                self.update_choices([])
        self.update_words()


    def update_words(self):
        #find all choices for which the words are the same sa words_picked
        first_words=set()
        for choice in self.get_remaining_choices():
            first_words.add(choice[len(self.words_picked)])
        #print("first words",first_words)
        picked_words=str.join(" ",self.words_picked)
        self.input_panel.update_info(picked_words,list(first_words))


        
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
