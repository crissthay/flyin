import colorsys
import math
import random

import pygame


COLOR_RGB = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "pink": (255, 20, 147),
    "black": (40, 40, 40),
    "magenta": (255, 0, 255),
    "orange": (255, 165, 0),
    "lime": (144, 238, 144)
}


class Visual:
    def __init__(
            self,
            hubs,
            start_hub,
            end_hub,
            drones,
            connections,
            simulation=None
            ):
        pygame.init()

        self.width = 1000
        self.height = 600

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in")
        self.clock = pygame.time.Clock()

        self.zoom = 100
        self.camera_x = 0
        self.camera_y = 0

        self.zoom_speed = 10
        self.camera_speed = 0.2

        self.start_hub = start_hub
        self.end_hub = end_hub
        self.hubs = hubs
        self.connections = connections
        self.simulation = simulation
        self.loop = True
        self.drone_list = drones
        self.stars = []
        self.hue = 0.0
        self.animation_turn = 0
        self.animation_progress = 0.0
        self.history = simulation.history if simulation else []


        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            phase = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            self.stars.append([x, y, phase, speed])

        self._load_images()

    def _load_images(self) -> None:
        self.back = pygame.transform.scale(
            pygame.image.load("visual/galaxybg.jpeg"),
            (self.width, self.height)
        )
        self.planet_original = pygame.transform.scale(
            pygame.image.load("visual/planetfinal.png").convert_alpha(),
            (90, 60)
        )
        self.start_end_img = pygame.transform.scale(
            pygame.image.load("visual/start_endbg.png").convert_alpha(),
            (100, 70)
        )
        self.yellow_img = pygame.transform.scale(
            pygame.image.load("visual/planetyellow.png").convert_alpha(),
            (90, 60)
        )
        self.gray_img = pygame.transform.scale(
            pygame.image.load("visual/planetgray.png").convert_alpha(),
            (90, 60)
        )
        self.drone_img = pygame.transform.scale(
            pygame.image.load("visual/drone.png").convert_alpha(),
            (90, 60)
        )
        self.cyan_img = pygame.transform.scale(
            pygame.image.load("visual/cyanplanet.png").convert_alpha(),
            (90, 60)
        )
        self.brown_image = pygame.transform.scale(
            pygame.image.load("visual/browplanet.png").convert_alpha(),
            (90, 60)
        )

    def map_to_screen(self, x: int, y: int) -> tuple[float, float]:
        screen_center_x = self.width / 2
        screen_center_y = self.height / 2

        screen_x = screen_center_x + (x - self.camera_x) * self.zoom
        screen_y = screen_center_y + (y - self.camera_y) * self.zoom

        return screen_x, screen_y

    def draw_connections(self) -> None:
        for conn in self.connections:
            x1, y1 = self.map_to_screen(conn.hub1.x, conn.hub1.y)
            x2, y2 = self.map_to_screen(conn.hub2.x, conn.hub2.y)
            pygame.draw.line(
                self.screen, (150, 150, 200),
                (x1 + 45, y1 + 30),
                (x2 + 45, y2 + 30), 2
            )

    def draw_stars(self) -> None:
        for star in self.stars:
            x, y, phase, speed = star
            brightness = (math.sin(phase) + 1) / 2
            size = 1 if brightness < 0.7 else 2
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), size)
            star[2] += 0.10 * speed

    def draw_hubs(self) -> None:
        for hub in self.hubs:
            x, y = self.map_to_screen(hub.x, hub.y)

            if hub == self.start_hub or hub == self.end_hub:
                planet = self.start_end_img.copy()

                if hub.color in COLOR_RGB:
                    planet.fill(
                        (*COLOR_RGB[hub.color], 255),
                        special_flags=pygame.BLEND_RGBA_MULT,
                    )
                elif hub.color == "yellow":
                    planet.fill(
                        (255, 255, 0, 255),
                        special_flags=pygame.BLEND_RGBA_MULT,
                    )
                elif hub.color == "gray":
                    planet.fill(
                        (150, 150, 150, 255),
                        special_flags=pygame.BLEND_RGBA_MULT,
                    )
                elif hub.color == "rainbow":
                    rgb = colorsys.hsv_to_rgb(self.hue, 1, 1)
                    rainbow_color = tuple(int(c * 255) for c in rgb)
                    planet.fill(
                        (*rainbow_color, 255),
                        special_flags=pygame.BLEND_RGBA_MULT,
                    )

                offset_y = math.sin(pygame.time.get_ticks() * 0.002) * 2
                rect = planet.get_rect(center=(x + 45, y + 30 + offset_y))
                self.screen.blit(planet, rect)
                continue

            planet = self.planet_original.copy()

            if hub.color in COLOR_RGB:
                planet.fill(
                    (*COLOR_RGB[hub.color], 255),
                    special_flags=pygame.BLEND_RGBA_MULT,
                )
            elif hub.color == "yellow":
                planet = self.yellow_img
            elif hub.color == "cyan":
                planet = self.cyan_img
            elif hub.color == "gray":
                planet = self.gray_img
            elif hub.color == "gold":
                planet = self.yellow_img
            elif hub.color == "silver":
                planet = self.gray_img
            elif hub.color == "brown":
                planet = self.brown_image
            elif hub.color == "rainbow":
                rgb = colorsys.hsv_to_rgb(self.hue, 1, 1)
                rainbow_color = tuple(int(c * 255) for c in rgb)
                planet.fill(
                    (*rainbow_color, 255), special_flags=pygame.BLEND_RGBA_MULT
                )

            rect = planet.get_rect(center=(x + 45, y + 30))
            self.screen.blit(planet, rect)

        self.hue = (self.hue + 0.005) % 1

    def draw_drones(self) -> None:
        by_hub: dict = {}
        for drone in self.drone_list:
            by_hub.setdefault(drone.location, []).append(drone)

        for hub, drones_here in by_hub.items():
            base_x, base_y = self.map_to_screen(hub.x, hub.y)
            for i, drone in enumerate(drones_here):
                offset = (i % 4) * 8
                rect = self.drone_img.get_rect(
                    center=(base_x + 45 + offset, base_y + 30 + offset)
                )
                self.screen.blit(self.drone_img, rect)

    def draw_animation_drones(self) -> None:
        if self.animation_turn >= len(self.history):
            return

        current_moves = self.history[self.animation_turn]

        moving_ids = {
            drone_id
            for drone_id, _, _ in current_moves
        }

        #Drones que n estão mover neste turno!!
        #s desenhados na posição do turno anterior
        if self.animation_turn == 0:
            previous_positions = {
                drone.id_name: self.start_hub
                for drone in self.drone_list
            }
        else:
            previous_positions = {}

            for turn_moves in self.history[:self.animation_turn]:
                for drone_id, _, target in turn_moves:
                    previous_positions[drone_id] = target

        for drone in self.drone_list:

            if drone.id_name in moving_ids:
                continue

            hub = previous_positions.get(
                drone.id_name,
                self.start_hub
            )

            x, y = self.map_to_screen(
                hub.x,
                hub.y
            )

            rect = self.drone_img.get_rect(
                center=(x + 45, y + 30)
            )

            self.screen.blit(
                self.drone_img,
                rect
            )

        #Drones que ESTao mover
        for drone_id, start_hub, target_hub in current_moves:

            start_x, start_y = self.map_to_screen(
                start_hub.x,
                start_hub.y
            )

            target_x, target_y = self.map_to_screen(
                target_hub.x,
                target_hub.y
            )

            x = (
                start_x
                + (target_x - start_x)
                * self.animation_progress
            )

            y = (
                start_y
                + (target_y - start_y)
                * self.animation_progress
            )

            rect = self.drone_img.get_rect(
                center=(x + 45, y + 30)
            )

            self.screen.blit(
                self.drone_img,
                rect
            )
    def render_frame(self) -> None:
        self.screen.blit(self.back, (0, 0))
        self.draw_connections()
        self.draw_stars()
        self.draw_hubs()
        self.draw_animation_drones()
        pygame.display.update()
        self.clock.tick(30)

    def run(self) -> None:
        while self.loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.loop = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.camera_x -= self.camera_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.camera_x += self.camera_speed
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.camera_y -= self.camera_speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.camera_y += self.camera_speed
            if keys[pygame.K_q]:
                self.zoom += self.zoom_speed
            if keys[pygame.K_e]:
                self.zoom -= self.zoom_speed

            self.zoom = max(20, min(self.zoom, 300))
            if self.animation_turn < len(self.history):
                self.animation_progress += 0.03

                if self.animation_progress >= 1.0:
                    self.animation_progress = 0.0
                    self.animation_turn += 1
            self.render_frame()

        pygame.quit()
