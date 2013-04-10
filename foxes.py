import sys
import random
from random import randint
import time
import itertools
import pygame
from pygame.locals import *
import colors

pygame.init()

DISPLAYSURF = pygame.display.set_mode((1080, 740))
SURF = DISPLAYSURF.convert_alpha()
pygame.display.set_caption("Foxes vs. Rabbits")
FPS = 30
fpsClock = pygame.time.Clock()
SCREENWIDTH = 1080
HALFWIDTH = SCREENWIDTH / 2
SCREENHEIGHT = 740
HALFHEIGHT = SCREENHEIGHT / 2

text12 = pygame.font.Font("freesansbold.ttf", 12)
text16 = pygame.font.Font("freesansbold.ttf", 16)
text24 = pygame.font.Font("freesansbold.ttf", 24)
text32 = pygame.font.Font("freesansbold.ttf", 32)

class Point(object):
	def __init__(self, x, y, color, size=5):
		self.x = x
		self.y = y
		self.color = color
		self.size = size
		
class Animal(object):
	def check_direction(self):
		if random.randint(1, 1000) <= self.erraticness:
			self.direction = random.choice(self.directions)
	
	def move(self):
		if self.eating:
			pass
		elif self.direction == "up":
			if self.Rect.top < self.Rect.height / 2:
				self.direction = "down"
				self.Rect.centery += self.speed
			else:
				self.Rect.centery -= self.speed
		elif self.direction == "down":
			if self.Rect.bottom > SCREENHEIGHT - (self.Rect.height / 2):
				self.direction = "up"
				self.Rect.centery -= self.speed
			else:
				self.Rect.centery += self.speed
		elif self.direction == "left":
			if self.Rect.left < self.Rect.width / 2:
				self.direction = "right"
				self.Rect.centerx += self.speed
			else:
				self.Rect.centerx -= self.speed
		elif self.direction == "right":
			if self.Rect.right > SCREENWIDTH - self.Rect.width / 2:
				self.direction = "left"
				self.Rect.centerx -= self.speed
			else:
				self.Rect.centerx += self.speed
				
class Grass(object):
	def __init__(self):
		self.maxbelly = 500
		self.belly = 500
		self.icon = pygame.image.load("grass.png").convert()
		self.Rect = self.icon.get_rect()
		self.growth_rate = 2
	def update(self):
		if self.belly < self.maxbelly: 
			self.belly += self.growth_rate
		if self.belly > self.maxbelly:
			self.belly = self.maxbelly
		if self.belly < self.maxbelly * 1/5:
			self.icon = pygame.image.load("grass.png").convert()
		elif self.belly < self.maxbelly * 2/5:
			self.icon = pygame.image.load("grass20.png").convert()
		elif self.belly < self.maxbelly * 3/5:
			self.icon = pygame.image.load("grass40.png").convert()
		elif self.belly < self.maxbelly * 4/5:
			self.icon = pygame.image.load("grass60.png").convert()
		elif self.belly <= self.maxbelly:
			self.icon = pygame.image.load("grass80.png").convert()
		
		
		
class Rabbit(Animal):
	directions = ["up", "down", "left", "right"]
	def __init__(self):
		self.age = 0
		self.maxbelly = 1000
		self.belly = 800
		self.appetite = 1
		self.speed = 3
		self.icon = pygame.image.load("rabbitleft.png").convert()
		self.Rect = self.icon.get_rect()
		self.eating = False	
		self.direction = random.choice(self.directions)
		self.erraticness = 5 # chance in 1000 of changing direction
		self.fertility_chance = 200 # chance in 10,000 of giving birth
		self.pregnant = False
		self.mated = False
		self.surf = pygame.Surface((self.Rect.width, self.Rect.height))
		self.surf.set_colorkey((157, 187, 97))
				
	def update(self, grasses, rabbits, new_rabbits):
		if self.is_dead():
			rabbits.remove(self)
		self.eating = False
		self.pregnant = False
		for grass in grasses:
			if self.is_hungry() and not self.eating:
				if self.Rect.colliderect(grass.Rect):
					self.eat(grass)
					break
		self.pregnant = self.pregnancy_check()
		self.check_direction()
		self.move()
		self.pick_image()
		self.belly -= self.appetite
		self.age += 1
	def is_hungry(self):
		hunger = self.maxbelly - self.belly
		return hunger > self.maxbelly * 1/5
			
	def eat(self, grass):
		hunger = self.maxbelly - self.belly
		if grass.belly >= hunger:
			self.belly += hunger
			grass.belly -= hunger
			self.eating = True
		elif grass.belly < 5:
			pass
		else:
			self.belly += grass.belly
			grass.belly = 0
			self.eating = True
						
	def is_dead(self):
			return self.belly < 1
			
	def is_fertile(self):
		return random.randint(1, 10000) <= self.fertility_chance and self.age > 100
	def pregnancy_check(self):
		return self.is_fertile() and (not self.eating and self.belly > self.maxbelly * 4/5)
			
	def pick_image(self):
		self.icon = pygame.image.load("rabbit" + self.direction + ".png").convert()
		
