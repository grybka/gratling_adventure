import pygame
import pygame_gui
from pygame_gui.elements.ui_text_box import UITextBox




#Responses to clicking on a link
# - expand a section of the text (which may have its own links)
# - open a new window with options

#Can I make it hierarchical? could a sublink open up another section?  Let's say maybe.

class UltraTextLink:
    def __init__(self, text, target):
        self.text=text
        self.target=target

class UltraText:
    def __init__(self):
        self.block_name=""
        self.text_blocks=[] #each can be a string, a link, or another UltraText
        self.visible=False

    def add_block(self,obj):
        self.text_blocks.append(obj)

    def make_visible(self, block_name):
        if self.block_name==block_name:
            self.visible=True
        for block in self.text_blocks:
            if isinstance(block, UltraText):
                block.make_visible(block_name)

    def toggle_visibility(self,block_name):
        if self.block_name==block_name:
            self.visible=not self.visible
        for block in self.text_blocks:
            if isinstance(block, UltraText):
                block.toggle_visibility(block_name)

    def to_html(self):
        if self.visible:
            html_text=""
            for block in self.text_blocks:
                if isinstance(block, UltraText):
                    html_text+=block.to_html()
                elif isinstance(block, UltraTextLink):
                    html_text+="<a href='"+block.target+"'>"+block.text+"</a>"
                else:
                    html_text+=block
            return html_text
        else:
            return ""
        
my_text=UltraText()
my_text.block_name="start"
my_text.add_block("This is the start of the text.\n ")
my_text.add_block(UltraTextLink("Click here to see more\n", "more"))
sub_block=UltraText()
sub_block.block_name="more"
sub_block.add_block("----This is the subblock. \n ")
my_text.add_block(sub_block)
my_text.add_block("This is the end of the text. \n")
my_text.visible=True



pygame.init()

pygame.display.set_caption('Gratling Adventure')

window_size=(1200, 800)

window_surface = pygame.display.set_mode(window_size)

background = pygame.Surface(window_size)

background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager(window_size, 'theme.json')

test_text="here is some text with a <a href='https://www.google.com'>link</a> in it"

textbox = UITextBox(relative_rect=window_surface.get_rect(), manager=manager, html_text=my_text.to_html()) 





is_running=True
while is_running:
    time_delta = pygame.time.Clock().tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
          my_text.toggle_visibility(event.link_target)
          textbox.clear()
          textbox.append_html_text(my_text.to_html())
          print(event.link_target)
        manager.process_events(event)
    
    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()