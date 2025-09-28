import pygame, sys , asyncio
from player import Player
import obstacle
from upgrades import UpgradeCard, get_random_upgrades
from alien import Alien, Extra
from random import choice, randint
from laser import Laser

# Ensure screen size is defined before Game is instantiated
screen_width = 1128
screen_height = 752
screen = pygame.display.set_mode((screen_width, screen_height))
 
class Game:
	def activate_super_speed(self):
		self.player.sprite.speed *= 2
		self.player.sprite.laser_cooldown = 60
		self.super_speed_ready = False
	
	def reset_laser_pierce(self):
		
		for laser in self.player.sprite.lasers:
			laser.pierce_count = 0
		orig_update = getattr(self.player.sprite.lasers.__class__, 'update', None)
		def patched_update(group_self, *args, **kwargs):
			for laser in group_self:
				if not hasattr(laser, 'pierce_count'):
					laser.pierce_count = 0
			if orig_update:
				orig_update(group_self, *args, **kwargs)
		self.player.sprite.lasers.update = patched_update.__get__(self.player.sprite.lasers)
	def __init__(self):
		self.round_transition = False  
		self.round_number = 1
		self.show_round_screen = False
		self.round_screen_timer = 0
		self.alien_speed = 1
		self.super_speed_ready = False

		player_sprite = Player((screen_width / 2, screen_height), screen_width, 5)
		self.player = pygame.sprite.GroupSingle(player_sprite)

		self.lives = 3
		self.live_surf = pygame.image.load('player.png').convert_alpha()
		self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 20)
		self.score = 0
		self.font = pygame.font.Font(None, 32)
		self.game_over = False

		self.shape = obstacle.shape
		self.block_size = 6
		self.blocks = pygame.sprite.Group()
		self.obstacle_amount = 4
		self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
		self.create_multiple_obstacles(*self.obstacle_x_positions, x_start=screen_width / 15, y_start=480)

		self.aliens = pygame.sprite.Group()
		self.alien_lasers = pygame.sprite.Group()
		self.alien_setup(rows=6, cols=8)
		self.alien_direction = 1

		self.extra = pygame.sprite.GroupSingle()
		self.extra_spawn_time = randint(40, 80)

		self.upgrade_cards = []
		self.selected_upgrade = None

		self.bullet_pierce = 1  

		# music = pygame.mixer.Sound('music.wav') -- i'm not sure we can use the music they made
		# music.set_volume(0.2)
		# music.play(loops = -1)
		self.laser_sound = pygame.mixer.Sound('laser.wav')
		self.laser_sound.set_volume(0.5)
		self.explosion_sound = pygame.mixer.Sound('explosion.wav')
		self.explosion_sound.set_volume(0.3)

	def create_obstacle(self, x_start, y_start,offset_x):
		for row_index, row in enumerate(self.shape):
			for col_index,col in enumerate(row):
				if col == 'x':
					x = x_start + col_index * self.block_size + offset_x
					y = y_start + row_index * self.block_size
					block = obstacle.Block(self.block_size,(241,79,80),x,y)
					self.blocks.add(block)

	def create_multiple_obstacles(self,*offset,x_start,y_start):
		for offset_x in offset:
			self.create_obstacle(x_start,y_start,offset_x)

	def alien_setup(self,rows,cols,x_distance = 60,y_distance = 48,x_offset = 70, y_offset = 100):
		for row_index, row in enumerate(range(rows)):
			for col_index, col in enumerate(range(cols)):
				x = col_index * x_distance + x_offset
				y = row_index * y_distance + y_offset
				
				if row_index == 0: alien_sprite = Alien('yellow',x,y)
				elif 1 <= row_index <= 2: alien_sprite = Alien('green',x,y)
				else: alien_sprite = Alien('red',x,y)
				self.aliens.add(alien_sprite)

	def alien_position_checker(self):
		all_aliens = self.aliens.sprites()
		for alien in all_aliens:
			if alien.rect.right >= screen_width:
				self.alien_direction = -1
				self.alien_move_down(2)
			elif alien.rect.left <= 0:
				self.alien_direction = 1
				self.alien_move_down(2)

	def alien_move_down(self,distance):
		if self.aliens:
			for alien in self.aliens.sprites():
				alien.rect.y += distance

	def alien_shoot(self):
		if self.aliens.sprites():
			random_alien = choice(self.aliens.sprites())
			laser_sprite = Laser(random_alien.rect.center,6,screen_height)
			self.alien_lasers.add(laser_sprite)
			self.laser_sound.play()

	def extra_alien_timer(self):
		self.extra_spawn_time -= 1
		if self.extra_spawn_time <= 0:
			self.extra.add(Extra(choice(['right','left']),screen_width))
			self.extra_spawn_time = randint(400,800)

	def collision_checks(self):
		if self.player.sprite.lasers:
			for laser in self.player.sprite.lasers:
				if not hasattr(laser, 'pierce_count') or laser.pierce_count is None:
					laser.pierce_count = 0
				if not hasattr(laser, 'spawn_time') or laser.spawn_time is None:
					laser.spawn_time = pygame.time.get_ticks()
				if pygame.sprite.spritecollide(laser, self.blocks, True):
					laser.kill()
				aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
				if aliens_hit:
					for alien in aliens_hit:
						self.score += alien.value
						self.explosion_sound.play()
						laser.pierce_count += 1
						if laser.pierce_count >= self.bullet_pierce:
							laser.kill()
							break
				elif pygame.sprite.spritecollide(laser, self.extra, True):
					self.score += 500
					laser.kill()
				if self.bullet_pierce == 2 and hasattr(laser, 'spawn_time'):
					if pygame.time.get_ticks() - laser.spawn_time > 8000:
						laser.kill()

		if self.alien_lasers:
			for laser in self.alien_lasers:
				if pygame.sprite.spritecollide(laser, self.blocks, True):
					laser.kill()

				if pygame.sprite.spritecollide(laser, self.player, False):
					laser.kill()
					self.lives -= 1
					if self.lives <= 0:
						self.game_over = True

		
		if self.aliens:
			for alien in self.aliens:
				pygame.sprite.spritecollide(alien, self.blocks, True)

				if pygame.sprite.spritecollide(alien, self.player, False):
					self.game_over = True
	def game_over_message(self):
		if self.game_over:
			pygame.mixer.stop()
			screen.fill((30, 30, 30))
			over_surf = self.font.render('Game Over', False, 'red')
			over_rect = over_surf.get_rect(center=(screen_width / 2, screen_height / 2))
			screen.blit(over_surf, over_rect)
	
	def display_lives(self):
		for live in range(self.lives - 1):
			x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
			screen.blit(self.live_surf,(x,8))

	def display_score(self):
		score_surf = self.font.render(f'Score: {self.score}', False, 'white')
		score_rect = score_surf.get_rect(topleft = (10, 10))
		screen.blit(score_surf, score_rect)

	def victory_message(self):
		if not self.aliens.sprites() and not self.round_transition and not self.show_round_screen:
			if not hasattr(self, 'wave_passed_timer') or self.wave_passed_timer is None:
				self.wave_passed_timer = 5 * 60 
			if self.wave_passed_timer > 0:
				wave_surf = self.font.render('Wave Passed', False, 'white')
				wave_rect = wave_surf.get_rect(center=(screen_width / 2, screen_height / 2))
				screen.blit(wave_surf, wave_rect)
				self.wave_passed_timer -= 1
			else:
				self.wave_passed_timer = None
				self.round_transition = True
				self.upgrade_cards = get_random_upgrades(3)
				self.selected_upgrade = None
	def draw_upgrade_cards(self):
		card_width = 340  
		card_height = 170  
		spacing = 60
		total_width = 3 * card_width + 2 * spacing
		start_x = (screen_width - total_width) // 2
		y = screen_height // 2 - card_height // 2
		for i, card in enumerate(self.upgrade_cards):
			x = start_x + i * (card_width + spacing)
			card.draw(screen, self.font, x, y, card_width, card_height, i+1)

	def draw_round_screen(self):
		round_surf = self.font.render(f'Round {self.round_number}', True, 'yellow')
		screen.blit(round_surf, (screen_width // 2 - round_surf.get_width() // 2, screen_height // 2 - round_surf.get_height() // 2))

	def run(self):
		# Player handles its own firing logic (cooldown/ready)
		if self.round_transition:
			screen.fill((20, 20, 40))
			self.draw_upgrade_cards()
			instr = self.font.render('Choose an upgrade: Click a card', True, 'yellow')
			screen.blit(instr, (screen_width // 2 - instr.get_width() // 2, 100))
		elif self.show_round_screen:
			screen.fill((0, 0, 0))
			self.draw_round_screen()
			self.round_screen_timer -= 1
			if self.round_screen_timer <= 0:
				self.show_round_screen = False
				if self.round_number > 1:
					self.alien_speed += 1
				self.aliens.empty()
				self.alien_lasers.empty()
				self.blocks.empty()
				self.alien_setup(rows=6, cols=8)
				self.create_multiple_obstacles(*self.obstacle_x_positions, x_start=screen_width / 15, y_start=480)
				self.upgrade_cards = []
				self.selected_upgrade = None
		elif not self.game_over and self.aliens:
			self.player.update()
			self.alien_lasers.update()
			self.extra.update()
			self.aliens.update(self.alien_direction * self.alien_speed)
			self.alien_position_checker()
			self.extra_alien_timer()
			self.collision_checks()

			self.player.sprite.lasers.draw(screen)
			self.player.draw(screen)
			self.blocks.draw(screen)
			self.aliens.draw(screen)
			self.alien_lasers.draw(screen)
			self.extra.draw(screen)
			self.display_lives()
			self.display_score()
			self.victory_message()
			self.game_over_message()
		else:
			self.player.sprite.lasers.draw(screen)
			self.player.draw(screen)
			self.blocks.draw(screen)
			self.aliens.draw(screen)
			self.alien_lasers.draw(screen)
			self.extra.draw(screen)
			self.display_lives()
			self.display_score()
			self.victory_message()
			self.game_over_message()

class CRT:
	def __init__(self):
		self.tv = pygame.image.load('tv.png').convert_alpha()
		self.tv = pygame.transform.scale(self.tv,(screen_width,screen_height))

	def create_crt_lines(self):
		line_height = 3
		line_amount = int(screen_height / line_height)
		for line in range(line_amount):
			y_pos = line * line_height
			pygame.draw.line(self.tv,'black',(0,y_pos),(screen_width,y_pos),1)

	def draw(self):
		self.tv.set_alpha(randint(75,90))
		self.create_crt_lines()
		screen.blit(self.tv,(0,0))
async def main():

	if __name__ == '__main__':
		pygame.init()
		screen_width = 1128
		screen_height = 752
		screen = pygame.display.set_mode((screen_width,screen_height))
		clock = pygame.time.Clock()
		game = Game()
		crt = CRT()

		ALIENLASER = pygame.USEREVENT + 1
		pygame.time.set_timer(ALIENLASER,800)

		while True:
			# Activate super speed if E is pressed and ready
			keys = pygame.key.get_pressed()
			if hasattr(game, 'super_speed_ready') and game.super_speed_ready and keys[pygame.K_e]:
				game.activate_super_speed()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == ALIENLASER:
					game.alien_shoot()
				
				if game.round_transition and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
					mouse_x, mouse_y = event.pos
					card_width = 340
					card_height = 170
					spacing = 60
					total_width = 3 * card_width + 2 * spacing
					start_x = (screen_width - total_width) // 2
					y = screen_height // 2 - card_height // 2
					for i, card in enumerate(game.upgrade_cards):
						x = start_x + i * (card_width + spacing)
						rect = pygame.Rect(x, y, card_width, card_height)
						if rect.collidepoint(mouse_x, mouse_y):
							game.selected_upgrade = card
							if 'lasers capable of hitting 2 aliens' in card.name:
								if game.lives > 1:
									game.lives -= 1
								game.bullet_pierce = 2
								game.player.sprite.laser_cooldown = 600
							elif 'fire your lasers faster' in card.name:
								if game.lives > 1:
									game.lives -= 1
								game.player.sprite.laser_cooldown = 300  # 50% faster
								game.bullet_pierce = 1
							elif 'instantly clear all aliens' in card.name:
								if game.lives > 1:
									game.lives -= 1
								game.aliens.empty()
								game.super_speed_ready = True
							else:
								game.bullet_pierce = 1
								game.player.sprite.laser_cooldown = 600
							game.reset_laser_pierce()
							
							screen.fill((30,30,30))
							game.run()
							crt.draw()
							pygame.display.flip()
							game.round_transition = False
							game.show_round_screen = True
							game.round_screen_timer = 2 * 60  
							game.round_number += 1
							break

			screen.fill((30,30,30))
			game.run()
			crt.draw()
			pygame.display.flip()
			clock.tick(60)
			await asyncio.sleep(0)
asyncio.run(main())