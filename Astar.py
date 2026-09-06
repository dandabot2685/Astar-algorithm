import pygame
from math import sqrt
from pygame.locals import*
from time import perf_counter
import heapq
from itertools import count
pygame.init()

HEIGHT = 800
WIDTH = 1200

screen = pygame.display.set_mode((WIDTH,HEIGHT))
run = True
font = pygame.font.Font(None,15)
clock = pygame.time.Clock()



class move_rect:
    def __init__(self,rect):
        self.rect = rect  
        self.reset() #initialises the variables
    def int_vec(self,vec):
        return pygame.Vector2(round(vec.x),round(vec.y))   #rounds pos/arguement to the nearest whole num 
    def move_rect(self,pos_x,pos_y,speed):
        self.end = (pos_x,pos_y)
        self.end_vec = pygame.math.Vector2(self.end) 
        self.rect.x,self.rect.y = self.pos.x,self.pos.y #updates the self.pos varible linked to the rect
        if self.move:
            self.delta = self.end_vec - self.start_vec #difference between start and end
            if self.delta.length_squared() != 0: #avoids an error for when the rect gets to the end
                self.direction = self.delta.normalize() #creates a unit vector 
                self.pos += (self.direction * speed) 
            if self.int_vec(self.pos) == self.int_vec(self.end_vec): #if the rect reaches the end
                self.move = False
        else: #pos reaches the end
            self.pos = self.end_vec #snaps the rect into end position when it's near
            # revert start variables
            self.start_vec = self.end_vec
            self.start = self.end 
            self.reset()
            return True #signals that the rect has completed its movement
    def reset(self):
        self.start = (self.rect.x,self.rect.y)
        self.start_vec = pygame.math.Vector2(self.start)
        self.pos = self.start_vec.copy()
        self.move = True
