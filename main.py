# import classes
from components.button import Button
from components.enemy import Enemy
from components.mace import Mace
from components.lava import Lava
from components.water import Water
from components.saw import Saw
from components.coin import Coin
from components.platform import Platform
from components.exit import Exit
from components.chest import Chest
from components.tree import Tree

#from swf.movie import SWF

# import and initialize pygame
import pygame
from pygame.locals import *

# import pickle to load and save text files for the 7 levels
import pickle
from os import path
from pygame import mixer
import math

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# create a clock object to track frames per second
clock = pygame.time.Clock()
fps = 60

screen_width = 900
screen_height = 900

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Treasure Forest Game")

# define font
font = pygame.font.SysFont("Bauhaus 93", 100)
font_score = pygame.font.SysFont("Bauhaus 93", 30)
small_font = pygame.font.SysFont("Bauhaus 93", 20)
header_font = pygame.font.Font('Rubik-Mono-One.ttf', 65)
main_font = pygame.font.Font('Rubik-Mono-One.ttf', 16)

# define game variables
tile_size = 45
game_over = 0
lives = 3
main_menu = True
instruction_menu = True
level = 1
max_levels = 7
score = 0
shooter_cooldown = 1000 # bullet cooldown in milliseconds
last_shooter_shot = pygame.time.get_ticks()
sound = 0

# define colour
white = (255, 255, 255)
blue = (0, 0, 255)
red = (231, 15, 17)
green = (0, 255, 0)

# load images
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
instruction_img = pygame.image.load('img/instruction_btn.png')
home_btn = pygame.image.load('img/home_btn.png')
scoreboard_img = pygame.image.load('img/scoreboard_btn.png')
sound_on_img = pygame.image.load('img/sound_on_btn.png')
sound_on_img = pygame.transform.scale(sound_on_img, (100, 100))
sound_off_img = pygame.image.load('img/sound_off_btn.png')
sound_off_img = pygame.transform.scale(sound_off_img, (100, 100))
bg_img = pygame.image.load('img/bg.png')
bg_img = pygame.transform.scale(bg_img, (1820, 1000))
sun_img = pygame.image.load('img/sun.png')
dirt_img = pygame.image.load('img/dirt.png')
grass_img = pygame.image.load('img/grass.png')

# load sounds
music_fx = pygame.mixer.Sound('img/bg_music.wav')
music_fx.set_volume(0.2)

coin_fx = pygame.mixer.Sound("img/coin.wav")
coin_fx.set_volume(0.3)

jump_fx = pygame.mixer.Sound("img/jump.wav")
jump_fx.set_volume(0.3)

game_over_fx = pygame.mixer.Sound("img/game_over.wav")
game_over_fx.set_volume(0.3)

# def draw_grid():
# 	for line in range(0, 20):
# 		pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
# 		pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

# reset level function
def reset_level(level):
	player.reset(100, screen_height - 130)
	blob_group.empty()
	lava_group.empty()
	exit_group.empty()
	platform_group.empty()
	mace_group.empty()
	saw_group.empty()
	shooter_bullet_group.empty()
	water_group.empty()
	chest_group.empty()
	tree_group.empty()

	if path.exists(f"level{level}_data"):
		pickle_in = open(f"level{level}_data", "rb")
		world_data = pickle.load(pickle_in)
	world = World(world_data)

	return world

