import pygame
import colorsys
import random
import math


class Visual:
    def __init__(self, hubs, start_hub, end_hub, drones):
        pygame.init()
        self.width = 1000 #largura
        self.height = 600 #altura
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in")

        self.start_hub = start_hub
        self.end_hub = end_hub
        self.hubs = hubs
        self.loop = True
        self.drone_list = drones
        self.stars = []
        self.hue = 0

        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            phase = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            self.stars.append([x, y, phase, speed])

    def load_images(self):
        back = pygame.image.load('visual/galaxybg.jpeg')
        back = pygame.transform.scale(back, (self.width, self.height))

        while self.loop:
            for events in pygame.event.get():
                if events.type == pygame.QUIT:
                    self.loop = False

            self.screen.blit(back, (0, 0))
            self.draw_hubs()
            self.draw_stars()
            self.draw_drones()

            pygame.display.update()

        pygame.quit()

    def draw_connections(self):
        pass
    def draw_stars(self):
        for star in self.stars:
            x, y, phase, speed = star

            brightness = (math.sin(phase) + 1) / 2

            size = 1 if brightness < 0.7 else 2

            pygame.draw.circle(
                self.screen,
                (255, 255, 255),
                (x, y),
                size
            )
            star[2] += 0.10 * speed
    
    def draw_hubs(self):
        planet_original = pygame.image.load(
            'visual/planetfinal.png'
        ).convert_alpha()

        planet_original = pygame.transform.scale(
            planet_original,
            (90, 60)
        )

        start_end = pygame.image.load(
            'visual/start_endbg.png'
        ).convert_alpha()

        start_end = pygame.transform.scale(
            start_end,
            (100, 70)
        )

        yellow = pygame.image.load(
            'visual/planetyellow.png'
        ).convert_alpha()

        yellow = pygame.transform.scale(
            yellow,
            (90, 60)
        )

        gray = pygame.image.load(
            'visual/planetgray.png'
        ).convert_alpha()

        gray = pygame.transform.scale(
            gray,
            (90, 60)
        )

        for hub in self.hubs:
            x = hub.x * 100
            y = hub.y * 100

            if hub == self.start_hub or hub == self.end_hub:
                offset_y = math.sin(
                    pygame.time.get_ticks() * 0.002
                ) * 2

                self.screen.blit(
                    start_end,
                    (x, y + offset_y)
                )

                continue

            # Começa SEMPRE com uma cópia limpa
            planet = planet_original.copy()

            if hub.color == "red":
                planet.fill(
                    (255, 0, 0),
                    special_flags=pygame.BLEND_RGBA_MULT
                )

            elif hub.color == "green":
                planet.fill(
                    (0, 255, 0),
                    special_flags=pygame.BLEND_RGBA_MULT
                )

            elif hub.color == "blue":
                planet.fill(
                    (0, 0, 255),
                    special_flags=pygame.BLEND_RGBA_MULT
                )

            elif hub.color == "pink":
                planet.fill(
                    (255, 20, 147),
                    special_flags=pygame.BLEND_RGBA_MULT
                )

            elif hub.color == "yellow":
                planet = yellow

            elif hub.color == "gray":
                planet = gray

            elif hub.color == "rainbow":
                rgb = colorsys.hsv_to_rgb(
                    self.hue,
                    1,
                    1
                )

                rainbow_color = tuple(
                    int(c * 255)
                    for c in rgb
                )

                planet.fill(
                    (*rainbow_color, 255),
                    special_flags=pygame.BLEND_RGBA_MULT
                )

            # None / sem cor → planet original
            self.screen.blit(
                planet,
                (x, y)
            )

        self.hue = (self.hue + 0.005) % 1
    def draw_drones(self):
        drone_img = pygame.image.load(
            'visual/drone.png'
        ).convert_alpha()
        drone_img = pygame.transform.scale(
            drone_img, (100, 70)
        )

        for drone in self.drone_list:
            x = drone.location.x * 100
            y = drone.location.y * 100
            self.screen.blit(drone_img, (x, y))
