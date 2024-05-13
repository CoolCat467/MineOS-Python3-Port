"""Display brail image."""

# Programmed by CoolCat467


from pygame.locals import (
    DROPFILE,
    K_ESCAPE,
    KEYUP,
    QUIT,
    RESIZABLE,
    SRCALPHA,
    VIDEORESIZE,
)

__title__ = "Brail Image"
__author__ = "CoolCat467"
__version__ = "0.0.0"

import numpy as np
import ocif
import pygame

FPS = 2
FONT_FILE = "unifont-15.1.05.otf"


def get_color(color: int, alpha: int = 255) -> pygame.Color:
    """Return color from 24 bit int and optional alpha."""
    return pygame.Color(*map(int, color.to_bytes(3)), alpha)


def char_surf(
    char: str,
    foreground: np.uint32,
    background: np.uint32,
    alpha: np.uint8,
    font: pygame.font.Font,
) -> pygame.Surface:
    """Render character surface from pixel data."""
    back = get_color(int(background), int(alpha))
    fore = get_color(int(foreground), int(alpha))
    return font.render(char, False, fore, back)


class RenderedPicture(ocif.Picture):
    """Resizable Picture."""

    __slots__ = ()

    def render(self, font_size: int = 10) -> pygame.Surface:
        """Convert picture to surface."""
        font = pygame.font.Font(FONT_FILE, font_size)
        wsize = font_size // 2

        surf = pygame.Surface(
            (self.width * wsize, self.height * font_size),
            SRCALPHA,
        )
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.get(x, y)
                surf.blit(char_surf(*pixel, font), (x * wsize, y * font_size))
        return surf

    def get_fontsize(self, _width: int, height: int) -> int:
        """Get fontsize for given screen dimensions."""
        ##        print(f'{width = }\t\t{height = }')
        ##        print(f'{self.width = }\t{self.height = }')
        lines = self.height
        return height // lines


def run() -> None:
    """Start program."""
    # Load picture
    picture = RenderedPicture.from_picture(ocif.load("Pictures/Nettle.pic"))

    # Convert to image
    font_size = 10
    surf = picture.render(font_size)

    pygame.display.set_icon(surf)
    pygame.image.save(surf, "image.png")

    # Set up the screen
    screen = pygame.display.set_mode(
        surf.get_size(),
        RESIZABLE,
        256,
        vsync=True,
    )
    pygame.display.set_caption(f"{__title__} {__version__}")
    screen.fill((255, 255, 255))
    screen.blit(surf, (0, 0))

    # Update the display
    pygame.display.update()

    # Set up the FPS clock
    clock = pygame.time.Clock()

    running = True

    # While active
    while running:
        # Event handler
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYUP and event.key == K_ESCAPE:
                pygame.event.post(pygame.event.Event(QUIT))
            elif event.type == VIDEORESIZE:
                # Update fontsize
                old_font_size = font_size
                font_size = picture.get_fontsize(*event.size)

                if font_size != old_font_size:
                    # Re-render at new font size
                    surf = picture.render(font_size)

                # Redraw scaled image
                screen.blit(pygame.transform.scale(surf, event.size), (0, 0))

                # Update display
                pygame.display.update()
            elif event.type == DROPFILE:
                # Load picture
                picture = RenderedPicture.from_picture(ocif.load(event.file))

                # Render at current font size
                surf = picture.render(font_size)

                # Update icon
                pygame.display.set_icon(surf)

                # Reset screen dimensions
                screen = pygame.display.set_mode(
                    surf.get_size(),
                    RESIZABLE,
                    256,
                    vsync=True,
                )

                # Draw image to screen
                screen.blit(surf, (0, 0))

                # Update the display
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
