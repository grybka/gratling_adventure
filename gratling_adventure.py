from display.Display import DisplayInterface
import pygame
import pygame_gui
from engine.GameStates import GameState, GameStateManager, PlayGameState

pygame.init()


pygame.display.set_caption('Gratling Adventure')
window_surface = pygame.display.set_mode((800, 600))


background = pygame.Surface((800, 600))

background.fill(pygame.Color('#000000'))

manager = pygame_gui.UIManager((800, 600))

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