
class AbstractDisplay:
    def __init__(self):
        ...

    def update_text(self,text):
        ...

    def update_choices(self,choices):
        ...

    def update_image(self,image):
        ...

    def update_status(self,status):
        ...

    def update_map(self,map):
        ...

    def update_map_position(self,position): #position is an x,y tuple in pixels on the map image
        ...

    def get_waiting_choices(self):
        return None