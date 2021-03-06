import pygame
import random
from events import *

DOWN = 1
UP = 2
LEFT = 3
RIGHT = 4
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
TILE_WIDTH = 20
TILE_HEIGHT = 20
DEBUG = 1

def opposite(x):
    if x == 1:
        return 2
    elif x == 2:
        return 1
    elif x == 3:
        return 4
    elif x == 4:
        return 3

def outOfRange(coords):
   return coords[0] < 0 or coords[0] > SCREEN_WIDTH or coords[1] < 0 or coords[1] > SCREEN_HEIGHT


def dist(coord1, coord2):
    sq1 = coord2[0] - coord1[0]
    sq2 = coord2[1] - coord1[1]
    sq1 = sq1**2
    sq2 = sq2**2
    result = (sq1 + sq2)**(0.5)
    return result

def adjacent(coord):
    left = (coord[0] - TILE_WIDTH, coord[1])
    right = (coord[0] + TILE_WIDTH, coord[1])
    up = (coord[0], coord[1] - TILE_HEIGHT)
    down = (coord[0], coord[1] + TILE_HEIGHT)
    
    adjList = [left, right, up, down]

    result = [tile for tile in adjList if not outOfRange(tile)]
    return result


class EventManager:
    """this object is responsible for coordinating most communication
    between the Model, View, and Controller.
    """
    def __init__(self):
        from weakref import WeakKeyDictionary
        self.listeners = WeakKeyDictionary()

    #----------------------------------------------------------------------
    def registerListener( self, listener ):
        self.listeners[ listener ] = 1

    #----------------------------------------------------------------------
    def unregisterListener( self, listener ):
        if listener in self.listeners.keys():
            del self.listeners[ listener ]
        
    #----------------------------------------------------------------------
    def post( self, event ):
        if DEBUG:
            if not isinstance(event, TickEvent) and not isinstance(event, MoveEvent):
                print "Message: " + event.name
        """Post a new event.  It will be broadcast to all listeners"""
        for listener in self.listeners.keys():
            #NOTE: If the weakref has died, it will be 
            #automatically removed, so we don't have 
            #to worry about it.
            listener.notify( event )


class KeyBoardController:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.registerListener(self)

    def notify(self, event):
        if isinstance(event, TickEvent):
            for event in pygame.event.get():
                ev = None

                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.evManager.post(QuitEvent())
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    ev = GameStartRequest()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                    direction = UP
                    ev = MoveRequest(direction)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                    direction = DOWN
                    ev = MoveRequest(direction)    
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                    direction = RIGHT
                    ev = MoveRequest(direction)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                    direction = LEFT
                    ev = MoveRequest(direction)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    ev = AddPlayerRequest()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                    ev = AddComputerRequest()
                if ev:
                    self.evManager.post(ev)


class CPUSpinnerController:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.registerListener(self)

        self.go = 1
        self.timer = 0

    def run(self):
        while self.go:
            pygame.time.wait(10)

            import time
            clock = time.time() * 1000
            if self.timer < clock:
                event = TickEvent()
                self.evManager.post(event)
                self.timer = clock + 75

    def notify(self, event):
        if isinstance(event, QuitEvent):
            self.go = 0


