import pygame
pygame.init()

class Button(pygame.sprite.Sprite):
	def __init__(self, x, y, image, screen, text = ''):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.screen = screen
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False
		self.text = text

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

		# add text to button
		font = pygame.font.SysFont('FreeMono, Monospace', 60)
		text_img = font.render(self.text, True, (255,255,255))
		text_len = text_img.get_width()
		text_height = text_img.get_height()
			
		# draw button
		self.screen.blit(self.image, self.rect)
		self.screen.blit(text_img, (self.rect.x + (self.width / 2 - text_len / 2), + self.rect.y + (self.height / 2 - text_height / 2)))

		return action