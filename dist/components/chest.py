import pygame
pygame.init()

class Chest(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		image = pygame.image.load("img/chest.png")
		self.image = pygame.transform.scale(image, (50,50))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self):
		pass