class View:
    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.registerListener(self)

        pygame.init()
        clock = pygame.time.Clock()
        clock.tick(10)

        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("snake")
        self.background = pygame.Surface(self.window.get_size())
        self.background.fill((0,0,0)) # black

        self.displayMenu()

        self.window.blit(self.background, (0,0))
        pygame.display.flip()

        self.snakeSprites = pygame.sprite.RenderUpdates()
        self.appleSprites = pygame.sprite.RenderUpdates()

    def displayMenu(self):
        font = pygame.font.SysFont("Arial", 30)
        text = """Press SPACE BAR to start"""
        textImg = font.render( text, 1, (255,255,255))
        self.background.blit( textImg, (0,0) )
        text = """P for new player"""
        textImg = font.render(text, 1, (255,255,255))
        self.background.blit(textImg, (0,font.get_linesize()))
        text = """C for new computer"""
        textImg = font.render(text, 1, (255,255,255))
        self.background.blit(textImg, (0,2*font.get_linesize()))
        self.window.blit(self.background,(0,0))
        pygame.display.flip()

    def showSnake(self, snake):
        for s in snake.snakeList:
            bodySprite = SnakeSprite(self.snakeSprites)
            bodySprite.rect.center = s.rect.center

    def showApple(self, apple):
        appleSprite = AppleSprite(self.appleSprites)
        appleSprite.rect.center = apple.rect.center

    def extendSnake(self, snake):
        snakeSprite = SnakeSprite(self.snakeSprites)
        snakeSprite.rect.center = snake.snakeList[-1].rect.center

    def moveSnake(self, snake):
        self.snakeSprites.empty()

        for s in snake.snakeList:
            bodySprite = SnakeSprite(self.snakeSprites)
            bodySprite.rect.center = s.rect.center

    def checkCollision(self):
        for snake in self.snakeSprites:
            if pygame.sprite.spritecollide(snake, self.appleSprites, True):
                ev = AppleEatenEvent()
                self.evManager.post(ev)
        
    def gameOver(self):
        self.snakeSprites.empty()
        self.appleSprites.empty()

    def clearScreen(self):
        self.background.fill((0,0,0))
        self.window.blit(self.background, (0,0))
        pygame.display.flip()

    def notify(self, event):
        if isinstance(event, TickEvent):
            self.checkCollision()

            self.snakeSprites.clear(self.window, self.background)
            self.appleSprites.clear(self.window, self.background)

            self.snakeSprites.update()
            self.appleSprites.update()

            dirtyRects1 = self.snakeSprites.draw(self.window)
            dirtyRects2 = self.appleSprites.draw(self.window)
            dirtyRects = dirtyRects1 + dirtyRects2

            pygame.display.update(dirtyRects)
        elif isinstance(event, ApplePlaceEvent):
            self.showApple(event.apple)
        elif isinstance(event, SnakePlaceEvent):
            self.clearScreen()
            self.showSnake(event.snake)
        elif isinstance(event, ExtendEvent):
            self.extendSnake(event.snake)
        elif isinstance(event, MoveEvent):
            self.moveSnake(event.snake)
        elif isinstance(event, GameOverEvent):
            self.gameOver()
        elif isinstance(event, MenuDisplayRequest):
            self.displayMenu()


class Game:
    STATE_PREPARING = 0
    STATE_RUNNING = 1

    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.registerListener(self)
        self.state = Game.STATE_PREPARING

        self.maxplayers = 1
        self.players = []
        self.computers = []
        self.apples = [Apple(evManager)]

    def Start(self):
        ev = GameStartedEvent(self)
        self.evManager.post(ev)
        self.state = Game.STATE_RUNNING

    def addPlayer(self):
        if len(self.players) + len(self.computers) == 0:
            player = Player(self.evManager)
            self.players.append(player)

    def addComputer(self):
        if len(self.players) + len(self.computers) == 0:
            computer = Computer(self.evManager)
            self.computers.append(computer)

    def notify(self, event):
        if isinstance(event, GameStartRequest):
            if self.state == Game.STATE_PREPARING:
                self.Start()
        elif isinstance(event, GameOverEvent):
            del self.players[:]
            del self.computers[:]
            self.state = Game.STATE_PREPARING
            ev = MenuDisplayRequest()
            self.evManager.post(ev)
        elif isinstance(event, AddPlayerRequest):
            if self.state == Game.STATE_PREPARING:
                self.addPlayer()
        elif isinstance(event, AddComputerRequest):
            if self.state == Game.STATE_PREPARING:
                self.addComputer()
        

