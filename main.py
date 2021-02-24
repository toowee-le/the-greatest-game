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
from components.bullet import Bullet
from components.player import Player

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

# set gamw window size
screen_width = 900
screen_height = 900

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Treasure Forest Game")

# define font
header_font = pygame.font.Font('Rubik-Mono-One.ttf', 65)
main_font = pygame.font.Font('Rubik-Mono-One.ttf', 19)

# define font colour
white = (255, 255, 255)
red = (231, 15, 17)
green = (0, 255, 0)
black = (45, 45, 45)

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

"""
Helper methods
"""

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

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

"""
Draw window methods
"""

def draw_menu_window():
	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (710, 60))

def draw_instruction_window():
	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (710, 60))

	draw_text(
		f"HOW TO PLAY:",
		header_font,
		red,
		(screen_width // 3) - 204,
		(screen_height // 3) - 170,
	)
	draw_text(
		f"-  Move character around the treasure",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) - 75,
	)
	draw_text(
		f"   forest to his next level with -arrow keys-",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) - 55,
	)
	draw_text(
		f"-  Don't fall in the lava or river by",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) - 15,
	)
	draw_text(
		f"   jumping with the -up- key",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) + 5,
	)
	draw_text(
		f"-  Destory enemies by throwing rocks",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) + 45,
	)
	draw_text(
		f"   at them with -space bar-",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) + 65,
	)
	draw_text(
		f"-  Avoid the mace or you'll lose a live",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) + 105,
	)
	draw_text(
		f"-  Open the treasure chest for extra points",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) + 145,
	)
	draw_text(
		f"-  Levels of play are from 1 to 7",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) + 185,
	)
	draw_text(
		f"-  Choose your moves wisely or you will ",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) + 225,
	)
	draw_text(
		f"   lose all your coins",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) + 245,
	)
	draw_text(
		f"-  Let the games begin treasure hunter!",
		main_font,
		black,
		(screen_width // 3) - 200,
		(screen_height // 3) + 295,
	)

# a class to create the game map
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
				#12 water
				if tile == 12:
					water = Water(
						col_count * tile_size,
						row_count * tile_size + 1 + (tile_size // 2),
						tile_size
					)
					water_group.add(water)
				#13 tree
				if tile == 13:
					tree = Tree(col_count * tile_size // 2, row_count * tile_size + 1 + (tile_size // 2), tile_size)
					tree_group.add(tree)

				col_count += 1
			row_count += 1

	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			# pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

# sprite groups
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

# create player
player = Player(100, screen_height - 130)

# create buttons
restart_button = Button(screen_width // 2 - 55, screen_height // 2 + 40, restart_img, screen)
start_button = Button(screen_width // 2 - 130, screen_height // 2 - 66, start_img, screen, 'START')
exit_button = Button(screen_width // 2 + 152, screen_height // 2 - 65, exit_img, screen)
instruction_button = Button(screen_width // 2 - 280, screen_height // 2 - 65, instruction_img, screen)
play_button = Button(screen_width // 2 - 60, screen_height // 2 + 200, start_img, screen, 'PLAY')
home_button = Button(screen_width // 2 - 230, screen_height // 2 + 200, home_btn, screen)
scoreboard_button = Button(750, 750, scoreboard_img, screen)
sound_on_button = Button(20, 20, sound_on_img, screen)
sound_off_button = Button(130, 20, sound_off_img, screen)

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
			music_fx.play(-1)
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

	# if user clicked on instruction page
	elif instruction_menu == True:
		draw_instruction_window()

		# take user back to main menu
		if home_button.draw():
			instruction_menu = False
			main_menu = True

		# take user to game
		if play_button.draw():
			main_menu = False
			instruction_menu = False

	# if user clicked to play game
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
			draw_text("X" + str(score), main_font, white, tile_size, 10)

			if pygame.sprite.spritecollide(player, chest_group, True):
				score += 3
				coin_fx.play()
			draw_text("X" + str(score), main_font, white, tile_size, 10)

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

		draw_text("LIVES:" + str(lives), main_font, white, tile_size + 700, 10)
		draw_text("LEVEL: " + str(level) + "/7", main_font, white, tile_size + 325, 10)

		# draw.grid()
		game_over = player.update(game_over, blob_group, platform_group, lava_group, water_group, shooter_bullet_group, exit_group, mace_group, saw_group, world, bullet_group, screen_height, screen_width, screen)

		# display score and lives left when player dies
		if game_over == -1 and lives > 0:
			draw_text(
				f"You lost {score} coins",
				main_font,
				black,
				(screen_width // 3) + 28,
				(screen_height // 3) + 100,
			)
			draw_text(
				f"{lives - 1} lives left",
				main_font,
				black,
				(screen_width // 3) + 60,
				(screen_height // 3) + 130,
			)
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				lives -= 1
				print(lives)
				score = 0
		# if player loses all 3 lives
		if lives == 0:
			draw_text(
				"You lose!", 
				main_font,
				red, 
				(screen_width // 3) + 80, 
				(screen_height // 3) + 60
			)
			draw_text(
				"Game Over",
				main_font,
				black,
				(screen_width // 3) + 76,
				(screen_height // 3) + 100,
			)
			draw_text(
				"Play again?",
				main_font,
				black,
				(screen_width // 3) + 65,
				(screen_height // 3) + 130,
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
		# when player completes a level, reset game and go to next level
		if game_over == 1:
			level += 1
			if level <= max_levels:
				# reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
			else:
				draw_text(
					"You Win!",
					main_font,
					green,
					(screen_width // 3) + 75,
					(screen_height // 3) + 100,
				)
				draw_text(
					f"Coins won: {score}",
					main_font,
					black,
					(screen_width // 3) + 65,
					(screen_height // 3) + 130,
				)
				# restart game
				if restart_button.draw():
					level = 1
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0
		elif game_over == -1 and lives == 0:
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
