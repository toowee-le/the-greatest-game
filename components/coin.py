import pygame
pygame.init()

class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y, tile_size):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/coin.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x,y) 