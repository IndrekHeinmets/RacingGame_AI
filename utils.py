import pygame

def scale_img(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blit_rotate_center(win, img, top_left, angle):
    rotated_img = pygame.transform.rotate(img, angle)
    new_rect = rotated_img.get_rect(center=img.get_rect(topleft=top_left).center)
    win.blit(rotated_img, new_rect.topleft)

def blit_txt_center(win, font, txt):
    render = font.render(txt, True, (245, 245, 245))
    win.blit(render, (win.get_width()/2  - render.get_width()/2, win.get_height()/2 - render.get_height()/2))
