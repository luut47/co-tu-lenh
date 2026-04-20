from functools import lru_cache
import os

import pygame


def _convert_surface(surface, use_alpha):
    if pygame.display.get_surface() is None:
        return surface
    return surface.convert_alpha() if use_alpha else surface.convert()


@lru_cache(maxsize=256)
def load_image(path, size=None, use_alpha=True):
    surface = pygame.image.load(path)
    surface = _convert_surface(surface, use_alpha)
    if size is not None:
        surface = pygame.transform.scale(surface, size)
    return surface


def load_image_from_dir(base_dir, filename, size=None, use_alpha=True):
    return load_image(os.path.join(base_dir, filename), size=size, use_alpha=use_alpha)
