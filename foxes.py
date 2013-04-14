import os
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
pygame.display.set_caption("Foxes vs. Rabbits vs. Grass")
FPS = 30
fpsClock = pygame.time.Clock()
SCREENWIDTH = 1080
SCREENHEIGHT = 740


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
			if self.rect.top < self.rect.height / 2:
				self.direction = "down"
				self.rect.centery += self.speed
			else:
				self.rect.centery -= self.speed
		elif self.direction == "down":
			if self.rect.bottom > SCREENHEIGHT - (self.rect.height / 2):
				self.direction = "up"
				self.rect.centery -= self.speed
			else:
				self.rect.centery += self.speed
		elif self.direction == "left":
			if self.rect.left < self.rect.width / 2:
				self.direction = "right"
				self.rect.centerx += self.speed
			else:
				self.rect.centerx -= self.speed
		elif self.direction == "right":
			if self.rect.right > SCREENWIDTH - self.rect.width / 2:
				self.direction = "left"
				self.rect.centerx -= self.speed
			else:
				self.rect.centerx += self.speed
				
class Grass(object):
	def __init__(self):
		self.maxbelly = 500
		self.belly = 500
		self.icon = pygame.image.load(os.path.join("Art", "grass.png")).convert()
		self.rect = self.icon.get_rect()
		self.growth_rate = 2
	
	def update(self):
		if self.belly < self.maxbelly: 
			self.belly += self.growth_rate
		if self.belly > self.maxbelly:
			self.belly = self.maxbelly
		if self.belly < self.maxbelly * 1/5:
			self.icon = pygame.image.load(os.path.join("Art", "grass20.png")).convert()
		elif self.belly < self.maxbelly * 2/5:
			self.icon = pygame.image.load(os.path.join("Art", "grass40.png")).convert()
		elif self.belly < self.maxbelly * 3/5:
			self.icon = pygame.image.load(os.path.join("Art", "grass60.png")).convert()
		elif self.belly < self.maxbelly * 4/5:
			self.icon = pygame.image.load(os.path.join("Art", "grass80.png")).convert()
		else:
			self.icon = pygame.image.load(os.path.join("Art", "grass.png")).convert()
		
		
		
class Rabbit(Animal):
	directions = ["up", "down", "left", "right"]
	def __init__(self):
		self.age = 0
		self.maxbelly = 1000
		self.belly = 800
		self.appetite = 1
		self.speed = 3
		self.icon = pygame.image.load(os.path.join("Art", "rabbitleft.png")).convert()
		self.rect = self.icon.get_rect()
		self.eating = False	
		self.direction = random.choice(self.directions)
		self.erraticness = 5 # chance in 1000 of changing direction
		self.fertility_chance = 200 # chance in 10,000 of being fertile
		self.pregnant = False
		self.mated = False
		self.surf = pygame.Surface((self.rect.width, self.rect.height))
		self.surf.set_colorkey((157, 187, 97))
				
	def update(self, grasses, rabbits, new_rabbits):
		if self.is_dead():
			rabbits.remove(self)
		self.eating = False
		self.pregnant = False
		for grass in grasses:
			if self.is_hungry() and not self.eating:
				if self.rect.colliderect(grass.rect):
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
		self.icon = pygame.image.load(os.path.join("Art", "rabbit" + self.direction + ".png")).convert()
		
class Fox(Animal):
	directions = ["up", "down", "left", "right"]
	def __init__(self):
		self.age = 0
		self.maxbelly = 1000
		self.belly = 800
		self.appetite = 2
		self.speed = 4
		self.icon = pygame.image.load(os.path.join("Art", "foxleft.png")).convert()
		self.rect = self.icon.get_rect()
		self.eating = False	
		self.direction = random.choice(self.directions)
		self.erraticness = 5 # chance in 1000 of changing direction
		self.fertility_chance = 25 # chance in 10,000 of being fertile
		self.pregnant = False
		self.mated = False
		self.surf = pygame.Surface((self.rect.width, self.rect.height))
		self.surf.set_colorkey((157, 187, 97))
	
	def update(self, rabbits, foxes, new_foxes):
		if self.is_dead():
			foxes.remove(self)
		self.eating = False
		self.pregnant = False
		for rabbit in rabbits:
			if self.is_hungry() and not self.eating:
				if self.rect.colliderect(rabbit.rect):
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
		self.icon = pygame.image.load(os.path.join("Art", "fox" + self.direction + ".png")).convert()

