#01/05/22
#enemy pathing implement and indication (eg. an overlay on the screen to show it's close)
#01/11/22
#adding health/death
#01/12/22
#game over functionality

#package imports
import pygame
import math
import sys
import random

#global constants
SCREEN_HEIGHT = 480
SCREEN_WIDTH = SCREEN_HEIGHT * 2
MAP_SIZE = 8
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
SKY = (66, 70, 70)
FLOOR = (15, 20, 20)

#global variables
playerX = (SCREEN_WIDTH / 2) / 2
playerY = (SCREEN_WIDTH / 2) / 2
playerAngle = math.pi
monsterX = playerX
monsterY = playerY + 50
monsterActive = False
roomNumber = 0
noiseAlpha = 0
count = 0
playerHP = 6
gameOver = False
lose = False

def loadMap():
  #accesses map
  global monsterActive
  global gameOver
  global lose
  maps = ["maps/map1.txt", "maps/map2.txt", "maps/map3.txt", "maps/map4.txt", "maps/map5.txt", "maps/map6.txt", "maps/map7.txt", "maps/map8.txt", "maps/map9.txt", "maps/map10.txt"]
  if roomNumber == 0:
    mapFile = "maps/map0.txt"
  elif roomNumber == 50:
    monsterActive = False
    mapFile = maps[random.randrange(0, len(maps))]
    gameOver = True
    lose = False
  else:
    mapFile = maps[random.randrange(0, len(maps))]

    #determines status of monster
    global count
    global playerHP
    if roomNumber > 5:
      fun = random.randrange(0, 15)
      if fun >= 10:
        if not monsterActive:
          monsterActive = True
        else:
          count += 1
          if count >= 10:
            count = 0
            monsterActive = False
            if playerHP < 6:
              playerHP += 1
              print("HP increased to: ", playerHP)
          print("count: ", count)
    

  fileIn = open(mapFile, "r")
  room = ""

  #turns map into string and then closes the file
  for x in range (MAP_SIZE):
    line = fileIn.readline()
    line = str(line.replace("\n", ""))
    room = str(room + line)
  fileIn.close()

  print("Map: ", mapFile)
  return room

room = loadMap()

#starts up pygame
pygame.init()

#creates game window and caption
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GHOST MAZE")
pygame.mouse.set_visible(False)

#timer start up
clock = pygame.time.Clock()

#images
noiseOverlay = pygame.image.load("images/noise.png").convert_alpha()
endScreen = pygame.image.load("images/gameOver.png").convert()
HPlow = pygame.image.load("images/red.png").convert_alpha()
winScreen = pygame.image.load("images/winScreen.png").convert()

#health state images
HP_full = pygame.image.load("images/3Hearts.png").convert()
HP_full.set_colorkey(BLACK)

HP_2half = pygame.image.load("images/2.5Hearts.png").convert()
HP_2half.set_colorkey(BLACK)

HP_2 = pygame.image.load("images/2Hearts.png").convert()
HP_2.set_colorkey(BLACK)

HP_1half = pygame.image.load("images/1.5Hearts.png").convert()
HP_1half.set_colorkey(BLACK)

HP_1 = pygame.image.load("images/1Heart.png").convert()
HP_1.set_colorkey(BLACK)

HP_half = pygame.image.load("images/0.5Hearts.png").convert()
HP_half.set_colorkey(BLACK)

HP_none = pygame.image.load("images/0Hearts.png").convert()
HP_none.set_colorkey(BLACK)

