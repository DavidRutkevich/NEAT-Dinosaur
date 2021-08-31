import random
import math
import pygame
import os, sys
import neat

pygame.init()

# Screen
HEIGHT = 650
WIDTH = 1000
BGCOLOR = (18, 18, 18 )
FPS = 30
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)

# IMAGES
RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]

JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))


BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

FONT = pygame.font.Font('Assets/PressStart2P-Regular.ttf', 20)


class Dinosaur:
    X = 80
    Y = 310
    JUMP_VEL = 8.5

    def __init__(self, image=RUNNING[0]):
        self.image = image

        self.sprite_run = True
        self.sprite_jump = False

        
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(self.X, self.Y, image.get_width(), image.get_height())
        self.step_idx = 0

    def update(self):
        if self.sprite_run:
            self.run()
        if self.sprite_jump:
            self.jump()
        if self.step_idx >= 10:
            self.step_idx = 0

        
    def run(self):
        self.image = RUNNING[self.step_idx // 5]
        self.rect.x = self.X
        self.rect.y = self.Y
        self.step_idx += 1

    def jump(self):
        self.image = JUMPING
        if self.sprite_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL:
            self.sprite_jump = False
            self.sprite_run = True
            self.jump_vel = self.JUMP_VEL


    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Cloud:

    def __init__(self):
        self.x = WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = WIDTH + random.randint(1500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))



class Obstacle:
    def __init__(self, image, number_of_cacti):
        self.image = image
        self.type = number_of_cacti
        self.rect = self.image[self.type].get_rect()
        self.rect.x = WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image, num_cactus):
        super().__init__(image, num_cactus)
        self.rect.y = 340
        
class LargeCactus(Obstacle):
    def __init__(self, image, num_cactus):
        super().__init__(image, num_cactus)
        self.rect.y = 318
        

def remove(index):
    dinosaurs.pop(index)
    gen.pop(index)
    nets.pop(index)

def distance(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.sqrt(dx **2 + dy ** 2)



def eval_genomes(genomes, config):
    global game_speed, x_bg, y_bg, score, obstacles, gen, nets, dinosaurs
    score = 0
    x_bg = 0
    y_bg = 400
    game_speed = 20


    clock = pygame.time.Clock()
    
    
    dinosaurs = []
    cloud = Cloud()
    obstacles = []
    gen = []
    nets = []
    
    for gen_id, genome  in genomes:
        dinosaurs.append(Dinosaur())
        gen.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
        
    
    def score_draw():
        global score, game_speed
        score += 1

        if score % 100 == 0:
            game_speed += 10

        text = FONT.render(f"Score:{str(score)}", False, (236, 239, 244))
        screen.blit(text, (700, 50))

    def background():
        global x_bg, y_bg
        img_width = BG.get_width()
        screen.blit(BG, (x_bg, y_bg))
        screen.blit(BG, (img_width + x_bg, y_bg))
        if x_bg <= img_width * -1:
            x_bg = 0
        x_bg -= game_speed
        
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # if event.key == pygame.K_SPACE:
                #     dinosaur.sprite_jump = True
                #     dinosaur.sprite_run = False

        screen.fill((18, 18, 18))

        for dinosaur in dinosaurs:
            dinosaur.update()
            dinosaur.draw()

        if len(dinosaurs) == 0:
            break
        
        if len(obstacles) == 0:
            random_integer = random.randint(0, 2)
            if random_integer  == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS, random.randint(0, 2)))
            elif random_integer == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS, random.randint(0, 2)))

                
                
        for obstacle in obstacles:
            obstacle.draw(screen)
            obstacle.update()
            for i, dinosaur in enumerate(dinosaurs):
                if dinosaur.rect.colliderect(obstacle.rect):
                    gen[i].fitness -= 1
                    remove(i)
        # key_input = pygame.key.get_pressed()

        for i, dinosaur in enumerate(dinosaurs):
            output = nets[i].activate((dinosaur.rect.y,
                                        distance((dinosaur.rect.x, dinosaur.rect.y),
                                        obstacle.rect.midtop)))
            
            
            if output[0] > 0.5 and dinosaur.rect.y == dinosaur.Y:
                dinosaur.sprite_jump = True
                dinosaur.sprite_run = False
                dinosaur.sprite_duck = False
        cloud.draw(screen)
        cloud.update()

        score_draw()
        background()
        clock.tick(FPS)
        pygame.display.update()


def run(conf_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        conf_path
    )
    
    population  = neat.Population(config)
    population.run(eval_genomes, 50)

if __name__ == '__main__':
    local_directory = os.path.dirname(__file__)
    config_path = os.path.join(local_directory, "config.txt")
    run(config_path)