class Fox(Animal):
	directions = ["up", "down", "left", "right"]
	def __init__(self):
		self.age = 0
		self.maxbelly = 1000
		self.belly = 800
		self.appetite = 2
		self.speed = 4
		self.icon = pygame.image.load("foxleft.png").convert()
		self.Rect = self.icon.get_rect()
		self.eating = False	
		self.direction = random.choice(self.directions)
		self.erraticness = 5 # chance in 1000 of changing direction
		self.fertility_chance = 25 # chance in 10,000 of getting pregnant
		self.pregnant = False
		self.mated = False
		self.surf = pygame.Surface((self.Rect.width, self.Rect.height))
		self.surf.set_colorkey((157, 187, 97))
	
	def update(self, rabbits, foxes, new_foxes):
		if self.is_dead():
			foxes.remove(self)
		self.eating = False
		self.pregnant = False
		for rabbit in rabbits:
			if self.is_hungry() and not self.eating:
				if self.Rect.colliderect(rabbit.Rect):
					self.eat(rabbit, rabbits)
					break
		self.pregnant = self.pregnancy_check()
		self.check_direction()
		self.move()
		self.pick_image()
		self.belly -= self.appetite
		self.age += 1
	def is_hungry(self):
		hunger = self.maxbelly - self.belly
		return hunger > self.maxbelly * 1/5
			
	def eat(self, rabbit, rabbits):
		self.belly += rabbit.belly
		if self.belly > self.maxbelly:
			self.belly = self.maxbelly
		self.eating = True
		rabbits.remove(rabbit)
						
	def is_dead(self):
		return self.belly < 1
			
	def is_fertile(self):
		return random.randint(1, 10000) <= self.fertility_chance and self.age > 200
	
	def pregnancy_check(self):
		return self.is_fertile() and (not self.eating and self.belly > self.maxbelly * 4/5)
				
	def pick_image(self):
		self.icon = pygame.image.load("fox" + self.direction + ".png").convert()

def intro():
	title = text32.render("Foxes vs. Rabbits", True, colors.blue)
	title_Rect = title.get_rect()
	title_Rect.midtop = (HALFWIDTH, 50)
	lines = [
		"On the next screen you can choose the initial populations of each",
		"type of object or you can place them directly during the simulation.",
		'Use the "c" key to cycle through the placeable objects',
		"(Grass, Rabbits or Foxes). Place objects with the mouse button. You",
		"can also set the minimum populations of rabbits and foxes. If they",
		"drop below the minimum, a new object of the correct type will be placed",
		"randomly. Use the Spacebar to access the graph or to return to the sim from",
		"the graph.", " ",
		"Click anywhere to continue"]
	while True:
		for event in pygame.event.get():
			if event.type == MOUSEBUTTONDOWN:
				return False
		vert = 0
		vert_space = 20
		DISPLAYSURF.fill(colors.black)
		DISPLAYSURF.blit(title, title_Rect)
		for line in lines:
			line_text = text24.render(line, True, colors.white)
			line_Rect = line_text.get_rect()
			line_Rect.midtop = (HALFWIDTH, title_Rect.bottom + 50 + vert) 
			DISPLAYSURF.blit(line_text, line_Rect)
			vert += vert_space + line_Rect.height
		pygame.display.update()
		fpsClock.tick(FPS)
		