HP_state = [HP_none, HP_half, HP_1, HP_1half, HP_2, HP_2half, HP_full]

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
      if room[square] != " ":

        if room[square] == "W":
          #wall shading
          colour = (0 / (1 + depth * depth * 0.0001), 255 / (1 + depth * depth * 0.0001), 255 / (1 + depth * depth * 0.0001))
          #starting value / (1 + depth * depth * 0.0001)
        if room[square] == "D":
          colour = (0 / (1 + depth * depth * 0.0001), 43 / (1 + depth * depth * 0.0001), 74 / (1 + depth * depth * 0.0001))

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
  if not gameOver:
    #convert target x, y coord to map col, row
    col = int(playerX / TILE_SIZE)
    row = int(playerY / TILE_SIZE)

    #calculate map square index
    square = row * MAP_SIZE + col

    #player hits wall (collision detection)
    if room[square] != " ":
      if forward:
        playerX -= -math.sin(playerAngle) * 5
        playerY -= math.cos(playerAngle) * 5
      else:
        playerX += -math.sin(playerAngle) * 5
        playerY += math.cos(playerAngle) * 5

    #monster moves towards player (no wall collision)
    if monsterActive: 
      if monsterX < playerX:
        monsterX += 1
      if monsterX > playerX:
        monsterX -= 1
      if monsterY < playerY:
        monsterY += 1
      if monsterY > playerY:
        monsterY -= 1
      if int(monsterY - playerY) == 0 and int(monsterX - playerX) == 0:
        playerHP -= 1
        print("HP reduced to: ", playerHP)
        monsterY -= 25
        monsterX -= 25
        if playerHP <= 0:
          lose = True
          gameOver = True
  
    if not monsterActive:
      monsterX = playerX
      monsterY = playerY + 50
      noiseAlpha = 0

    #update 3D background
    pygame.draw.rect(screen, FLOOR, [0,SCREEN_HEIGHT/2,SCREEN_WIDTH,SCREEN_HEIGHT])
    pygame.draw.rect(screen, SKY, [0,0,SCREEN_WIDTH, SCREEN_HEIGHT/2])

    #apply raycasting
    castRays()

    #health low indicator
    if playerHP <= 2:
      HPlow.set_alpha(100)
      screen.blit(HPlow, [0,0])

    #danger indicator
    if monsterActive:
      noiseAlpha = 150 / (1 + abs(monsterX - playerX) * abs(monsterY - playerY) * 0.0001)
      noiseOverlay.set_alpha(noiseAlpha)
      screen.blit(noiseOverlay, [0,0])

    #get user input
    keys = pygame.key.get_pressed()

    #handle user input
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: playerAngle -= 0.1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: playerAngle += 0.1
    if keys[pygame.K_UP] or keys[pygame.K_w]:
      forward = True
      playerX += -math.sin(playerAngle) * 5
      playerY += math.cos(playerAngle) * 5
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
      forward = False
      playerX -= -math.sin(playerAngle) * 5
      playerY -= math.cos(playerAngle) * 5
    if keys[pygame.K_SPACE]:
      if room[square] == "D":
        pygame.time.wait(300)
        roomNumber += 1
        print("room number:", roomNumber)
        screen.fill(BLACK)
        playerX = (SCREEN_WIDTH / 2) / 2
        playerY = (SCREEN_WIDTH / 2) / 2
        playerAngle = math.pi
        room = loadMap()
        castRays()

    #set FPS
    clock.tick(30)

    #display room number
    score = "Room: " + str(roomNumber)
    font = pygame.font.SysFont('Monospace Regular', 45)
    scoreSurface = font.render(score, False, WHITE)
    screen.blit(scoreSurface, (SCREEN_WIDTH / 2,0))

    #display HP
    screen.blit(HP_state[playerHP], (0,0))

  else:
    if lose:
      screen.blit(endScreen, (0,0))
      score = str(roomNumber)
      scoreSurface = font.render(score, False, WHITE)
      screen.blit(scoreSurface, ((SCREEN_WIDTH / 2) + 50,200))

      keys = pygame.key.get_pressed()
      if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit(0)
      if keys[pygame.K_RETURN]:
        roomNumber = 0
        playerHP = 6
        monsterActive = False
        count = 0
        screen.fill(BLACK)
        playerX = (SCREEN_WIDTH / 2) / 2
        playerY = (SCREEN_WIDTH / 2) / 2
        playerAngle = math.pi
        room = loadMap()
        castRays()
        gameOver = False
    elif not lose:
      screen.blit(winScreen, (0,0))
      keys = pygame.key.get_pressed()
      if keys[pygame.K_RETURN]:
        screen.fill(BLACK)
        playerX = (SCREEN_WIDTH / 2) / 2
        playerY = (SCREEN_WIDTH / 2) / 2
        playerAngle = math.pi
        roomNumber += 1
        room = loadMap()
        castRays()
        gameOver = False
      if keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit(0)

  #update display
  pygame.display.flip()