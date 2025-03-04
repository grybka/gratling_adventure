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