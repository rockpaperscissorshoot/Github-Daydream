import pygame, sys

class Game:
    def __init__(self):
        pass
    def run(self):
        pass
        # Just like in love you should do updates first then a draw afterwards

if __name__ == "__main__": # this basically tells you if the code thats running is being imported or not
    pygame.init()
    screen_width = 600
    screen_height = 400
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