def setup():	
	grass_uparrow = pygame.image.load("uparrow.png").convert()
	rabbit_uparrow = pygame.image.load("uparrow.png").convert()
	fox_uparrow = pygame.image.load("uparrow.png").convert()
	rabbit_min_uparrow = pygame.image.load("uparrow.png").convert()
	fox_min_uparrow = pygame.image.load("uparrow.png").convert()
	grass_downarrow = pygame.image.load("downarrow.png").convert()
	rabbit_downarrow = pygame.image.load("downarrow.png").convert()
	fox_downarrow = pygame.image.load("downarrow.png").convert()
	rabbit_min_downarrow = pygame.image.load("downarrow.png").convert()
	fox_min_downarrow = pygame.image.load("downarrow.png").convert()
	grass_uparrowRect = grass_uparrow.get_rect()
	rabbit_uparrowRect = rabbit_uparrow.get_rect()
	fox_uparrowRect = fox_uparrow.get_rect()
	rabbit_min_uparrowRect = rabbit_min_uparrow.get_rect()
	fox_min_uparrowRect = fox_min_uparrow.get_rect()
	grass_downarrowRect = grass_downarrow.get_rect()
	rabbit_downarrowRect = rabbit_downarrow.get_rect()
	fox_downarrowRect = fox_downarrow.get_rect()
	rabbit_min_downarrowRect = rabbit_min_downarrow.get_rect()
	fox_min_downarrowRect = fox_min_downarrow.get_rect()
	start = text32.render("Start", True, colors.blue, colors.gray)
	startRect = start.get_rect()
	starting_grasses = 6
	starting_rabbits = 3
	starting_foxes = 1
	rabbit_minimum = 3
	fox_minimum = 1
	while True:
		grass_num = text24.render("Grasses: %d" % starting_grasses, True, colors.white)
		rabbit_num = text24.render("Rabbits: %d" % starting_rabbits, True, colors.white)
		fox_num = text24.render("Foxes: %d" % starting_foxes, True, colors.white)
		rabbit_min = text24.render("Min. Rabbits: %d" % rabbit_minimum, True, colors.white)
		fox_min = text24.render("Min. Foxes: %d" % fox_minimum, True, colors.white)
		grass_numRect = grass_num.get_rect()
		rabbit_numRect = rabbit_num.get_rect()
		fox_numRect = fox_num.get_rect()
		rabbit_minRect = rabbit_min.get_rect()
		fox_minRect = fox_min.get_rect()
		grass_numRect.topleft = (100, 50)
		rabbit_numRect.topleft = (100, grass_numRect.bottom + 50)
		fox_numRect.topleft = (100, rabbit_numRect.bottom + 50)
		rabbit_minRect.topleft = (100, fox_numRect.bottom + 50) 
		fox_minRect.topleft = (100, rabbit_minRect.bottom + 50)
		grass_uparrowRect.topleft = (grass_numRect.right + 20, grass_numRect.top)
		rabbit_uparrowRect.topleft = (rabbit_numRect.right + 20, rabbit_numRect.top)
		fox_uparrowRect.topleft = (fox_numRect.right + 20, fox_numRect.top)
		rabbit_min_uparrowRect.topleft = (rabbit_minRect.right + 20, rabbit_minRect.top)
		fox_min_uparrowRect.topleft = (fox_minRect.right + 20, fox_minRect.top)
		grass_downarrowRect.topleft = (grass_uparrowRect.right + 20, grass_uparrowRect.top)
		rabbit_downarrowRect.topleft = (rabbit_uparrowRect.right + 20, rabbit_uparrowRect.top)
		fox_downarrowRect.topleft = (fox_uparrowRect.right + 20, fox_uparrowRect.top)
		rabbit_min_downarrowRect.topleft = (rabbit_min_uparrowRect.right + 20, rabbit_min_uparrowRect.top)
		fox_min_downarrowRect.topleft = (fox_min_uparrowRect.right + 20, fox_min_uparrowRect.top)
		startRect.center = (HALFWIDTH, fox_min_downarrowRect.bottom + 50)
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				mousex, mousey = event.pos
				if grass_uparrowRect.collidepoint(mousex, mousey):
					starting_grasses += 1
				elif rabbit_uparrowRect.collidepoint(mousex, mousey):
					starting_rabbits += 1
				elif fox_uparrowRect.collidepoint(mousex, mousey):
					starting_foxes += 1
				elif grass_downarrowRect.collidepoint(mousex, mousey):
					starting_grasses -= 1
				elif rabbit_downarrowRect.collidepoint(mousex, mousey):
					starting_rabbits -= 1
				elif fox_downarrowRect.collidepoint(mousex, mousey):
					starting_foxes -= 1
				elif rabbit_min_uparrowRect.collidepoint(mousex, mousey):
					rabbit_minimum += 1
				elif fox_min_uparrowRect.collidepoint(mousex, mousey):
					fox_minimum += 1
				elif rabbit_min_downarrowRect.collidepoint(mousex, mousey):
					rabbit_minimum -= 1
				elif fox_min_downarrowRect.collidepoint(mousex, mousey):
					fox_minimum -= 1
				elif startRect.collidepoint(mousex, mousey):
					return [starting_grasses, starting_rabbits, starting_foxes, rabbit_minimum, fox_minimum]
		blitters = [(grass_num, grass_numRect),(rabbit_num, rabbit_numRect),(fox_num, fox_numRect),
				(rabbit_min, rabbit_minRect),(fox_min, fox_minRect),(grass_uparrow, grass_uparrowRect),
				(rabbit_uparrow, rabbit_uparrowRect),(fox_uparrow, fox_uparrowRect),
				(rabbit_min_uparrow, rabbit_min_uparrowRect),(fox_min_uparrow, fox_min_uparrowRect),
				(grass_downarrow, grass_downarrowRect),(rabbit_downarrow, rabbit_downarrowRect),
				(fox_downarrow, fox_downarrowRect),(rabbit_min_downarrow, rabbit_min_downarrowRect),
				(fox_min_downarrow, fox_min_downarrowRect),(start, startRect)]
		DISPLAYSURF.fill(colors.black)
		for elem in blitters:
			DISPLAYSURF.blit(elem[0], elem[1])
		pygame.display.update()
		fpsClock.tick(FPS)
		
