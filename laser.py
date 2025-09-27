import pygame

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos,speed = 8):
        super().__init__()
        self.image = pygame.Surface((4,20))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect(center = pos)
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()
