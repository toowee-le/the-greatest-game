import pygame
pygame.init()

class Saw(pygame.sprite.Sprite):
	def __init__(self, x, y, tile_size):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/saw.png')
		self.image = pygame.transform.scale(img, (50,50))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1

	def update(self):
		self.rect.y += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 75:
			self.move_direction *= -1
			self.move_counter *= -1

	def move_towards_player(self, Player):
		dx, dy = self.rect.x - Player.rect.x, self.rect.y - Player.rect.y
		dist = math.hypot(dx, dy)
		dx, dy = dx / dist, dy / dist
		self.rect.x += dx * self.move_direction
		self.rect.y += dy * self.move_direction