class Player():
    def __init__(self, evManager):
        self.evManager = evManager
        self.game = None
        self.name = ""
        self.evManager.registerListener(self)

        self.snake = [Snake(evManager)]

    def notify(self, event):
        return

class Computer():
    def __init__(self, evManager):
        self.evManager = evManager
        self.game = None
        self.name = ""
        self.evManager.registerListener(self)

        self.snake = [AutoSnake(evManager)]

    def notify(self, event):
        return

class SnakeSprite(pygame.sprite.Sprite):
    def __init__(self, group=None):
        pygame.sprite.Sprite.__init__(self, group)

        snakeSurface = pygame.Surface((TILE_WIDTH,TILE_HEIGHT))
        snakeSurface = snakeSurface.convert_alpha()
        snakeSurface.fill((255,255,255))
        pygame.draw.rect(snakeSurface, (0,0,0), snakeSurface.get_rect(), 1)

        self.image = snakeSurface
        self.rect = snakeSurface.get_rect()

class Snake:
    STATE_ACTIVE = 1
    STATE_INACTIVE = 0

    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.registerListener(self)

        self.state = Snake.STATE_INACTIVE
        self.snakeList = []
        self.score = len(self.snakeList)

        self.speed = 20
        self.counter = 0

        #to prevent multiple keypresses at once
        self.moved = True

    def changeBodyDirection(self, direction):
        if self.state == Snake.STATE_INACTIVE:
            return
        elif direction == opposite(self.snakeList[0].direction):
            return

        self.snakeList[0].prevDirection = self.snakeList[0].direction
        self.snakeList[0].direction = direction
        for i in range(1, len(self.snakeList)):
            self.snakeList[i].prevDirection = self.snakeList[i].direction
            self.snakeList[i].direction = self.snakeList[i - 1].prevDirection

    def changeHeadDirection(self, direction):
        if self.state == Snake.STATE_INACTIVE:
            return
        elif direction == opposite(self.snakeList[0].direction):
            return
        elif self.moved == False:
            return

        self.snakeList[0].prevDirection = self.snakeList[0].direction
        self.snakeList[0].direction = direction
        self.moved = False

    def move(self):
        if self.state == Snake.STATE_ACTIVE:
            for snake in self.snakeList:
                snake.move()

            # deprecated speed control method
            # self.counter += self.speed
            # if self.counter >= 100:
            #     self.counter = 0
            #     self.moved = True
            #     ev = MoveEvent(self)
            #     self.evManager.post(ev)
            #     self.changeBodyDirection(self.snakeList[0].direction)

            self.moved = True
            ev = MoveEvent(self)
            self.evManager.post(ev)
            self.changeBodyDirection(self.snakeList[0].direction)

            #collision check
            headrect = self.snakeList[0].rect
            if headrect.x < 0 or headrect.y < 0 or headrect.x > SCREEN_WIDTH - TILE_WIDTH or headrect.y > SCREEN_HEIGHT - TILE_HEIGHT:
                ev = GameOverEvent()
                self.evManager.post(ev)

            for i in range(1, len(self.snakeList)):
                if headrect.colliderect(self.snakeList[i].rect):
                    ev = GameOverEvent()
                    self.evManager.post(ev)
                    return


    def placeRandom(self, length):
        if self.state == Snake.STATE_INACTIVE:
            x = random.randint(0, SCREEN_WIDTH - TILE_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT - TILE_HEIGHT)
            x = x - x%TILE_WIDTH
            y = y - y%TILE_HEIGHT

            for i in range(length):
                self.snakeList.append(SnakePiece(x, y + TILE_HEIGHT * i, UP, self.speed, self.counter))
            self.state = Snake.STATE_ACTIVE
            ev = SnakePlaceEvent(self)
            self.evManager.post(ev)

    def extend(self):
        def calculateExtend(x, y, direction):
            if direction == UP:
                return (x, y + TILE_HEIGHT)
            elif direction == DOWN:
                return (x, y - TILE_HEIGHT)
            elif direction == LEFT:
                return (x + TILE_WIDTH, y)
            elif direction == RIGHT:
                return (x - TILE_WIDTH, y)
        
        lastSnake = self.snakeList[-1]
        coords = calculateExtend(lastSnake.rect.x, lastSnake.rect.y, lastSnake.direction)
        snakePiece = SnakePiece(coords[0], coords[1], lastSnake.direction, self.speed, self.counter)
        self.snakeList.append(snakePiece)
        self.score += 1

        ev = ExtendEvent(self)
        self.evManager.post(ev)

    def gameOver(self):
        del self.snakeList[:]
        self.counter = 0
        self.state = Snake.STATE_INACTIVE

    def notify(self,event):
        if isinstance(event, TickEvent):
            self.move()
        elif isinstance(event, GameStartedEvent):
            self.placeRandom(3)
        elif isinstance(event, MoveRequest):
            self.changeHeadDirection(event.direction)
        elif isinstance(event, AppleEatenEvent):
            self.extend()
        elif isinstance(event, GameOverEvent):
            self.gameOver()


