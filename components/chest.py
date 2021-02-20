import pygame
pygame.init()

class Chest(pygame.sprite.Sprite):
	def __init__(self, x, y, tile_size):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/chest.png')
		self.image = pygame.transform.scale(img, (50,50))
		self.rect = self.image.get_rect()
		self.rect.center = (x,y) 