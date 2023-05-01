import random  # For generating random numbers
import sys  # We will use sys.exit to exit the program
import pygame
from pygame.locals import *  # Basic pygame imports
import numpy as np

# Global Variables for the game
# FPS = 128 # for a faster game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'
NUM_PLAYERS = 20

def closest_pipe(playerx, pipes, param):
    pipe0X = playerx - pipes[0]['x']

    if (pipe0X > param):
        return 1
    else:
        return 0


def welcomeScreen():
    """
    Shows welcome images on the screen
    """


    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player0'].get_height()) / 2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key, start the game for them
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player0'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)


def mainGame(input_params):
    for i in range(NUM_PLAYERS):
        GAME_SPRITES['player' + str(i)] = pygame.image.load(PLAYER).convert_alpha()

    playerAlive = {}
    for i in range(NUM_PLAYERS):
        playerAlive[i] = True
    playerScore = {}
    for i in range(NUM_PLAYERS):
        playerScore[i] = 0
    playersx = {}
    playersy = {}
    for i in range(NUM_PLAYERS):
        playersx[i] = int(SCREENWIDTH / 5)
        playersy[i] = int(SCREENHEIGHT / 2)
    basex = 0

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playersVelY = {}
    for i in range(NUM_PLAYERS):
        playersVelY[i] = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8  # velocity while flapping

    playerFlapped = {}
    for i in range(NUM_PLAYERS):
        playerFlapped[i] = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # flap when user clicks
                for i in range(NUM_PLAYERS):
                    if playersy[i] > 0:
                        playersVelY[i] = playerFlapAccv
                        playerFlapped[i] = True
                        # GAME_SOUNDS['wing'].play()

        # check for collisions
        for i in range(NUM_PLAYERS):
            crashTest = isCollide(playersx[i], playersy[i], upperPipes,
                                  lowerPipes, i)
            if crashTest:
                playerAlive[i] = False
                # turn off the player sprite
                GAME_SPRITES['player' + str(i)].fill((0, 0, 0, 0))




        # check for if every player is dead
        allDead = True
        for i in range(NUM_PLAYERS):
            if playerAlive[i]:
                allDead = False
                break
        if allDead:
            # return the scores along with the starting parameter
            return playerScore, input_params

        # this takes the input param that we will optimizing over many generations
        # the param decides how much above the lower pipe the bird should be to flap
        height = {}
        for i in range(NUM_PLAYERS):
            height[i] = lowerPipes[closest_pipe(playersx[i], lowerPipes, input_params[i][1])]['y'] + input_params[i][0]
            if playersy[i] > height[i]:
                playersVelY[i] = playerFlapAccv
                playerFlapped[i] = True
                # GAME_SOUNDS['wing'].play()


        # check for score
        for i in range(NUM_PLAYERS):
            playerMidPos = playersx[i] + GAME_SPRITES['player' + str(i)].get_width() / 2
            for pipe in upperPipes:
                pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
                if pipeMidPos <= playerMidPos < pipeMidPos + 4 and playerAlive[i]:
                    playerScore[i] += 1
                    # GAME_SOUNDS['point'].play()

        for i in range(NUM_PLAYERS):
            if playersVelY[i] < playerMaxVelY and not playerFlapped[i]:
                playersVelY[i] += playerAccY

        for i in range(NUM_PLAYERS):
            if playerFlapped[i]:
                playerFlapped[i] = False
            playerHeight = GAME_SPRITES['player' + str(i)].get_height()
            playersy[i] = playersy[i] + min(playersVelY[i], GROUNDY - playersy[i] - playerHeight)

        # move pipes to the left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        for i in range(NUM_PLAYERS):
            SCREEN.blit(GAME_SPRITES['player' + str(i)], (playersx[i], playersy[i]))
        max = 0
        for i in range(NUM_PLAYERS):
            if playerScore[i] > max:
                max = playerScore[i]
        myDigits = [int(x) for x in list(str(max))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(playerx, playery, upperPipes, lowerPipes, playerNum):
    if playery > GROUNDY - 25 or playery < 0:
        # GAME_SOUNDS['hit'].play()
        return True

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if (playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            # GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player' + str(playerNum)].get_height() > pipe['y']) and abs(playerx - pipe['x']) < \
                GAME_SPRITES['pipe'][0].get_width():
            # GAME_SOUNDS['hit'].play()
            return True

    return False


def getRandomPipe():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},  # upper Pipe
        {'x': pipeX, 'y': y2}  # lower Pipe
    ]
    return pipe

def getNewPopulation(scores, input_parameters, natural_selection_constant = 5):
    best_scores_index = sorted(range(len(scores)), key=lambda i: scores[i])[-natural_selection_constant:]

    top_parameters = []
    for i in range(natural_selection_constant):
        top_parameters.append(input_parameters[best_scores_index[i]])

    new_population = {}
    for i in range(NUM_PLAYERS):
        # randomly select two different parents
        parent1 = random.choice(top_parameters)
        parent2 = random.choice(top_parameters)
        while parent1 == parent2:
            parent2 = random.choice(top_parameters)

        mean_values = []
        sd_values = []
        for j in range(len(parent1)):
            mean_values.append((parent1[j] + parent2[j])/2)
            sd_values.append(abs(parent1[j] - parent2[j])/2)

        new_member_params = {}
        for j in range(len(mean_values)):
            new_member_params[j] = np.random.normal(mean_values[j], sd_values[j])

        new_population[i] = new_member_params

    return new_population





if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init()  # Initialize all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird by CodeWithHarry')
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )

    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
                            pygame.image.load(PIPE).convert_alpha()
                            )

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    # create multiple players
    for i in range(NUM_PLAYERS):
        GAME_SPRITES['player' + str(i)] = pygame.image.load(PLAYER).convert_alpha()

    welcomeScreen()  # Shows welcome screen to the user until he presses a button

    # create an initial population
    modifying_values = {}
    for i in range(NUM_PLAYERS):
        # generate random values as input for the population
        modifying_values[i] = [
            random.randint(-200, 200),
            random.randint(-100, 100)
        ]

    j = 1
    while True:
        scores, input = mainGame(modifying_values)  # This is the main game function

        print("Generation " + str(j))
        for i in range(NUM_PLAYERS):
            print("Player " + str(i) + " score is " + str(scores[i]) + " and input is " + str(input[i]))
        j += 1

        modifying_values = getNewPopulation(scores, input, 5)

