import pygame
import sys


class Visual:
    def __init__(self):
        pygame.init()
        self.width = 736 #largura
        self.height = 414 #altura
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in")

        self.loop = True
    def load_images(self):
        back = pygame.image.load('visual/galaxy.bg.jpeg')
        while self.loop:
            for events in pygame.event.get():
                if events.type == pygame.QUIT:
                    self.loop = False
            
            self.screen.blit(back, (0,0))
            
            pygame.display.update()
        pygame.quit()

    def draw_background(self):
        pass

    def draw_connections(self):
        pass

    def draw_hubs(self):
        pass

    def draw_drones(self):
        pass

    def update(self):
        pass