grass_data = []
rabbit_data = []
fox_data = []
rabbits = []
foxes = []
grasses = []
def seed_world(params):
	if params[0] > 0:
		for i in range(params[0]):
			grass = Grass()
			grass.Rect.center = (randint(50, SCREENWIDTH - 50), randint(50, SCREENHEIGHT - 50))
			grasses.append(grass)
	if params[1] > 0:
		for i in range(params[1]):
			rabbit = Rabbit()
			rabbit.Rect.center = (randint(50, SCREENWIDTH - rabbit.Rect.width / 2), randint(50, SCREENHEIGHT - 50))
			rabbits.append(rabbit)
	if params[2] > 0:
		for i in range(params[2]):
			fox = Fox()
			fox.Rect.center = (randint(50, SCREENWIDTH - 50), randint(50, SCREENHEIGHT - 50))
			foxes.append(fox)
	return params[3], params[4]

def report(grass_data, rabbit_data, fox_data):
	grass_text = text24.render("Grass", True, colors.weirdgreen)
	rabbit_text = text24.render("Rabbits", True, colors.white)
	fox_text = text24.render("Foxes", True, colors.orange)
	grass_text_rect = grass_text.get_rect()
	rabbit_text_rect = rabbit_text.get_rect()
	fox_text_rect = fox_text.get_rect()
	grass_text_rect.topleft = (50, SCREENHEIGHT - 50)
	rabbit_text_rect.topleft = (grass_text_rect.right + 50, SCREENHEIGHT - 50)
	fox_text_rect.topleft = (rabbit_text_rect.right + 50, SCREENHEIGHT - 50)
	
	mousex = 0
	mousey = 0
	point_offset = 0 
	data_length = len(grass_data) + len(rabbit_data) + len(fox_data)
	if (data_length/3) * 5 > SCREENWIDTH:
		point_offset += (data_length/3) * 5 - SCREENWIDTH
	for point in grass_data:
		point.x -= point_offset 
	for point in rabbit_data:
		point.x -= point_offset 
	for point in fox_data:
		point.x -= point_offset 
	for rect in [grass_text_rect, rabbit_text_rect, fox_text_rect]:
		rect.centerx -= point_offset
	while True:
		for event in  pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_SPACE:
					for point in grass_data:
						point.x += point_offset
					for point in rabbit_data:
						point.x += point_offset
					for point in fox_data:
						point.x += point_offset
					for rect in [grass_text_rect, rabbit_text_rect, fox_text_rect]:
						rect.centerx += point_offset
					return False
		mousex, mousey = pygame.mouse.get_pos()
		if mousex > SCREENWIDTH - 50:
			for point in grass_data:
				point.x -= 5
			for point in rabbit_data:
				point.x -= 5
			for point in fox_data:
				point.x -= 5
			for rect in [grass_text_rect, rabbit_text_rect, fox_text_rect]:
				rect.centerx -= 5
			point_offset += 5
		elif mousex < 50:
			for point in grass_data:
				point.x += 5
			for point in rabbit_data:
				point.x += 5
			for point in fox_data:
				point.x += 5
			for rect in [grass_text_rect, rabbit_text_rect, fox_text_rect]:
				rect.centerx += 5
			point_offset -= 5	
		
		DISPLAYSURF.fill(colors.black)
		pygame.draw.lines(DISPLAYSURF, colors.white, False, [(point.x, point.y) for point in rabbit_data], 5)
		pygame.draw.lines(DISPLAYSURF, colors.weirdgreen, False, [(point.x, point.y) for point in grass_data], 5)	
		pygame.draw.lines(DISPLAYSURF, colors.orange, False, [(point.x, point.y) for point in fox_data], 5)
		DISPLAYSURF.blit(grass_text, grass_text_rect)
		DISPLAYSURF.blit(rabbit_text, rabbit_text_rect)
		DISPLAYSURF.blit(fox_text, fox_text_rect)
		pygame.display.update()
		fpsClock.tick(FPS)
	
	
