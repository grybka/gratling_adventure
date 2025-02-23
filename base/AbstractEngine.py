
class AbstractEngine:
    def __init__(self):
        pass

    def choice_made(self,choice):
        pass

    #functions that get called by objects to change the world
    def move_player(self,exit):
        pass

    #functions that get called to output to user
    def announce_action(self,text):
        pass
    
    def post_text(self,text):
        pass

def set_game_engine(engine):
    global _game_engine
    _game_engine=engine

def game_engine():
    global _game_engine
    return _game_engine