class Astar():
    class options():
        def __init__(self,x,y,direction,target,curr):
            self.rect = pygame.Rect(x,y,50,50)
            self.direction = direction
            self.parent = direction * -1
            self.gcost = curr + 30
            self.hcost = round(sqrt((target.x-x)**2 + (target.y-y)**2)) 
            self.fcost = self.gcost + self.hcost
            
        def Render(self,color):
            self.text = font.render(str(self.parent),True,color)
            screen.blit(self.text,(self.rect.x,self.rect.y))
        def __repr__(self):
            return f'{self.direction} '
    def __init__(self,rect):
        self.rect = rect
        self.loop = False       
        self.directions = {(0,-60):pygame.Vector2(0,-1), #up
                       (0, 60):pygame.Vector2(0,1),  #down
                       (60,0):pygame.Vector2(1,0),  #right
                       (-60,0):pygame.Vector2(-1,0)} #left
    def setgrid(self):
        self.grid = []
        
        for i in range(-1,2): #generates a 3x3 grid around the chaser and saves it in self.grid
            for row,rects in tilemap.items():
                if row == (self.row + i): #as i changes to -1 to 1 it scans the rows above, the same and below of the chaser
                    for rect in rects:
                        if (self.rect.x - 60) <= rect.x <= (self.rect.x + 60): #checks for rects between a certain range of the chaser
                            self.grid.append(rect)
       
        
        return self.grid
    def recontruct_path(self,sol):
        self.sol = [sol[-1].parent * -1]
        self.pos = pygame.Vector2(self.rect.x,self.rect.y) 
        self.pos += sol[-1].parent * 60
        while self.rect != self.start:
            self.rect.x,self.rect.y = self.pos.x,self.pos.y
            self.index = sol[sol.index(self.rect)] #basically gives object in sol where it intersects with self.rect
            self.sol.insert(0,self.index.parent * -1)
            self.pos += self.index.parent * 60
        self.sol.pop(0)
       
        
        return self.sol
        
        
                
            
        
        
    def pathfind(self,target): #recursion boolean allows the method to repeat itself within itself
        if self.loop == False:
            
            self.start = self.rect.copy()
            self.curr = 0
            self.open = []
            self.closed = []
            self.sol = []
            self.count = count() # this acts as a tie break for the heapq so that if two nodes have the same fcost then it will choose the one that was added first
            self.last_pos = self.rect.copy()
 
            while self.rect != target:
                #clock.tick(15)
               
                self.found = False
                self.neighbors = []
                self.row = 1
                self.y = 50

                #calculates the row where ever it is
                while self.y != self.rect.y:
                    self.y += 60
                    self.row += 1
                self.grid_3x3 = self.setgrid()

                #calculates each path around the chaser 
                for (dx,dy),direction in self.directions.items():
                    self.path = self.options(self.rect.x + dx,self.rect.y + dy,direction,target,self.curr) 
                    self.collision = 0
                    for rect in self.grid_3x3: #uses the 3x3 grid too determine which rects do not collide 
                        if self.path.rect.colliderect(rect): 
                            self.collision += 1 #there is an obstruction
                    
                    if self.collision == 0 and all(self.path.rect.topleft != rect.topleft for rect in self.closed) : #doesnt collide with walls or node is not in the closed list
                        
                        self.neighbors.append(self.path)
                        #pygame.draw.rect(screen,((255,255,255)),self.path.rect)
                
                for neighbor in self.neighbors:
                    self.found = False
                    for element in self.open:
                        if neighbor.rect.topleft == element[-1].rect.topleft: #there is a neighbor in the open list
                            self.found = True
                            if element[-1].gcost > neighbor.gcost:  #compares gcost and if there is a better path then updates it           
                                element[-1].gcost = neighbor.gcost
                                element[-1].fcost = neighbor.gcost + element[-1].hcost
                                element[-1].parent = neighbor.direction    
                    if self.found == False:  #neighbor was not in the open list         
                        heapq.heappush(self.open, (neighbor.fcost,next(self.count), neighbor))
                        
                
                self.lowest = heapq.heappop(self.open) #returns the tuple with the lowest fcost and removes it from the heapq
                
                #pygame.draw.rect(screen,(0,255,255),self.lowest[2].rect)

                self.curr = self.lowest[2].gcost #obtains the object gcost from the tuple in the heapq
                self.sol.append(self.lowest[2]) #adds the object to the solution list
                self.closed.append(self.rect.copy())
                self.rect = self.lowest[2].rect #moves rect to the node with the lowest heuristic
               
                #pygame.display.flip()
                
            self.loop = True 
            
            
            return self.recontruct_path(self.sol[:]) #passes in a shallow copy of self.sol as an argument
        else:
            return self.sol
            
          
                

    

class chaser():
    def __init__(self,x,y,h,w):
        self.rect = pygame.Rect(x,y,h,w)
        self.pos = pygame.Vector2(x,y)
        self.Move = move_rect(self.rect)
        self.moving = False
        self.shadow = Astar(self.rect) #in order to pathfind again i must redefine this
        self.count = 0
       
        self.speed = 1
        self.skip = False
    def move(self,target):
        self.sol = self.shadow.pathfind(target) #gives a list containing vectors that pathfind to the target
        if self.skip == False:
            print(str((perf_counter() - start_time)*1000) + 'ms') #shows how fast the algorithm performs
            self.skip = True
        #clock.tick(144)
        if self.count >= len(self.sol):
            print('finish!')
            return True
        if self.moving == False: #prevents accidental incrementation during movement
            self.pos += self.sol[self.count] *60
        if self.Move.move_rect(self.pos.x,self.pos.y,self.speed) == True:
            #movement is complete
            
            self.count += 1
            self.moving = False
        else:
            self.moving = True
        

    def draw(self,surface):
        pygame.draw.rect(surface,((0,0,255)),self.rect)





start = False