def intro():
	title = text32.render("Foxes vs. Rabbits", True, colors.blue)
	title_rect = title.get_rect()
	title_rect.midtop = (SCREENWIDTH/2, 50)
	lines = ["On the next screen you can choose the initial populations of each",
		"type of object or you can place them directly during the simulation.",
		'Use the "c" key to cycle through the placeable objects',
		"(Grass, Rabbits or Foxes). Place objects with the mouse button. You",
		"can also set the minimum populations of rabbits and foxes. If they",
		"drop below the minimum, a new object of the correct type will be placed",
		"randomly. Use the Spacebar to access the graph or to return to the sim from",
		"the graph.", " ", "Click anywhere to continue"]
	while True:
		for event in pygame.event.get():
			if event.type == MOUSEBUTTONDOWN:
				return False
		vert = 0
		vert_space = 20
		DISPLAYSURF.fill(colors.black)
		DISPLAYSURF.blit(title, title_rect)
		for line in lines:
			line_text = text24.render(line, True, colors.white)
			line_rect = line_text.get_rect()
			line_rect.midtop = (SCREENWIDTH/2, title_rect.bottom + 50 + vert) 
			DISPLAYSURF.blit(line_text, line_rect)
			vert += vert_space + line_rect.height
		pygame.display.update()
		fpsClock.tick(FPS)
		
def setup():	
	grass_uparrow = pygame.image.load(os.path.join("Art", "uparrow.png")).convert()
	rabbit_uparrow = pygame.image.load(os.path.join("Art", "uparrow.png")).convert()
	fox_uparrow = pygame.image.load(os.path.join("Art", "uparrow.png")).convert()
	rabbit_min_uparrow = pygame.image.load(os.path.join("Art", "uparrow.png")).convert()
	fox_min_uparrow = pygame.image.load(os.path.join("Art", "uparrow.png")).convert()
	grass_downarrow = pygame.image.load(os.path.join("Art", "downarrow.png")).convert()
	rabbit_downarrow = pygame.image.load(os.path.join("Art", "downarrow.png")).convert()
	fox_downarrow = pygame.image.load(os.path.join("Art", "downarrow.png")).convert()
	rabbit_min_downarrow = pygame.image.load(os.path.join("Art", "downarrow.png")).convert()
	fox_min_downarrow = pygame.image.load(os.path.join("Art", "downarrow.png")).convert()
	start = text32.render("Start", True, colors.blue, colors.gray)
	
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
		grass_numrect = grass_num.get_rect(topleft = (100, 50))
		rabbit_numrect = rabbit_num.get_rect(topleft = (100, grass_numrect.bottom + 50))
		fox_numrect = fox_num.get_rect(topleft = (100, rabbit_numrect.bottom + 50))
		rabbit_minrect = rabbit_min.get_rect(topleft = (100, fox_numrect.bottom + 50))
		fox_minrect = fox_min.get_rect(topleft = (100, rabbit_minrect.bottom + 50))
		grass_uparrowrect = grass_uparrow.get_rect(topleft = (grass_numrect.right + 20, grass_numrect.top))
		rabbit_uparrowrect = rabbit_uparrow.get_rect(topleft = (rabbit_numrect.right + 20, rabbit_numrect.top))
		fox_uparrowrect = fox_uparrow.get_rect(topleft = (fox_numrect.right + 20, fox_numrect.top))
		rabbit_min_uparrowrect = rabbit_min_uparrow.get_rect(topleft = (rabbit_minrect.right + 20, rabbit_minrect.top))
		fox_min_uparrowrect = fox_min_uparrow.get_rect(topleft = (fox_minrect.right + 20, fox_minrect.top))
		grass_downarrowrect = grass_downarrow.get_rect(topleft = (grass_uparrowrect.right + 20, grass_uparrowrect.top))
		rabbit_downarrowrect = rabbit_downarrow.get_rect(topleft = (rabbit_uparrowrect.right + 20, rabbit_uparrowrect.top))
		fox_downarrowrect = fox_downarrow.get_rect(topleft = (fox_uparrowrect.right + 20, fox_uparrowrect.top))
		rabbit_min_downarrowrect = rabbit_min_downarrow.get_rect(topleft = (rabbit_min_uparrowrect.right + 20,
																			rabbit_min_uparrowrect.top))
		fox_min_downarrowrect = fox_min_downarrow.get_rect(topleft = (fox_min_uparrowrect.right + 20, fox_min_uparrowrect.top))
		startrect = start.get_rect(center = (SCREENWIDTH/2, fox_min_downarrowrect.bottom + 50))
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				mousex, mousey = event.pos				
				if grass_uparrowrect.collidepoint(mousex, mousey):
					starting_grasses += 1
				elif rabbit_uparrowrect.collidepoint(mousex, mousey):
					starting_rabbits += 1
				elif fox_uparrowrect.collidepoint(mousex, mousey):
					starting_foxes += 1
				elif grass_downarrowrect.collidepoint(mousex, mousey):
					starting_grasses -= 1
				elif rabbit_downarrowrect.collidepoint(mousex, mousey):
					starting_rabbits -= 1
				elif fox_downarrowrect.collidepoint(mousex, mousey):
					starting_foxes -= 1
				elif rabbit_min_uparrowrect.collidepoint(mousex, mousey):
					rabbit_minimum += 1
				elif fox_min_uparrowrect.collidepoint(mousex, mousey):
					fox_minimum += 1
				elif rabbit_min_downarrowrect.collidepoint(mousex, mousey):
					rabbit_minimum -= 1
				elif fox_min_downarrowrect.collidepoint(mousex, mousey):
					fox_minimum -= 1
				elif startrect.collidepoint(mousex, mousey):
					return [starting_grasses, starting_rabbits, starting_foxes, rabbit_minimum, fox_minimum]
		blitters = [(grass_num, grass_numrect),(rabbit_num, rabbit_numrect),(fox_num, fox_numrect),
				(rabbit_min, rabbit_minrect),(fox_min, fox_minrect),(grass_uparrow, grass_uparrowrect),
				(rabbit_uparrow, rabbit_uparrowrect),(fox_uparrow, fox_uparrowrect),
				(rabbit_min_uparrow, rabbit_min_uparrowrect),(fox_min_uparrow, fox_min_uparrowrect),
				(grass_downarrow, grass_downarrowrect),(rabbit_downarrow, rabbit_downarrowrect),
				(fox_downarrow, fox_downarrowrect),(rabbit_min_downarrow, rabbit_min_downarrowrect),
				(fox_min_downarrow, fox_min_downarrowrect),(start, startrect)]
		DISPLAYSURF.fill(colors.black)
		for elem in blitters:
			DISPLAYSURF.blit(elem[0], elem[1])
		pygame.display.update()
		fpsClock.tick(FPS)