class Player:
	def __init__(self, x, y):
		self.reset(x, y)
		self.last_shot = pygame.time.get_ticks()

	# handles player's animations
	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20
		cooldown = 500  # milliseconds
		lives = 3

		# check the game is still running
		if game_over == 0 and lives > 0:
			# get keypresses
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
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				# reset player to stand still when not moving
				self.counter = 0
				self.index = 0
				# check if right or left keys are pressed to change player direction
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			# record current time
			time_now = pygame.time.get_ticks()

			if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
				bullet = Bullet(
					self.rect.x + 10, self.rect.bottom - 30, player.direction
				)
				bullet_group.add(bullet)
				self.last_shot = time_now

			# handle player's walking animation
			if self.counter > walk_cooldown:
				self.counter = 0
				self.index += 1
				# reset image index to 0 after the last image displays
				if self.index >= len(self.images_right):
					self.index = 0
				# check if right or left keys are pressed to change player's facing direction
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			# add gravity when player jumps
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			# check for collision with block tiles
			self.in_air = True
			for tile in world.tile_list:
				# check for collision in x direction
				if tile[1].colliderect(
					self.rect.x + dx, self.rect.y, self.width, self.height
				):
					dx = 0
				# check for collision in y direction
				if tile[1].colliderect(
					self.rect.x, self.rect.y + dy, self.width, self.height
				):
					# check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					# if player is above ground i.e falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False

			# check for collision with enemies
			if pygame.sprite.spritecollide(self, blob_group, False):
				game_over = -1
				game_over_fx.play()
			# check for collision with mace
			if pygame.sprite.spritecollide(self, mace_group, False):
				game_over = -1
				game_over_fx.play()
			# check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
				game_over_fx.play()
			# check for collision with water
			if pygame.sprite.spritecollide(self,water_group, False):
				game_over = -1
				game_over_fx.play()
			# check for collision with saw
			if pygame.sprite.spritecollide(self, saw_group, False):
				game_over = -1
				game_over_fx.play()
			# check for collision with shooter bullets
			if pygame.sprite.spritecollide(self,shooter_bullet_group, False):
				game_over = -1
				game_over_fx.play()
			# check for collision with exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1

			# check for collision with platforms
			for platform in platform_group:
				# collision in x direction
				if platform.rect.colliderect(
					self.rect.x + dx, self.rect.y, self.width, self.height
				):
					dx = 0
				# collision in y direction
				if platform.rect.colliderect(
					self.rect.x, self.rect.y + dy, self.width, self.height
				):
					# check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					# check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					# move with platform - sideways
					if platform.move_x != 0:
						self.rect.x += platform.move_direction

			# update plater cordinates
			self.rect.x += dx
			self.rect.y += dy

			if self.rect.bottom > screen_height:
				self.rect.bottom = screen_height
				dy = 0

		# if player has died
		elif game_over == -1:
			self.image = self.dead_image
			if self.rect.y > 200:
				self.rect.y -= 5

		# draw player onto screen
		screen.blit(self.image, self.rect)
		# pygame.draw.rect(screen, (255, 255, 255,), self.rect, 2)

		# return the global game_over variable which will change if player collides with enemies/obstacles
		return game_over
		return lives

	# reset the game with player at starting initalized position
	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f"img/guy{num}.png")
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load("img/ghost.png")
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

