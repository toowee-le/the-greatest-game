import pygame
pygame.init()

class Mace(pygame.sprite.Sprite):
	def __init__(self, x, y, health):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/Mace.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0
		# self.health_start = health
		self.health_remaining = health

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter +=1
		if abs(self.move_counter > 50):
			self.move_direction *= -1
			self.move_counter *= -1

		#health bar
		# pygame.draw.rect(screen, red, (self.rect.x, (self.rect.top - 30), self.rect.width, 15))
		# if self.health_remaining > 0:
		# 	pygame.draw.rect(screen, green, (self.rect.x, (self.rect.top - 30), int(self.rect.width * (self.health_remaining / self.health_start)), 15))

			