def seed_world(params):
	rabbits = []
	foxes = []
	grasses = []
	if params[0] > 0:
		for i in range(params[0]):
			grass = Grass()
			grass.rect.center = (randint(50, SCREENWIDTH - 50), randint(50, SCREENHEIGHT - 50))
			grasses.append(grass)
	if params[1] > 0:
		for i in range(params[1]):
			rabbit = Rabbit()
			rabbit.rect.center = (randint(50, SCREENWIDTH - rabbit.rect.width / 2), randint(50, SCREENHEIGHT - 50))
			rabbits.append(rabbit)
	if params[2] > 0:
		for i in range(params[2]):
			fox = Fox()
			fox.rect.center = (randint(50, SCREENWIDTH - 50), randint(50, SCREENHEIGHT - 50))
			foxes.append(fox)
	return params[3], params[4], rabbits, foxes, grasses

def report(grass_data, rabbit_data, fox_data):
	grass_text = text24.render("Grass", True, colors.weirdgreen, colors.black)
	rabbit_text = text24.render("Rabbits", True, colors.white, colors.black)
	fox_text = text24.render("Foxes", True, colors.orange, colors.black)
	grass_text_rect = grass_text.get_rect(topleft = (50, SCREENHEIGHT - 100))
	rabbit_text_rect = rabbit_text.get_rect(topleft = (grass_text_rect.right + 50, grass_text_rect.top))
	fox_text_rect = fox_text.get_rect(topleft = (rabbit_text_rect.right + 50, grass_text_rect.top))
	exit = text24.render("<SPACE> to exit", True, colors.white, colors.black)
	exit_rect = exit.get_rect(midbottom = (SCREENWIDTH/2, SCREENHEIGHT))
	instruct = text24.render("Use arrow keys to expand/compress the graph", True, colors.gray, colors.black)
	instruct_rect = instruct.get_rect(midbottom = (SCREENWIDTH/2, exit_rect.top - 20))
	mousex = 0
	mousey = 0
	xscale = 5
	yscale = 1
	base = 600
	while len(grass_data) * xscale > SCREENWIDTH:
		xscale -= .5
	expandingx = False
	expandingy = False
	compressingx = False
	compressingy = False
	while True:
		for event in  pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:
				if event.key == K_SPACE:
					return False
				elif event.key == K_RIGHT:
					expandingx = True
				elif event.key == K_UP:
					expandingy = True
				elif event.key == K_LEFT:
					compressingx = True
				elif event.key == K_DOWN:
					compressingy = True
			elif event.type == KEYUP:
				if event.key == K_RIGHT:
					expandingx = False
				elif event.key == K_UP:
					expandingy = False
				elif event.key == K_LEFT:
					compressingx = False
				elif event.key == K_DOWN:
					compressingy = False
		if expandingx:
			xscale += .2
		elif expandingy:
			yscale += .2
		elif compressingx and xscale > 0:
			xscale -= .2
		elif compressingy and yscale > 1:
			yscale -= .2
		
		DISPLAYSURF.fill(colors.black)
		pygame.draw.lines(DISPLAYSURF, colors.weirdgreen, False,
				[(point.x * xscale, base - point.y * yscale) for point in grass_data], 5)
		pygame.draw.lines(DISPLAYSURF, colors.white, False,
				[(point.x * xscale, base - point.y * yscale) for point in rabbit_data], 5)
		pygame.draw.lines(DISPLAYSURF, colors.orange, False,
				[(point.x * xscale, base - point.y * yscale) for point in fox_data], 5)
		for item in [(grass_text, grass_text_rect),(rabbit_text, rabbit_text_rect),
					(fox_text, fox_text_rect),(exit, exit_rect), (instruct, instruct_rect)]:
			DISPLAYSURF.blit(item[0], item[1])
		pygame.display.update()
		fpsClock.tick(FPS)