model1 = ['####################',
'#.-...#..x..#......#',
'###.#.#.###.#.######',
'#...#.#...#.#......#',
'#.###.###.#.######.#',
'#.#.....#.#.#....#.#',
'#.#.###.#.#.#.##.#.#',
'#.#.#...#.....#..#.#',
'#...#.#######.#.##.#',
'###.#.........#....#',
'#...###########.####',
'#.###............T##',
'#.....##############',
'####################']
model2 = ['#####################',
'#x....#T........#...#',
'#.#######.#####.#.###',
'#.......#.....#.#...#',
'#####.#.#####.#.###.#',
'#.....#.......#.....#',
'#.#########.#.#######',
'#...........#......-#',
'#####################']
model3 = ['##########',
          '#T-#-----#',
          '##-#-----#',
          '##----#-##',
          '##-##-#-##',
          '##--#-#-##',
          '###---#-##',
          '---#--#--#',
          '---##---x#',
          '---#######']
model4 = ['##########---',
          '##-#####-#---',
          '##----##-#---',
          '##-##-##-### ',
          '##-##T##---# ',
          '##-#####-###-',
          '##--x----###-',
          '######-#####-',
          '######-#####-',
          '#####---####-',
          '#####-#-####-',
          '############-',
          ]
model5 = ['#####################',
'#x....#.............#',
'#.##.#.###########.##',
'#.#..#.#.........#..#',
'#.#.##.#.#######.##.#',
'#.#....#.#.....#....#',
'#.######.#.###.######',
'#........#...#...T..#',
'#..########.#.#######',
'#...........#.......#',
'#####################']
model6 = ['#####################',
'#x........#........T#',
'#.........#.........#',
'#....######.........#',
'#.........######....#',
'#.........#.........#',
'#....######.........#',
'#...................#',
'#...................#',
'#####################']
model7 = [
'############',
'#x.....#...#',
'#......#...#',
'#......#...#',  
'#------#---#',
'#......#...#',
'#..#####.-.#',
'#----------#',
'#.........T#',
'############']
model8 = [
'##################',
"#-----#----------#",
"#-----#------#---#",
"#-----#T---#####-#",
"#-----######---#-#",
"#----------#---#-#",
"#----------#---#-#",
"#----------#---#-#",
"#----------------#",
"#-x--------------#",
'##################'

]
model9 = ['##########',
          '#--------#',
          '#--#T----#',
          '#--#####-#',
          '#--------#',
          '#------x-#',
          '##########']
model10 =    ['###################',
              '#x-------#--------#',
              '#-##-###-#-###-##-#'
              '#-##-###-#-###-##-#',
              '#-----------------#',
              '#-##-#-#####-#-##-#',
              '#----#---#---#----#',
              '####-###-#-###-####',
              '####-#-------#-####',
              '####-#-#####-#-####'
              '-------#####-------',
              '####-#---T---#-####',
              '####-#-#####-#-####',
              '#--------#---------',
              '#-##-###-#-###-##-#',
              '#--#-----------#--#',
              '##-#-#-#####-#-#-##',
              '#----#---#---#----#',
              '#-######-#-######-#',
              '#-----------------#',
              '###################'
              ]

design = model8

# generates a map of pygame.Rects from the design
tilemap = {}
x,y = 50,50
row = 1
for line in design:
    tilemap[row] = []
    for char in line:
        if char == '#':
            tilemap[row].append(pygame.Rect(x,y,50,50)) 
            # tilemap is stored with keys representing rows and values a list of pygame.Rects (representing walls)
        elif char == 'x':
            bot1 = chaser(x, y,50,50) 
        
        elif char == 'T':
            target = pygame.Rect(x,y,50,50)
        
        x += 60  
    row += 1                                  
    y += 60
    x = 50




cooldown = False

while run == True:
    clock.tick(144)
    start_time = pygame.time.get_ticks()
    screen.fill((0,0,0))
    
    key = pygame.key.get_pressed()
    pygame.draw.rect(screen,((0,255,0)),target)

    for rects in tilemap.values(): #draws all the walls on the screen
        for rect in rects:
            pygame.draw.rect(screen,((255,0,0)),rect)
    

    bot1.draw(screen)
    if cooldown == False:
        if key[K_SPACE] == True:
            start_time = perf_counter()
            start = True

    if start == True:
        if bot1.move(target) == True:
         
            start = False
            cooldown = True
            
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()

pygame.quit()