class AutoSnake(Snake):
    def __init__(self, evManager):
        Snake.__init__(self, evManager)
        self.speed = 25
        self.appleLocation = ()
        self.path = []

    # return list of tiles adjacent to snake head
    def getAdjacent(self):
        x = self.snakeList[0].rect.x
        y = self.snakeList[0].rect.y

        up = (x, y - TILE_HEIGHT)
        down = (x, y + TILE_HEIGHT)
        left = (x - TILE_WIDTH, y)
        right = (x + TILE_HEIGHT, y)

        return [up, down, left, right]


    def closestNeighbor(self, dest):
        distDict = {}
        adjList = self.getAdjacent()
        for adj in adjList:
            distDict[adj] = dist(adj, dest)

        for snake in self.snakeList:
            distDict.pop((snake.rect.x, snake.rect.y), False)
        for coords in distDict.keys():
            if outOfRange(coords):
                del distDict[coords]

        try:
            result = min(distDict, key = distDict.get)
            return result
        except:
            print "Dead end!"
            self.evManager.post(GameOverEvent())

    # returns direction toward tile
    def getDirection(self, dest): 
        if self.state == Snake.STATE_ACTIVE:       
            x = self.snakeList[0].rect.x
            y = self.snakeList[0].rect.y

            if dest[0] > x:
                return RIGHT
            elif dest[0] < x:
                return LEFT
            elif dest[1] > y:
                return DOWN
            elif dest[1] < y:
                return UP

    def greedy(self, dest):
        closest = self.closestNeighbor(dest)
        newDir = self.getDirection(closest)
        self.changeHeadDirection(newDir)

    # return list of steps from dest --> source
    def dijkstra(self, dest):
        if self.state == Snake.STATE_INACTIVE:
            return None

        graph = {} # (x, y) : distance

        # initialize graph
        from sys import maxint
        for y in range(0, SCREEN_HEIGHT, TILE_HEIGHT):
            for x in range(0, SCREEN_WIDTH, TILE_WIDTH):
                graph[(x, y)] = maxint
        # remove tiles blocked by itself
        for snake in self.snakeList[1:]:
            graph.pop((snake.rect.x, snake.rect.y), None)

        prevList = dict.fromkeys(graph.keys())

        source = (self.snakeList[0].rect.x, self.snakeList[0].rect.y)
        graph[source] = 0

        while graph:
            u = min(graph, key = graph .get)
            if u == dest:
                break
            if graph[u] == None:
                print "Nowhere to go"
                break

            adj = adjacent(u)
            for neighbor in adj:
                if neighbor in graph:
                    alt = graph[u] + dist(u, neighbor)
                    if alt < graph[neighbor]:
                        graph[neighbor] = alt
                        prevList[neighbor] = u

            del graph[u]

        S = []
        u = dest
        try:
            while prevList[u] != None:
                S.append(u)
                u = prevList[u]
        except:
            return None
        
        return S[::-1]

    def autopilot(self, dest):
        if not self.path:
            self.greedy(dest)
        else:
            curLocation = (self.snakeList[0].rect.x, self.snakeList[0].rect.y)            
            if self.path[0] == curLocation:
                self.path.pop(0)
            self.greedy(self.path[0])

    def notify(self, event):
        if isinstance(event, TickEvent):
            if self.state == Snake.STATE_ACTIVE:
                self.autopilot(self.appleLocation)
                self.move()
        elif isinstance(event, ApplePlaceEvent):
            self.appleLocation = (event.apple.rect.x, event.apple.rect.y)
            self.path = self.dijkstra(self.appleLocation)
        elif isinstance(event, GameStartedEvent):
            Snake.placeRandom(self, 3)
        elif isinstance(event, AppleEatenEvent):
            self.extend()
        elif isinstance(event, GameOverEvent):
            self.gameOver()


