from world.GameObject import *


class CharacterStats:
    def __init__(self):
        self.strength=10
        self.dexterity=10
        self.charisma=10
        self.max_strength=10
        self.max_dexterity=10
        self.max_charisma=10
        self.health=6
        self.max_health=6

    def get_stat_string(self):
        return "Health: "+str(self.health)+"/"+str(self.max_health)+\
               " Str: "+str(self.strength)+"/"+str(self.max_strength)+\
               " Dex: "+str(self.dexterity)+"/"+str(self.max_dexterity)+\
               " Cha: "+str(self.charisma)+"/"+str(self.max_charisma)               
        
    
#characters can move around and carry things
#they have stats and health and such
#let's try something inspired by ItO or Cairn
class Character(ContainerInterface,GameObject):
    def __init__(self,base_noun="creature"):
        super().__init__(base_noun=base_noun)
        self.description="It's a creature"
        self.known_locations=set() #given as map positions
        #stats        
        self.stats=CharacterStats()

    def set_location(self,location):
        super().set_location(location)
        self.known_locations.append(location.map_position)    