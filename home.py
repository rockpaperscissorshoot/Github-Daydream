import pygame, sys
from player import Player

class Game:
    def __init__(self):
        player_sprite = Player((screen_width, screen_height),screen_width,5)
        self.player = pygame.sprite.GroupSingle(player_sprite)
        pass
    def run(self):
        self.player.update()
        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        pass
        # Just like in love you should do updates first then a draw afterwards

if __name__ == "__main__": # this basically tells you if the code thats running is being imported or not
    pygame.init()
    screen_width = 1100
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((30, 30, 30)) # Background color
        game.run()

        pygame.display.flip()
        clock.tick(60)