class SnakePiece:
    def __init__(self, x, y, direction, speed, counter):
        self.rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
        self.direction = direction
        self.prevDirection = None
        self.speed = speed
        self.counter = counter

    def move(self):
        # deprecated speed control method
        # self.counter += self.speed

        # if self.counter >= 100:
        #     if self.direction == DOWN:
        #         self.rect.y += TILE_HEIGHT
        #     elif self.direction == UP:
        #         self.rect.y -= TILE_HEIGHT
        #     elif self.direction == LEFT:
        #         self.rect.x -= TILE_WIDTH
        #     elif self.direction == RIGHT:
        #         self.rect.x += TILE_WIDTH
        #     self.counter = 0

        if self.direction == DOWN:
                self.rect.y += TILE_HEIGHT
        elif self.direction == UP:
            self.rect.y -= TILE_HEIGHT
        elif self.direction == LEFT:
            self.rect.x -= TILE_WIDTH
        elif self.direction == RIGHT:
            self.rect.x += TILE_WIDTH

class AppleSprite(pygame.sprite.Sprite):
    def __init__(self, group = None):
        pygame.sprite.Sprite.__init__(self,group)

        appleSurface = pygame.Surface((TILE_WIDTH,TILE_HEIGHT))
        appleSurface = appleSurface.convert_alpha()
        appleSurface.fill((0,0,0))
        pygame.draw.circle(appleSurface, (255,0,0), (TILE_WIDTH/2, TILE_HEIGHT/2), TILE_WIDTH/2)

        self.image = appleSurface
        self.rect = appleSurface.get_rect()


class Apple:
    STATE_ACTIVE = 1
    STATE_INACTIVE = 0

    def __init__(self, evManager):
        self.evManager = evManager
        self.evManager.registerListener(self)
        self.state = self.STATE_INACTIVE

    def placeRandom(self):
        x = random.randint(0, SCREEN_WIDTH - TILE_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT - TILE_HEIGHT)
        x = x - x%TILE_WIDTH
        y = y - y%TILE_HEIGHT
        self.rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
        self.state = Snake.STATE_ACTIVE
        ev = ApplePlaceEvent(self)
        self.evManager.post(ev)

    def notify(self, event):
        if isinstance(event, GameStartedEvent) or isinstance(event, AppleEatenEvent):
            self.placeRandom()
        elif isinstance(event, GameOverEvent):
            self.state = self.STATE_INACTIVE
        # elif isinstance(event, RestartEvent) and self.state == self.STATE_INACTIVE:
        #     self.placeRandom()


def main():
    evManager = EventManager()

    keybd = KeyBoardController(evManager)
    spinner = CPUSpinnerController(evManager)
    view = View(evManager)
    game = Game(evManager)

    spinner.run()


if __name__ == "__main__":
    main()
