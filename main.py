from components.button import Button
from components.enemy import Enemy
from components.mace import Mace
from components.lava import Lava
from components.shooter import Shooter
from components.coin import Coin
from components.bullet import Bullet
from components.platform import Platform
from components.exit import Exit

import pygame
from pygame.locals import *
import pickle
from os import path
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 900
screen_height = 900

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')


#define font
font = pygame.font.SysFont('Bauhaus 93', 100)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

#define game variables
tile_size = 45
game_over = 0
main_menu = True
level = 1
max_levels = 7
score = 0
shooter_cooldown = 1000 #bullet cooldown in milliseconds
last_shooter_shot = pygame.time.get_ticks()

#define colour
white = (255,255,255)
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)

#load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

#load sounds

coin_fx = pygame.mixer.Sound('img/coin.wav')
coin_fx.set_volume(0.3)

jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.3)

game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.3)

# def draw_grid():
# 	for line in range(0, 20):
# 		pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
# 		pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x,y))

#reset level function
def reset_level(level):
	player.reset(100, screen_height - 130)
	blob_group.empty()
	lava_group.empty()
	exit_group.empty()
	platform_group.empty()
	mace_group.empty()
	shooter_group.empty()
	shooter_bullet_group.empty()

	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)

	return world

class Player():	
	def __init__(self, x, y):
		self.reset(x, y)
		self.last_shot = pygame.time.get_ticks()

	def update(self,game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20
		cooldown = 500 #milliseconds

		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_UP] and self.jumped == False and self.in_air == False:
				jump_fx.play()
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_UP] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx +=5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			#record current time
			time_now = pygame.time.get_ticks()
 
			if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
				bullet = Bullet(self.rect.x +10, self.rect.bottom -40, player.direction, blob_group, platform_group, lava_group, exit_group, mace_group, world = World(world_data))
				bullet_group.add(bullet)
				self.last_shot = time_now


			#handle animation
			if self.counter > walk_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#add gravity
			self.vel_y +=1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y
			
			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				# check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile [1].bottom - self.rect.top
						self.vel_y = 0
					#if player is above ground i.e falling
					elif self.vel_y >= 0:
						dy = tile [1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False

			#check for collision with enemies
			if pygame.sprite.spritecollide(self,blob_group, False):
				game_over = -1
				game_over_fx.play()
			#check for collision with mace
			if pygame.sprite.spritecollide(self,mace_group, False):
				game_over = -1
				game_over_fx.play()
			#check for collision with lava
			if pygame.sprite.spritecollide(self,lava_group, False):
				game_over = -1
				game_over_fx.play()
			#check for collision with shooter
			if pygame.sprite.spritecollide(self,shooter_group, False):
				game_over = -1
				game_over_fx.play()
			#check for collision with shooter bullets
			if pygame.sprite.spritecollide(self,shooter_bullet_group, False):
				game_over = -1
				game_over_fx.play()
			#check for collision with exit
			if pygame.sprite.spritecollide(self,exit_group, False):
				game_over = 1

			#check for collision with platforms
			for platform in platform_group:
				#collision in x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move with platform - sideways
					if platform.move_x != 0:
						self.rect.x += platform.move_direction

			#update plater cordinates
			self.rect.x += dx
			self.rect.y +=dy

			if self.rect.bottom  > screen_height:
				self.rect.bottom = screen_height
				dy = 0

		elif game_over == -1:
			self.image = self.dead_image
			draw_text('Game Over!', font, blue, (screen_width // 2) - 200, screen_height // 2)
			if self.rect.y > 200:
				self.rect.y -= 5

		# draw player onto screen
		screen.blit(self.image, self.rect)
		# pygame.draw.rect(screen, (255, 255, 255,), self.rect, 2)

		return game_over




	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'img/guy{num}.png')
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('img/ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True

class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load('img/dirt.png')
		grass_img = pygame.image.load('img/grass.png')
		
		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
					blob_group.add(blob)
				if tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
					platform_group.add(platform)
				if tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
					platform_group.add(platform)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + 1 + (tile_size // 2), tile_size)
					lava_group.add(lava)
				if tile == 7:
					coin = Coin(col_count * tile_size // 2, row_count * tile_size + 1 + (tile_size // 2), tile_size)
					coin_group.add(coin)
				if tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2), tile_size)
					exit_group.add(exit)
				if tile == 9:
					mace = Mace(col_count * tile_size, row_count * tile_size + 15, 4)
					mace_group.add(mace)
				if tile == 10:
					shooter = Shooter(col_count * tile_size, row_count * tile_size + 15)
					shooter_group.add(shooter)

				col_count += 1
			row_count += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			#pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

class Shooter_Bullets(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/rock3.png')
		self.image = pygame.transform.scale(img, (12,12))
		self.rect = self.image.get_rect()
		self.rect.center = [x,y]

	#bullets disappear after a certain distance and direction is decided below
	def update(self):
		#record time for shooter bullets
		time_now = pygame.time.get_ticks()
		#shoot
		if time_now - last_shooter_shot > shooter_cooldown:
			shooter_bullet = Shooter_Bullets(shooter.rect.center, shooter.rect.bottom)
			shooter_bullet_group.add(shooter_bullet)
			last_shooter_shot = time_now

		self.rect.x -= 5
		if self.rect.right > 400:
			print('hit')
			self.kill()
		if pygame.sprite.spritecollide(self, (blob_group),False):
			self.kill()
		if pygame.sprite.spritecollide(self, (platform_group),False):
			self.kill()
		if pygame.sprite.spritecollide(self, (lava_group),False):
			self.kill()
		if pygame.sprite.spritecollide(self, (exit_group),False):
			self.kill()
		if pygame.sprite.spritecollide(self, (mace_group),False):
			self.kill()
			mace.health_remaining -= 1

# create instances
player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
mace_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
shooter_group = pygame.sprite.Group()
shooter_bullet_group = pygame.sprite.Group()

#create dummy coin for showing score
score_coin = Coin(tile_size // 2, tile_size // 2, tile_size)
coin_group.add(score_coin)

#load in level data and create world
if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)

#create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img, screen)
start_button = Button(screen_width // 2 -350, screen_height // 2, start_img, screen)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img, screen)

run = True
while run:

	clock.tick(fps)

	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (100, 100))
	if main_menu == True:
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
	else:
		world.draw()

		if game_over == 0:
			blob_group.update()
			mace_group.update()
			bullet_group.update()
			platform_group.update()
			shooter_group.update()
			shooter_bullet_group.update()
			lava_group.update()
			
			#update score & check if coin is collected
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_fx.play()
			draw_text('X ' + str(score), font_score, white, tile_size -10, 10)

		blob_group.draw(screen)
		platform_group.draw(screen)
		lava_group.draw(screen)
		exit_group.draw(screen)
		coin_group.draw(screen)
		mace_group.draw(screen)
		bullet_group.draw(screen)
		shooter_group.draw(screen)
		shooter_bullet_group.draw(screen)


		#draw.grid()
		game_over = player.update(game_over)

		#if player has died
		if game_over == -1:
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0

		#player completes level
		if game_over == 1:
			#reset game and go to next level
			level += 1
			if level <= max_levels:
				#reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
			else:
				draw_text('You Win!', font, blue, (screen_width // 2)- 140, screen_height // 2)
				#restart game
				if restart_button.draw():
					level = 1
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()
