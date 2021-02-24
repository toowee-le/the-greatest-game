import pygame

class Player:
	def __init__(self, x, y):
		self.reset(x, y)
		self.last_shot = pygame.time.get_ticks()

	# handles player's animations
	def update(self, game_over, blob_group, platform_group, lava_group, water_group, shooter_bullet_group, exit_group, mace_group, saw_group, world, bullet_group, screen_height, screen_width, screen):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20
		cooldown = 500  # milliseconds
		lives = 3

		# load sounds
		coin_fx = pygame.mixer.Sound("img/coin.wav")
		coin_fx.set_volume(0.3)

		jump_fx = pygame.mixer.Sound("img/jump.wav")
		jump_fx.set_volume(0.3)

		game_over_fx = pygame.mixer.Sound("img/game_over.wav")
		game_over_fx.set_volume(0.3)

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
					self.rect.x + 10, self.rect.bottom - 30, player.direction, blob_group, platform_group, lava_group, exit_group, mace_group, saw_group, world
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