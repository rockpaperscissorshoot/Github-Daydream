import random
import pygame

UPGRADE_LIST = [
    'Sacrifice 1 life to make your lasers capable of hitting 2 aliens',
    'Sacrifice 1 life to fire your lasers faster',
    'Upgrade 3', 'Upgrade 4',
    'Upgrade 5'
]

class UpgradeCard:
    def __init__(self, name):
        self.name = name
        # Placeholder for icon, description, etc.

    def draw(self, screen, font, x, y, width, height, number):
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (40, 40, 80), rect, border_radius=16)
        pygame.draw.rect(screen, (200, 200, 80), rect, 4, border_radius=16)
        # Text wrapping for long descriptions
        def draw_wrapped_text(text, font, color, rect, surface, line_spacing=4):
            words = text.split(' ')
            lines = []
            current_line = ''
            for word in words:
                test_line = current_line + (' ' if current_line else '') + word
                if font.size(test_line)[0] <= rect.width - 20:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            y_offset = rect.y + 20
            for line in lines:
                rendered = font.render(line, True, color)
                text_rect = rendered.get_rect(centerx=rect.centerx, y=y_offset)
                surface.blit(rendered, text_rect)
                y_offset += rendered.get_height() + line_spacing
        draw_wrapped_text(self.name, font, 'white', rect, screen)
        num = font.render(str(number), True, 'yellow')
        num_rect = num.get_rect(center=(x + width // 2, y + height - 20))
        screen.blit(num, num_rect)


def get_random_upgrades(n=3, exclude=None):
    exclude = exclude or []
    available = [u for u in UPGRADE_LIST if u not in exclude]
    if len(available) < n:
        available = UPGRADE_LIST.copy()
    chosen = random.sample(available, n)
    return [UpgradeCard(name) for name in chosen]
