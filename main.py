from utils import scale_img, blit_rotate_center, blit_txt_center
import pygame
import math
import time
pygame.font.init()

# Load images:
GRASS = scale_img(pygame.image.load('assets/grass.jpg'), 2.5)
TRACK = scale_img(pygame.image.load('assets/track.png'), 0.9)
TRACK_BOR = scale_img(pygame.image.load('assets/track-border-s.png'), 0.9)
TRACK_BOR_MASK = pygame.mask.from_surface(TRACK_BOR)
FINISH = scale_img(pygame.image.load('assets/finish.png'), 0.8)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POS = (138, 250)

PLAYER_CAR = scale_img(pygame.image.load('assets/bugatti.png'), 0.055)
AI_CAR = scale_img(pygame.image.load('assets/918.png'), 0.055)

# Window setup:
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Nürburgring Racing')
FONT = pygame.font.Font('font\\futura.ttf', 44)
FONT_S = pygame.font.Font('font\\futura.ttf', 22)
FPS = 120

PATH = [(176, 125), (121, 76), (67, 122), (65, 464), (142, 559), (313, 730), (375, 722), (405, 664), (418, 532), (508, 477), (596, 544), (606, 695), (672, 740), (735, 686), (734, 419), (697, 370), (435, 365), (397, 318), (447, 263), (696, 262), (744, 197), (714, 89), (334, 80), (287, 108), (285, 177), (288, 352), (234, 415), (180, 360), (180, 260)]

class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return time.time() - self.level_start_time

class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.accel = 0.1
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.accel, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.accel, -self.max_vel / 2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical_vel = math.cos(radians) * self.vel
        horizontal_vel = math.sin(radians) * self.vel

        self.x -= horizontal_vel
        self.y -= vertical_vel

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset) # point of intersection
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

class PlayerCar(AbstractCar):
    IMG = PLAYER_CAR
    START_POS = (180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.accel / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

class AICar(AbstractCar):
    IMG = AI_CAR
    START_POS = (150, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        # self.draw_points(win)

    def calc_angle(self):
        target_x, target_y = self.path[self.current_point]
        dx = target_x - self.x
        dy = target_y - self.y

        if dy == 0:
            desired_rad_angle = math.pi/2
        else:
            desired_rad_angle = math.atan(dx/dy)

        if target_y > self.y:
            desired_rad_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_rad_angle)

        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calc_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0

def draw(win, imgs, player_car, ai_car, game_info):
    for img, pos in imgs:
        win.blit(img, pos)

    level_txt = FONT_S.render(f'Level: {game_info.level}', True, (245, 245, 245))
    win.blit(level_txt, (10, HEIGHT - level_txt.get_height() - 70))

    time_txt = FONT_S.render(f'Time: {round(game_info.get_level_time(), 2)}', True, (245, 245, 245))
    win.blit(time_txt, (10, HEIGHT - time_txt.get_height() - 40))

    velocity_txt = FONT_S.render(f'Speed: {round(player_car.vel, 2)}px/s', True, (245, 245, 245))
    win.blit(velocity_txt, (10, HEIGHT - velocity_txt.get_height() - 10))

    player_car.draw(win)
    ai_car.draw(win)
    pygame.display.update()

def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()
    if not moved:
        player_car.reduce_speed()


def handle_collision(player_car, ai_car, game_info):
    if player_car.collide(TRACK_BOR_MASK) != None:
        player_car.bounce()

    ai_finish_poi_collide = ai_car.collide(FINISH_MASK, *FINISH_POS)
    if ai_finish_poi_collide != None:
        WIN.fill((10, 240, 182))
        blit_txt_center(WIN, FONT, 'You lost!')
        pygame.display.update()
        pygame.time.wait(3000)
        game_info.reset()
        player_car.reset()
        ai_car.reset()

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POS)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            ai_car.next_level(game_info.level)

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, (FINISH_POS))]
player_car = PlayerCar(1.9, 2)
ai_car = AICar(0.9, 2, PATH)
game_info = GameInfo()

while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, ai_car, game_info)

    while not game_info.started:
        WIN.fill((10, 240, 182))
        blit_txt_center(WIN, FONT, f'Click the mouse to start level {game_info.level}!')
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    move_player(player_car)
    ai_car.move()

    handle_collision(player_car, ai_car, game_info)

    if game_info.game_finished():
        WIN.fill((10, 240, 182))
        blit_txt_center(WIN, FONT, 'You beat the AI!')
        pygame.display.update()
        pygame.time.wait(3000)
        game_info.reset()
        player_car.reset()
        ai_car.reset()

pygame.quit()