def sim((rabbit_minimum, fox_minimum, rabbits, foxes, grasses)):
	grass_data = []
	rabbit_data = []
	fox_data = []
	object_names = ["Grass", "Rabbit", "Fox"]
	current_objects = itertools.cycle(object_names)
	current_object = next(current_objects)
	loop_count = 0
	while True:
		#start = time.time()
		current_object_text = text16.render("<C>urrent object: %s     <SPACE> for graph" % current_object,
					True, colors.black)
		current_object_rect = current_object_text.get_rect(bottomleft = (0, SCREENHEIGHT))
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
					grass.rect.center = (x,y)
					grasses.append(grass)
				elif current_object == "Rabbit":
					rabbit = Rabbit()
					rabbit.rect.center = (x, y)
					rabbits.append(rabbit)
				elif current_object == "Fox":
					fox = Fox()
					fox.rect.center = (x, y)
					foxes.append(fox)

		for grass in grasses:
			grass.update()

		for rabbit in  rabbits:
			rabbit.update(grasses, rabbits, new_rabbits)
			if rabbit.pregnant:
				new_rabbit = Rabbit()
				new_rabbit.rect.center = (rabbit.rect.centerx, rabbit.rect.centery - rabbit.rect.height)
				new_rabbits.append(new_rabbit)
		for rabbit in new_rabbits:
			rabbits.append(new_rabbit)
		new_rabbits = []

		for fox in foxes:
			fox.update(rabbits, foxes, new_foxes)
			if fox.pregnant:
				new_fox = Fox()
				new_fox.rect.center = (fox.rect.centerx, fox.rect.centery - fox.rect.height)
				new_foxes.append(new_fox)
		for fox in new_foxes:
			foxes.append(fox)
		new_foxes = []
		
		if loop_count % FPS == 0:				# grab data once per second for graph
			total_grass = 0
			for grass in grasses:
				total_grass += grass.belly
			point = Point((loop_count / FPS), (total_grass / 10), colors.weirdgreen)
			point1 = Point((loop_count / FPS), len(rabbits * 3), colors.white)
			point2 = Point((loop_count / FPS), len(foxes * 5), colors.orange)
			grass_data.append(point)
			rabbit_data.append(point1)
			fox_data.append(point2)
		loop_count += 1

		if len(rabbits) < rabbit_minimum:
			additional_rabbit = Rabbit()
			rabbits.append(additional_rabbit)
		if len(foxes) < fox_minimum:
			additional_fox = Fox()
			foxes.append(additional_fox)
		
		SURF.fill(colors.weirdgreen)
		for grass in grasses:
			SURF.blit(grass.icon, grass.rect)
		for rabbit in rabbits:
			rabbit.surf.blit(rabbit.icon, (0, 0))
			SURF.blit(rabbit.surf, rabbit.rect)
		for fox in foxes:
			fox.surf.blit(fox.icon, (0, 0))
			SURF.blit(fox.surf, fox.rect)
		SURF.blit(current_object_text, current_object_rect)
		DISPLAYSURF.blit(SURF, (0, 0))
		pygame.display.update()
		fpsClock.tick(FPS)
		#now = time.time()
		#print now - start
intro()
sim(seed_world(setup()))

