import pygame
pygame.init()

class Bullet(pygame.sprite.Sprite):
	def __init__(self,x,y, direction, blob_group, platform_group, lava_group, exit_group, mace_group, world):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/rock9.png')
		self.image = pygame.transform.scale(img, (12,12))
		self.rect = self.image.get_rect()
		self.rect.center = [x,y]
		self.direction = direction
		self.direction = direction
		self.blob_group = blob_group
		self.platform_group = platform_group
		self.lava_group = lava_group
		self.exit_group = exit_group
		self.mace_group = mace_group
		self.world = world

	#bullets disappear after a certain distance and direction is decided below
	def update(self):
		if self.direction == 1:
			self.rect.x += 5
		else: 
			self.rect.x -= 5

		if self.rect.left > 400:
			print('hit')
			self.kill()
		if pygame.sprite.spritecollide(self, (self.blob_group),True):
			self.kill()
		if pygame.sprite.spritecollide(self, (self.platform_group),False):
			self.kill()
		if pygame.sprite.spritecollide(self, (self.platform_group),False):
			self.kill()
		if pygame.sprite.spritecollide(self, (self.lava_group),False):
			self.kill()
		if pygame.sprite.spritecollide(self, (self.exit_group),False):
			self.kill()
		if pygame.sprite.spritecollide(self, (self.mace_group),False):
			self.kill()
			# mace.health_remaining -= 1
		
		for tile in self.world.tile_list:
			#check for collision in x direction
			if tile[1].colliderect(self):
				self.kill()
			# check for collision in y direction
			if tile[1].colliderect(self):
				self.kill()