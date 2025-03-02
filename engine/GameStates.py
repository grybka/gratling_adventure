"""DEFUNCT
from engine.Engine import GameEngine
from base.AbstractEngine import set_game_engine
from world.generation.MapGenerator import MapGenerator1


class GameState:
    def __init__(self):
        ...

    def update(self): #Returns True if state should continue, next state
        return False, None

class GameStateManager:
    def __init__(self):
        self.current_state=None

    def update(self,time_delta):
        if self.current_state is not None:
            cont,next=self.current_state.update()
            if not cont:
                self.current_state=next

class PlayGameState(GameState):
    def __init__(self,display):
        self.is_running=True
        self.map_generator=MapGenerator1()
        self.map_generator.generate_map()
        self.engine=GameEngine(display,self.map_generator.my_map)
        set_game_engine(self.engine)
        self.display=display

    def update(self):
        self.engine.update()
        if not self.is_running:
            return False, None
        return True, self
"""