def main((rabbit_minimum, fox_minimum)):
	object_names = ["Grass", "Rabbit", "Fox"]
	current_objects = itertools.cycle(object_names)
	loop_count = 0
	current_object = next(current_objects)
	while True:
		current_object_text = text16.render("<C>urrent object: %s" % current_object, True, colors.black)
		current_object_Rect = current_object_text.get_rect()
		current_object_Rect.bottomleft = (0, SCREENHEIGHT)
		new_rabbits = []
		new_foxes = []
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_SPACE:
					report(grass_data, rabbit_data, fox_data)
				elif event.key == K_c:
					current_object = next(current_objects)
			elif event.type == MOUSEBUTTONDOWN:
				x, y = event.pos
				if current_object == "Grass":
					grass = Grass()
					grass.Rect.center = (x,y)
					grasses.append(grass)
				elif current_object == "Rabbit":
					rabbit = Rabbit()
					rabbit.Rect.center = (x, y)
					rabbits.append(rabbit)
				elif current_object == "Fox":
					fox = Fox()
					fox.Rect.center = (x, y)
					foxes.append(fox)
		
		for grass in grasses:
			grass.update()
		
		for rabbit in  rabbits:
			rabbit.update(grasses, rabbits, new_rabbits)
			if rabbit.pregnant:
				new_rabbit = Rabbit()
				new_rabbit.Rect.center = (rabbit.Rect.centerx, rabbit.Rect.centery - rabbit.Rect.height)
				new_rabbits.append(new_rabbit)
		for rabbit in new_rabbits:
			rabbits.append(new_rabbit)
		new_rabbits = []	
		
		for fox in foxes:
			fox.update(rabbits, foxes, new_foxes)
			if fox.pregnant:
				new_fox = Fox()
				new_fox.Rect.center = (fox.Rect.centerx, fox.Rect.centery - fox.Rect.height)
				new_foxes.append(new_fox)
		for fox in new_foxes:
			foxes.append(fox)
		new_foxes = []
		if loop_count % FPS == 0:				# grab data once per second for graph
			total_grass = 0
			for grass in grasses:
				total_grass += grass.belly
			point = Point((loop_count / FPS) * 5, 600 - (total_grass / 10), colors.weirdgreen)
			point1 = Point((loop_count / FPS) * 5, 600 - len(rabbits * 3), colors.white)
			point2 = Point((loop_count / FPS) * 5, 600 - len(foxes * 5), colors.orange)
			grass_data.append(point)
			rabbit_data.append(point1)
			fox_data.append(point2)
			
		loop_count += 1
		if len(rabbits) < rabbit_minimum:
			rabbit = Rabbit()
			rabbits.append(rabbit)
		if len(foxes) < fox_minimum:
			fox = Fox()
			foxes.append(fox)		
		SURF.fill(colors.weirdgreen)
		for grass in grasses:
			SURF.blit(grass.icon, grass.Rect)
		for rabbit in rabbits:
			rabbit.surf.blit(rabbit.icon, (0, 0))
			SURF.blit(rabbit.surf, rabbit.Rect)
		for fox in foxes:
			fox.surf.blit(fox.icon, (0, 0))
			SURF.blit(fox.surf, fox.Rect)
		SURF.blit(current_object_text, current_object_Rect)
		DISPLAYSURF.blit(SURF, (0, 0))
		pygame.display.update()
		fpsClock.tick(FPS)

intro()
main(seed_world(setup()))		

