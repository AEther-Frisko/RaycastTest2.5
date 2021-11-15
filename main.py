#11/03/21
#Attempting to make one that doesn't show the map.

#11/15/21 - Turned map into seperate txt file for multi-map compatibility!

#package imports
import pygame
import math
import sys

#global constants
SCREEN_HEIGHT = 480
SCREEN_WIDTH = SCREEN_HEIGHT * 2
MAP_SIZE = 16
TILE_SIZE = int((SCREEN_WIDTH / 2) / MAP_SIZE)
MAX_DEPTH = int(MAP_SIZE * TILE_SIZE)
FOV = math.pi / 3
HALF_FOV = FOV / 2
CASTED_RAYS = 120
STEP_ANGLE = FOV / CASTED_RAYS
SCALE = SCREEN_WIDTH / CASTED_RAYS

#Colours
RED = (255, 0, 0)
GREEN = (0, 255, 0)
L_GREY = (200, 200, 200)
GREY = (100, 100, 100)
BLACK = (0, 0, 0)
WHITE = (255,255,255)
YELLOW = (255,255,0)
SKY = (145, 203, 230)
FLOOR = (30, 26, 61)

#global variables
playerX = (SCREEN_WIDTH / 2) / 2
playerY = (SCREEN_WIDTH / 2) / 2
playerAngle = math.pi

#accesses map
mapFile = "map1.txt"
fileIn = open(mapFile, "r")
level = ""

#turns map into string and then closes the file
for x in range (MAP_SIZE):
  line = fileIn.readline()
  line = str(line.replace("\n", ""))
  level = str(level + line)
fileIn.close()

#starts up pygame
pygame.init()

#creates game window and caption
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Raycast Test")

#timer start up
clock = pygame.time.Clock()

#raycast algorithm
def castRays():
  #leftmost angle of FOV
  startAngle = playerAngle - HALF_FOV
  #loop over casted rays
  for ray in range(CASTED_RAYS):
    #cast ray step by step
    for depth in range(MAX_DEPTH):
      #get ray target coords
      targetX = playerX - math.sin(startAngle) * depth
      targetY = playerY + math.cos(startAngle) * depth

      #convert target x, y coord to map col, row
      col = int(targetX / TILE_SIZE)
      row = int(targetY / TILE_SIZE)

      #calculate map square index
      square = row * MAP_SIZE + col
      if level[square] == "1":

        #wall shading
        colour = (126 / (1 + depth * depth * 0.0001), 78 / (1 + depth * depth * 0.0001), 245 / (1 + depth * depth * 0.0001))
        #255 / (1 + depth * depth * 0.0001) <-- original

        #fix fish eye
        depth *= math.cos(playerAngle - startAngle)

        #calculate wall height
        wallHeight = 21000 / (depth + 0.0001)

        #fix stuck at wall
        if wallHeight > SCREEN_HEIGHT:
          wallHeight = SCREEN_HEIGHT

        #draw 3D projection (rectangle by rectangle)
        pygame.draw.rect(screen, colour,
        [ray * SCALE,
        (SCREEN_HEIGHT / 2) - wallHeight / 2,
        SCALE, wallHeight])
        
        break

    #increment angle by one step
    startAngle += STEP_ANGLE

#movement direction
forward = True

#game loop
while True:
  #quit condition
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit(0)

  #convert target x, y coord to map col, row
  col = int(playerX / TILE_SIZE)
  row = int(playerY / TILE_SIZE)

  #calculate map square index
  square = row * MAP_SIZE + col

  #player hits wall (collision detection)
  if level[square] == "1":
    if forward:
      playerX -= -math.sin(playerAngle) * 5
      playerY -= math.cos(playerAngle) * 5
    else:
      playerX += -math.sin(playerAngle) * 5
      playerY += math.cos(playerAngle) * 5

  #update 2D background
  #pygame.draw.rect(screen, BLACK, (0,0,SCREEN_HEIGHT,SCREEN_HEIGHT))

  #update 3D background
  pygame.draw.rect(screen, FLOOR, [0,SCREEN_HEIGHT/2,SCREEN_WIDTH,SCREEN_HEIGHT])
  pygame.draw.rect(screen, SKY, [0,0,SCREEN_WIDTH, SCREEN_HEIGHT/2])

  #draw 2D map
  #draw_map()

  #apply raycasting
  castRays()

  #get user input
  keys = pygame.key.get_pressed()

  #handle user input
  if keys[pygame.K_LEFT]: playerAngle -= 0.1
  if keys[pygame.K_RIGHT]: playerAngle += 0.1
  if keys[pygame.K_UP]:
    forward = True
    playerX += -math.sin(playerAngle) * 5
    playerY += math.cos(playerAngle) * 5
  if keys[pygame.K_DOWN]:
    forward = False
    playerX -= -math.sin(playerAngle) * 5
    playerY -= math.cos(playerAngle) * 5

  #set FPS
  clock.tick(30)

  #show FPS
  fps = str(int(clock.get_fps()))
  font = pygame.font.SysFont('Monospace Regular', 30)
  fpsSurface = font.render(fps, False, WHITE)
  screen.blit(fpsSurface, (SCREEN_WIDTH / 2, 0))

  #update display
  pygame.display.flip()