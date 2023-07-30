import math
import random
import sys
import os
from functools import partial

import neat
import pygame

# Window Size
WIDTH = 1920
HEIGHT = 1080

# Car Size
CAR_SIZE_X = 64    
CAR_SIZE_Y = 64

BORDER_COLOR = (255, 255, 255, 255) # Color To Detect Crash (White)

current_generation = 0 # Generation counter

Maps = {
    'map_0.png': 'Map 0',
    'map_1.png': 'Map 1',
    'map_2.png': 'Map 2',
    'map_3.png': 'Map 3',
    'map_4.png': 'Map 4',
    'map_5.png': 'Map 5',
    'map_6.png': 'Map 6'
}

# Store the selected map as a global variable
selected_map = None

class Car:

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        self.position = [830, 920] # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False # Flag For Default Speed

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] # Center

        self.radars = [] # List For Radars
        self.drawing_radars = [] # Radars To Be Drawn

        self.alive = True # Bool To Check If Car is Crashed or Not

        self.distance = 0 # Distance Driven
        self.time = 0 # Time Passed

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)
        self.draw_radar(screen)

    def draw_radar(self, screen):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length) # x = r * cos(theta)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length) # y = r * sin(theta)

        # While We Don't Crash -> Move Forward
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    
    def update(self, game_map):
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 15px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 15)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1
        
        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate Four Corners using Trignometry
        length = 0.5 * CAR_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        return self.alive

    def get_reward(self):
        return self.distance / (CAR_SIZE_X / 2)

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image

# Add a menu screen to select the map
def select_map(screen):
    selected_index = 0

    font = pygame.font.SysFont("Arial", 40)
    options = list(Maps.values())
    option_height = 50
    option_start_y = (HEIGHT - len(options) * option_height) // 2

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return list(Maps.keys())[selected_index]

                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)

        screen.fill((0, 0, 0))

        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_index else (128, 128, 128)
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, option_start_y + i * option_height))
            screen.blit(text, text_rect)

        pygame.display.flip()

def run_simulation(genomes, config):
    
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN, pygame.SRCALPHA)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings, Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load(selected_map).convert()
    global current_generation
    current_generation += 1

    # Simple Counter To Limit Time
    counter = 0

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10 # Left
            elif choice == 1:
                car.angle -= 10 # Right
            elif choice == 2:
                if(car.speed - 2 >= 12):
                    car.speed -= 2 # Slow Down
            else:
                car.speed += 2 # Speed Up
        
        # Check If Car Is Still Alive -> If Yes Increase Fitness  |  If Not Break Loop
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40: # Stop the Generation's Run
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)
        
        # best_genome = stats.best_genome()
        # best_fitness = best_genome.fitness
        # avg_fitness = stats.get_fitness_mean()
        # num_generations = current_generation

        # Display Info
        # text = generation_font.render("Generation: " + str(current_generation), True, (0,0,0))
        # text_rect = text.get_rect()
        # text_rect.center = (900, 450)
        # screen.blit(text, text_rect)

        # text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        # text_rect = text.get_rect()
        # text_rect.center = (900, 490)
        # screen.blit(text, text_rect)

        # text = alive_font.render("Best Fitness: {:.2f}".format(best_fitness), True, (0, 0, 0))
        # text_rect = text.get_rect()
        # text_rect.center = (900, 530)
        # screen.blit(text, text_rect)

        # text = alive_font.render("Average Fitness: {:.2f}".format(avg_fitness), True, (0, 0, 0))
        # text_rect = text.get_rect()
        # text_rect.center = (900, 570)
        # screen.blit(text, text_rect)

        generation_text = generation_font.render("Generation: " + str(current_generation), True, (0, 0, 0))
        alive_text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))

        # Create a white background surface
        info_background = pygame.Surface((300, 100))
        info_background.fill((255, 255, 255))

        # Blit the text surfaces onto the background
        info_background.blit(generation_text, (10, 10))
        info_background.blit(alive_text, (10, 40))

        # Blit the background surface on the screen (top-left corner)
        screen.blit(info_background, (10, 10))

        pygame.display.flip()
        clock.tick(30) # 30 FPS

if __name__ == "__main__":

    # Add menu to select the map
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Car Simulation - Select Map")

    selected_map = select_map(screen)

    pygame.display.set_caption("Car Simulation - " + Maps[selected_map])
    
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)

    # Run Simulation For A Maximum of 1000 Generations
    # population.run(lambda genomes, config: run_simulation(selected_map, genomes, config), 1000)