# a class for the world map
class World:
	def __init__(self, data):
		self.tile_list = []

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				#1 dirt
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				#2 grass
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				#3 enemy blob
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
					blob_group.add(blob)
				#4 platform
				if tile == 4:
					platform = Platform(
						col_count * tile_size, row_count * tile_size, 1, 0, tile_size
					)
					platform_group.add(platform)
				#5 platform
				if tile == 5:
					platform = Platform(
						col_count * tile_size, row_count * tile_size, 0, 1,tile_size
					)
					platform_group.add(platform)
				#6 lava
				if tile == 6:
					lava = Lava(
						col_count * tile_size,
						row_count * tile_size + 1 + (tile_size // 2),
						tile_size
					)
					lava_group.add(lava)
				#7 coin
				if tile == 7:
					coin = Coin(
						col_count * tile_size // 2,
						row_count * tile_size + 1 + (tile_size // 2),
						tile_size
					)
					coin_group.add(coin)
				#8 exit level door
				if tile == 8:
					exit = Exit(
						col_count * tile_size, row_count * tile_size - (tile_size // 2), tile_size
					)
					exit_group.add(exit)
				#9 mace enemy
				if tile == 9:
					mace = Mace(col_count * tile_size, row_count * tile_size + 15, 4)
					mace_group.add(mace)
				#10 saw
				if tile == 10:
					saw = Saw(col_count * tile_size, row_count * tile_size + 15, tile_size)
					saw_group.add(saw)
					#shooter.move_towards_player(player)
				#11 chest
				if tile == 11:
					chest = Chest(col_count * tile_size, row_count * tile_size + 15)
					chest_group.add(chest)
				# from tuyet's branch
				# if tile == 11:
				# 	chest = Chest(col_count * tile_size // 2, row_count * tile_size + 1 + (tile_size // 2), tile_size)
				# 	chest_group.add(chest)
				#12 water
				# if tile == 12:
				# 	water = Water(col_count * tile_size, row_count * tile_size + 1 + (tile_size // 2), tile_size)
				# 	water_group.add(water)
				#13 tree
				# if tile == 13:
				# 	tree = Tree(col_count * tile_size // 2, row_count * tile_size + 1 + (tile_size // 2), tile_size)
				# 	tree_group.add(tree)
				# # flowers
				# if tile == 15:
				# 	flower = Flower(col_count * tile_size // 2, row_count * tile_size + 1 + (tile_size // 2), tile_size)
				# 	flower_group.add(flower)
				# # rock
				# if tile == 16:
				# 	rock = rock(col_count * tile_size // 2, row_count * tile_size + 1 + (tile_size // 2), tile_size)
				# 	rock_group.add(rock)
				# character animation

				col_count += 1
			row_count += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			# pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/rock9.png")
        self.image = pygame.transform.scale(img, (12, 12))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.direction = direction

    # bullets disappear after a certain distance and direction is decided below
    def update(self):
        if self.direction == -1:
            self.rect.x -= 5
        else:
            self.rect.x += 5

        if pygame.sprite.spritecollide(self, (blob_group), True):
            self.kill()
        if pygame.sprite.spritecollide(self, (platform_group), False):
            self.kill()
        if pygame.sprite.spritecollide(self, (platform_group), False):
            self.kill()
        if pygame.sprite.spritecollide(self, (lava_group), False):
            self.kill()
        if pygame.sprite.spritecollide(self, (exit_group), False):
            self.kill()
        if pygame.sprite.spritecollide(self, (mace_group), False):
            self.kill()
            # mace.health_remaining -= 1
        if pygame.sprite.spritecollide(self, (saw_group), True):
            self.kill()

        for tile in world.tile_list:
            # check for collision in x direction
            if tile[1].colliderect(self):
                self.kill()
            # check for collision in y direction
            if tile[1].colliderect(self):
                self.kill()

player = Player(100, screen_height - 130)

# groups
blob_group = pygame.sprite.Group()
chest_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
mace_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
saw_group = pygame.sprite.Group()
shooter_bullet_group = pygame.sprite.Group()
chest_group = pygame.sprite.Group()
tree_group = pygame.sprite.Group()

# create dummy coin for showing score
score_coin = Coin(tile_size // 2, tile_size // 2, tile_size)
coin_group.add(score_coin)

# load in level data and create world
if path.exists(f"level{level}_data"):
	pickle_in = open(f"level{level}_data", "rb")
	world_data = pickle.load(pickle_in)
world = World(world_data)

# create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img, screen)
start_button = Button(screen_width // 2 - 130, screen_height // 2 - 66, start_img, screen, 'START')
exit_button = Button(screen_width // 2 + 152, screen_height // 2 - 65, exit_img, screen)
instruction_button = Button(screen_width // 2 - 280, screen_height // 2 - 65, instruction_img, screen)
scoreboard_button = Button(750, 750, scoreboard_img, screen)
sound_on_button = Button(20, 20, sound_on_img, screen)
sound_off_button = Button(130, 20, sound_off_img, screen) 

# draw menu buttons
def draw_menu_window():
	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (100, 100))

def draw_instruction_window():
	screen.fill((0,0,0))
	screen.blit(bg_img, (0, 0))

	draw_text(
		f"HOW TO PLAY:",
		header_font,
		red,
		(screen_width // 3) - 204,
		(screen_height // 3) - 170,
	)
	draw_text(
		f"- Move character to his next level with arrow keys",
		main_font,
		(0,0,0),
		(screen_width // 3) - 200,
		(screen_height // 3) - 85,
	)
	draw_text(
		f"- Jump with UP key to avoid obstacles",
		main_font,
		(0,0,0),
		(screen_width // 3) - 200,
		(screen_height // 3) - 55,
	)
	draw_text(
		f"- Throw rocks with space bar to destroy enemies",
		main_font,
		(0,0,0),
		(screen_width // 3) - 200,
		(screen_height // 3) - 25,
	)
	draw_text(
		f"- Avoid the mace or you'll lose a live",
		main_font,
		(0,0,0),
		(screen_width // 3) - 200,
		(screen_height // 3) + 5,
	)
	draw_text(
		f"- Get the treasure chest for extra points",
		main_font,
		(0,0,0),
		(screen_width // 3) - 200,
		(screen_height // 3) + 35,
	)
	draw_text(
		f"There's 7 levels and you only have 3 lives.",
		main_font,
		(0,0,0),
		(screen_width // 3) - 200,
		(screen_height // 3) + 105,
	)
	draw_text(
		f"Choose your moves wisely.",
		main_font,
		(0,0,0),
		(screen_width // 3) - 200,
		(screen_height // 3) + 135,
	)
	draw_text(
		f"Let the games begin!!!",
		main_font,
		(0,0,0),
		(screen_width // 3) - 200,
		(screen_height // 3) + 165,
	)

# main game loop
run = True
while run:

	clock.tick(fps)

	draw_menu_window()

	# display menu page
	if main_menu == True:
		# sound buttons
		if sound_on_button.draw() and sound == 0:
			sound = 1
			music_fx.play()
		if sound_off_button.draw() and sound == 1:
			sound = 0
			music_fx.stop()
		
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
			instruction_menu = False

		scoreboard_button.draw()

		# display instructions page
		if instruction_button.draw():
			main_menu = False
			instruction_menu = True

	elif instruction_menu == True:
		draw_instruction_window()

		# create and draw home button
		home_button = Button(screen_width // 2 - 90, screen_height // 2 + 160, home_btn, screen)
		if home_button.draw():
			instruction_menu = False
			main_menu = True

	else:
		world.draw()

		# if the game is still running and player hasn't died
		if game_over == 0:
			blob_group.update()
			mace_group.update()
			bullet_group.update()
			platform_group.update()
			saw_group.update()
			shooter_bullet_group.update()
			lava_group.update()
			water_group.update()
			chest_group.update()

			# update score & check if coin is collected
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_fx.play()
			draw_text("X " + str(score), font_score, white, tile_size - 10, 10)

			if pygame.sprite.spritecollide(player, chest_group, True):
				score += 3
				coin_fx.play()
			draw_text("X " + str(score), font_score, white, tile_size - 10, 10)

		blob_group.draw(screen)
		platform_group.draw(screen)
		lava_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)
		coin_group.draw(screen)
		mace_group.draw(screen)
		bullet_group.draw(screen)
		saw_group.draw(screen)
		shooter_bullet_group.draw(screen)
		chest_group.draw(screen)
		tree_group.draw(screen)

		draw_text("LIVES: " + str(lives), font_score, white, tile_size + 700, 10)
		draw_text("LEVEL: " + str(level) + "/7", font_score, white, tile_size + 350, 10)

		# draw.grid()
		game_over = player.update(game_over)

		# if player has died
		if game_over == -1 and lives > 0:
			draw_text(
				f"You have {lives - 1} lives left",
				font,
				(127, 255, 212),
				(screen_width // 3) - 200,
				screen_height // 3,
			)
			draw_text(
				f"Coins lost: {score}",
				font,
				(127, 255, 212),
				(screen_width // 3) - 200,
				screen_height // 3 - 100,
			)
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				lives -= 1
				print(lives)
				score = 0
		# if lost 3 lives
		if lives == 0:
			draw_text(
				"Game Over! Play again?",
				font,
				(127, 255, 212),
				(screen_width // 2) - 400,
				screen_height // 2,
			)
			score = 0
			# restart game
			if restart_button.draw():
				level = 1
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0
				lives = 3
		# player completes level
		if game_over == 1:
			# reset game and go to next level
			level += 1
			if level <= max_levels:
				# reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
			else:
				draw_text(
					"You Win!",
					font,
					blue,
					(screen_width // 2) - 100,
					screen_height // 2 - 100,
				)
				draw_text(
					f"Coins won: {score}",
					font,
					blue,
					(screen_width // 2) - 140,
					screen_height // 2,
				)
				# restart game
				if restart_button.draw():
					level = 1
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0
		elif game_over == -1 and lives == 0:
			draw_text(
				"You loose!", font, blue, (screen_width // 2) - 140, screen_height // 2
			)
			# restart game
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
