import pygame
from pygame import Vector2 as vec
from math import sqrt
from pygame.locals import*
from time import perf_counter
import heapq
from itertools import count
import numpy as np
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
    class path_node():
        def __init__(self,pos,direction,target,curr_g,rect):
            self.rect = rect
            self.pos = pos # location on the tilemap
            self.direction = vec(direction) 
            self.parent = self.neg_tuple(direction)
            self.gcost = curr_g + 5 # ground cost from moving to each node
            self.hcost = (pos[0] - target[0])**2 + (pos[1] - target[1])**2 # calculates the heuristic (distance between two points)
            self.fcost = self.gcost + self.hcost # sums them together

        def neg_tuple(self,tpl):
            return tuple(-x for x in tpl)
        
        def Render(self,color): #this method is used for debugging
            self.text = font.render(str(self.parent),True,color)
            screen.blit(self.text,(self.rect.x,self.rect.y))
        def __repr__(self):
            return str(self.parent)
    
    def __init__(self,tilemap,pos:tuple,rect):
        self.rect = rect
        self.tilemap = tilemap
        self.pos = pos #stores (row,col) of the chaser
        self.loop = False       
       
        self.directions = {(0,-1), #UP
                          (0,1), #DOWN
                          (1,0), #RIGHT
                          (-1,0)} #LEFT
        
        # keys represent vector directions 
        # I store them as tuples because vectors are unhashable 
        
   
    def add_tuples(self,a, b):
        return tuple(int(x + y) for x, y in zip(a, b))
    
   
    def pathfind(self,target:tuple): #recursion boolean allows the method to repeat itself within itself
        if self.loop == False:
            
            self.curr_g = 0
            self.open = [] #these will store tuples (row,col) where the algorithm considers the next path to take
            self.closed = set() 
            self.sol = []
            self.count = count() # this acts as a tie break for the heapq so that if two nodes have the same fcost then it will choose the one that was added first
            self.start = self.pos
 
            while not self.pos == target: 
                #clock.tick(15)
                
                self.found = False
                self.neighbors = []
                
                
                #calculates each path around the chaser 
                for direction in self.directions: 
                    self.is_barrier = self.add_tuples(self.pos,direction[::-1]) 
                    # since direction represent vector directions which will be stored in self.sol
                    # it must be reversed so that when i add it to self.pos it works according to the tilemap
                    
                    if self.tilemap[self.is_barrier[0],self.is_barrier[1]] !=  1 and not self.is_barrier in self.closed:
                        offset = (self.rect.x + direction[0]*60,self.rect.y + direction[1]*60)
                        self.neighbors.append(self.path_node(self.is_barrier,direction,target,self.curr_g,pygame.Rect(offset[0],offset[1],50,50)))

                        #pygame.draw.rect(screen,(255,255,255),pygame.Rect(offset[0],offset[1],50,50))

                                
                for neighbor in self.neighbors:                    
                    self.found = False
                    for element in self.open:
                        if neighbor.pos == element[-1].pos: #there is a neighbor in the open list
                            self.found = True
                            if element[-1].gcost > neighbor.gcost:  #compares gcost and if there is a better path then updates it           
                                element[-1].gcost = neighbor.gcost
                                element[-1].fcost = neighbor.gcost + element[-1].hcost
                                element[-1].parent = neighbor.direction    
                    if self.found == False:  #neighbor was not in the open list   
                        
                        heapq.heappush(self.open, (neighbor.fcost,next(self.count), neighbor))


                             
                self.lowest = heapq.heappop(self.open) #returns the tuple with the lowest fcost and removes it from the heapq

                #pygame.draw.rect(screen,(0,255,255),self.lowest[2].rect)

                self.curr_g = self.lowest[2].gcost #obtains the object gcost from the tuple in the heapq
                self.sol.append(self.lowest[2]) #adds the object to the solution list
                self.closed.add(self.pos)
                self.pos = self.lowest[2].pos # moves pos to the node with the lowest heuristic

                #self.rect = self.lowest[2].rect.copy()
                #pygame.display.flip()
                               
                
            self.loop = True
            
            return self.recontruct_path(self.sol[:]) #passes in a shallow copy of self.sol as an argument
        else:
            return self.sol
            
    def recontruct_path(self,sol):
        self.sol = [sol[-1].direction] #adds the last object.direction
        self.pos = self.add_tuples(self.pos,sol[-1].parent[::-1]) 

        while not self.pos == self.start:
            self.index = next((obj for obj in sol if obj.pos == self.pos), None)# gives object in sol where it intersects with self.pos
            if self.index == None:
                break
            self.sol.insert(0,self.index.direction)
            self.pos = self.add_tuples(self.pos,self.index.parent[::-1])
            
        return self.sol


def convert_array(map_design):
    global target
    arr = []
    rects = []
    x,y = 50,50
    for row in map_design:
        Row = []
        for col in row:
            if col == '#':
                Row.append(1)
                rects.append(pygame.Rect(x,y,50,50))
            elif col == 'T':
                target = pygame.Rect(x,y,50,50)
                Row.append(3)
            elif col == 'x':
                bot_x,bot_y = x,y
                Row.append(2)           
            
            else:
                Row.append(0)
                
            x += 60
        arr.append(Row)
        
        x = 50
        y += 60
        
    return np.array(arr),rects,bot_x,bot_y


       
                

    

class chaser():
    def __init__(self,x,y,h,w,tilemap,pos):
        self.rect = pygame.Rect(x,y,h,w)
        self.pos = vec(x,y)
        self.Move = move_rect(self.rect)
        self.moving = False
        self.shadow = Astar(tilemap,pos,self.rect.copy()) #in order to pathfind again i must redefine this
        self.count = 0
       
        self.speed = 1
        self.skip = False
    def move(self,target):
        self.sol = self.shadow.pathfind(target) #gives a list containing vectors that pathfind to the target
        
        if self.skip == False:
            print(str((perf_counter() - start_time)*1000) + 'ms')
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
              '#-##-###-#-###-##-#',
              '#-##-###-#-###-##-#',
              '#-----------------#',
              '#-##-#-#####-#-##-#',
              '#----#---#---#----#',
              '####-###-#-###-####',
              '####-#-------#-####',
              '####-#-#####-#-####',
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

design = model6

tilemap_array,tilemap_rects,bot_x,bot_y = convert_array(design)
# gets coords on tilemap for bot
x,y = np.where(tilemap_array == 2)
pos = (x[0],y[0])

bot = chaser(bot_x,bot_y,50,50,tilemap_array,pos)

# gets coords on tilemap for target
x,y = np.where(tilemap_array == 3)
target_pos = (x[0],y[0])

cooldown = False

while run == True:
    clock.tick(144)
    start_time = pygame.time.get_ticks()
    screen.fill((0,0,0))
    
    key = pygame.key.get_pressed()
    pygame.draw.rect(screen,((0,255,0)),target)

    for rect in tilemap_rects:
        pygame.draw.rect(screen,(255,0,0),rect)

    bot.draw(screen)
    if cooldown == False:
        if key[K_SPACE] == True:
            start_time = perf_counter()
            start = True

    if start == True:
        if bot.move(target_pos) == True:
         
            start = False
            cooldown = True
            
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip()

pygame.quit()

