
#Frame example
# wall_material = "stone"
# floor_material = "wood"
# room_shape = "square"
# room_size = "large"
# smell = "musty"
# temperature = "cold"
# sound = "silence"
# light = "dim"

import random
#generates a room frame

class RoomFrameGenerator:
    def __init__(self,obj):
        self.object = obj

    def generate(self):
        ret = {}
        for key in self.object.keys():
            #print("on key {}".format(key))
            #print("values are {}".format(self.object[key]))
            ret[key] = random.choice(self.object[key])
        return ret