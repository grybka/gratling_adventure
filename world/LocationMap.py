import pygame
from world.GameObject import *

class LocationMap:
    def __init__(self):
        side_size=4
        self.rooms=[]
        for i in range(side_size):
            self.rooms.append([])
            for j in range(side_size):
                self.rooms[i].append(GameLocation("Room {},{}".format(i,j)))
        for i in range(side_size):
            for j in range(side_size):
                if i+1<side_size:
                    self.rooms[i][j].exits.append(GameExit(destination=self.rooms[i+1][j],choice_word="path east"))
                    self.rooms[i+1][j].exits.append(GameExit(destination=self.rooms[i][j],choice_word="path west"))
                if j+1<side_size:
                    self.rooms[i][j].exits.append(GameExit(destination=self.rooms[i][j+1],choice_word="path south"))
                    self.rooms[i][j+1].exits.append(GameExit(destination=self.rooms[i][j],choice_word="path north"))
        #
        self.room_width=100
        self.room_height=30
        self.my_font=pygame.font.Font(None,20)

    def get_map_image(self,location):
        width=512
        height=512
        room_spacing=10
        my_surface=pygame.surface.Surface((width,height))
        my_surface.fill((255,255,255))
        for i in range(len(self.rooms)):
            for j in range(len(self.rooms[i])):
                pygame.draw.rect(my_surface,(0,0,0),pygame.Rect(i*(self.room_width+room_spacing),j*(self.room_height+room_spacing),self.room_width,self.room_height),1) 
                room_text=self.my_font.render(self.rooms[i][j].short_description,True,(0,0,0))
                center=(i*(self.room_width+room_spacing)+self.room_width/2,j*(self.room_height+room_spacing)+self.room_height/2)
                rect = room_text.get_rect(center=center)
                my_surface.blit(room_text,rect)
        return my_surface
    
    def get_map_image_location(self,location):
        room_spacing=10
        for i in range(len(self.rooms)):
            for j in range(len(self.rooms[i])):
                if self.rooms[i][j]==location:
                    return (i*(self.room_width+room_spacing)+self.room_width/2,j*(self.room_height+room_spacing)+self.room_height/2)
        return (0,0)

