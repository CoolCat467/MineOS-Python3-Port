"""Display brail image."""

# Programmed by CoolCat467


from pygame.locals import *

__title__ = "Brail Image"
__author__ = "CoolCat467"
__version__ = "0.0.0"

import numpy as np
import ocif
import pygame

SCREENSIZE = (500, 500)
FPS = 2

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREY = (170, 170, 170)
ORANGE = (255, 128, 0)


def braille_char(set_values: np.ndarray) -> str:
    """Convert array of flags to braille character."""
    flags = set_values.flatten()
    values = (1, 8, 2, 16, 4, 32, 64, 128)
    total = 0
    for flag, value in zip(flags, values):
        total += flag * value
    return chr(10240 + total)


def char_braille(char: str) -> np.ndarray:
    """Convert braille character to array of flags."""
    value = ord(char) - 10240
    flags = np.zeros((4, 2), dtype=bool)
    ##    0, 2, 4, 1,  3, 5,  6,    7
    ##    1, 2, 4, 8, 16, 32, 64, 128
    flag_lookup = (0, 2, 4, 1, 3, 5, 6, 7)
    for idx, div in enumerate(2 ** (7 - x) for x in range(8)):
        flag, value = divmod(value, div)
        if flag:
            flags.flat[flag_lookup[7 - idx]] = True
    return flags


def get_color(color: int, alpha: int = 255) -> pygame.Color:
    """Return color from 24 bit int and optional alpha."""
    return pygame.Color(*map(int, color.to_bytes(3)), 255 - alpha)


BRAILLE_W = 5
BRAILLE_H = 9


def braille_surf(
    char: str, background: np.int32, foreground: np.int32, alpha: np.int16,
) -> pygame.Surface:
    """Get braille surface."""
    ##    background = 16777215
    ##    foreground = 0
    back = get_color(int(background), int(alpha))
    fore = get_color(int(foreground), int(alpha))
    flags = char_braille(char)

    surf = pygame.Surface((BRAILLE_W, BRAILLE_H))
    surf.fill(back)

    surf.lock()
    x = 1
    for fx in range(2):
        y = 1
        for fy in range(4):
            if flags[fy, fx]:
                surf.set_at((x, y), fore)
            y += 2
        x += 2
    surf.unlock()
    return surf


def pict_to_surf(picture: ocif.Picture) -> pygame.Surface:
    """Convert picture to surface."""
    surf = pygame.Surface((picture.width * BRAILLE_W, picture.height * BRAILLE_H))
    for y in range(picture.height):
        for x in range(picture.width):
            surf.blit(braille_surf(*picture.get(x, y)), (x * BRAILLE_W, y * BRAILLE_H))
    return surf


def run() -> None:
    """Start program."""
    # Set up the screen
    screen = pygame.display.set_mode(SCREENSIZE, RESIZABLE, 256 * 2)
    pygame.display.set_caption(__title__ + " " + __version__)
    ##    pygame.display.set_icon(pygame.image.load('icon.png'))
    ##    screen.fill(WHITE)

    # Set up the FPS clock
    clock = pygame.time.Clock()

    picture = ocif.load("AhsokaTano.pic")
    surf = pict_to_surf(picture).convert_alpha()
    pygame.display.set_icon(surf)
    ##    pygame.image.save(surf, "image.png")

    ##    surf = braille_surf(*picture.get(0, 0))
    ##    size = surf.get_size()
    ##    scale = 2
    ##    surf = pygame.transform.scale(surf, (size[0]*scale, size[1]*scale))

    pygame.display.set_mode(surf.get_size(), RESIZABLE, 256)
    screen.blit(surf, (0, 0))

    # Update the display
    pygame.display.update()

    running = True

    # While active
    while running:
        # Event handler
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == VIDEORESIZE:
                screen.blit(pygame.transform.scale(surf, event.size), (0, 0))
                pygame.display.update()

        # Get the time passed from the FPS clock
        time_passed = clock.tick(FPS)
        time_passed / 1000


##        screen.blit(surf, (0, 0))
##
##
##        # Update the display
##        pygame.display.update()

if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.\n")
    try:
        pygame.init()
        run()
    finally:
        pygame.quit()
