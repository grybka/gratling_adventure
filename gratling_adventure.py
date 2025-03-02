from flask import Flask, render_template, request, jsonify
import random
from world.generation.MapGenerator import MapGenerator1
from engine.Engine import GameEngine
from base.AbstractEngine import set_game_engine,game_engine
import sys
import pygame

app=Flask(__name__)

#this binds a URL to a function
@app.route('/')
def sessions():
    return render_template('game_screen.html')

@app.route('/action', methods=['POST'])
def action():
    print('action was received!!!')
    print(request.data)
    data = request.get_json()
    print("data was {}".format(data))
    engine=game_engine()    
    return jsonify(engine.get_message_object())

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

if __name__ == '__main__':
    n = len(sys.argv)
    if n == 2:
        #use random seed
        random.seed(sys.argv[1])
    #it's probably silly to use all of pygame just to draw the map
    pygame.init()

    #Tuck this away somewhere else eventually.  I'd have a state manager, but I think I can do that with flask routes
    map_generator=MapGenerator1()
    map_generator.generate_map()
    engine=GameEngine(map_generator.my_map)
    set_game_engine(engine)
    engine.player_turn_start()

    app.run()
    



"""
from display.Display import DisplayInterface
import pygame
import pygame_gui
from engine.GameStates import GameState, GameStateManager, PlayGameState
import sys
import random

n = len(sys.argv)
if n == 2:
    #use random seed
    random.seed(sys.argv[1])

pygame.init()

pygame.display.set_caption('Gratling Adventure')

window_size=(1200, 800)

window_surface = pygame.display.set_mode(window_size)

background = pygame.Surface(window_size)

background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager(window_size, 'theme.json')

clock = pygame.time.Clock()

display=DisplayInterface(window_surface,manager)

gamestatemanager=GameStateManager()
gamestatemanager.current_state=PlayGameState(display)

is_running=True
while is_running:
    time_delta = pygame.time.Clock().tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        manager.process_events(event)

    gamestatemanager.update(time_delta)
    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()
"""