import pygame
pygame.init()

class Button():
	def __init__(self, x, y, image, screen):
		self.image = image
		self.screen = screen
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True
		
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
			
		#draw button
		self.screen.blit(self.image, self.rect)

		return action