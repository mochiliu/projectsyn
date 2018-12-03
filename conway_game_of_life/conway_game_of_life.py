# Python code to implement Conway's Game Of Life 
import numpy as np 
import matplotlib.pyplot as plt 
import pygame
import pygame.midi

from time import sleep,time

pygame.midi.init()

# 2 corresponds to my USB MIDI output
# 0 is often the default software MIDI
# Trial and Error needed here unfortunately
m = pygame.midi.Output(3)

# adding music componet
SCALES = {'CMAJOR': [0,2,4,5,7,9,11],
          'BLUES': [0,3,5,6,7,10,11],
          'MAJORPENT': [0,2,4,7,11],
          'MINORPENT': [0,3,5,7,10],
          'JAZZY': [0,2,4,6,8,10],
          'INSEN': [0,1,5,7,10],
          'HIRAJOSHI': [0,1,5,7,9],
          'THIRDS': [0,4,2,5,4,7,5,9,7,11,13,12],
          'CHROMATIC': [0,1,2,3,4,5,6,7,8,9,10,11]
          }
# Pick a scale from above or manufacture your own
default_scale = SCALES['MINORPENT']
# Notes start at:
OFFSET = 10 
N = 30 # set grid size 
note_length = 0.05 # 200ms
maxbounds = (N,N) # 32 notes long, 32 pitches high

def play_midi(notes, scale = default_scale):
    for cursor in range(maxbounds[0]):
        t = time()
        keys = []
        if cursor in notes:
            for note in notes[cursor]:
                keys.append(12 * (note / len(scale)) + (scale[round(note % len(scale))]))
        for k in keys:
            #print(round(k))
            m.note_on(round(k),100)
        sleep((note_length+t) - time())
        for k in keys:
            m.note_off(round(k),100)
            
            
def rgb_int2tuple(rgbint):
    return (rgbint // 256 // 256 % 256, rgbint // 256 % 256, rgbint % 256)

def rgb2int(rint, gint, bint):
    return int(rint*256*256 + (gint*256) + bint)

def color_drift(color, distance):
    drift_direction = np.random.uniform(low=-1,high=1,size=3)
    drift_direction = drift_direction / np.linalg.norm(drift_direction)
    newcolor = np.int32(np.abs(drift_direction*distance + color))
    if not np.any(newcolor):
        # rgb all 0
        nonzero_array_index = int(np.random.uniform(low=0,high=3))
        newcolor[nonzero_array_index] = 1
    return newcolor
    
def get_new_color(old_colors, mutation_distance):
    number_of_old_colors = len(old_colors)
    old_colors_rgb = np.zeros((number_of_old_colors,3))
    for old_color_index in range(number_of_old_colors):
        old_color_tuple = rgb_int2tuple(old_colors[old_color_index])
        old_colors_rgb[old_color_index, 0] = old_color_tuple[0]
        old_colors_rgb[old_color_index, 1] = old_color_tuple[1]
        old_colors_rgb[old_color_index, 2] = old_color_tuple[2]
    avg_old_color = np.mean(old_colors_rgb, axis=0)
    newcolor = color_drift(avg_old_color, mutation_distance)
    return rgb2int(newcolor[0],newcolor[1],newcolor[2])

def randomGrid(N): 
    """returns a grid of NxN random values"""
    grid = np.zeros((N,N), dtype=int)
    for i in range(N): 
        for j in range(N): 
            if np.random.uniform() < 0.2:
                # cell alive
                grid[i,j] = int(np.random.uniform(low=1, high=(256*256*256)-1))
    return grid

def addGlider(i, j, grid): 
	"""adds a glider with top left cell at (i, j)"""
	glider = np.array([[0, 0, 255], 
					[255, 0, 255], 
					[0, 255, 255]]) 
	grid[i:i+3, j:j+3] = glider 

def addGosperGliderGun(i, j, grid): 
	"""adds a Gosper Glider Gun with top left 
	cell at (i, j)"""
	gun = np.zeros(11*38).reshape(11, 38) 

	gun[5][1] = gun[5][2] = 255
	gun[6][1] = gun[6][2] = 255

	gun[3][13] = gun[3][14] = 255
	gun[4][12] = gun[4][16] = 255
	gun[5][11] = gun[5][17] = 255
	gun[6][11] = gun[6][15] = gun[6][17] = gun[6][18] = 255
	gun[7][11] = gun[7][17] = 255
	gun[8][12] = gun[8][16] = 255
	gun[9][13] = gun[9][14] = 255

	gun[1][25] = 255
	gun[2][23] = gun[2][25] = 255
	gun[3][21] = gun[3][22] = 255
	gun[4][21] = gun[4][22] = 255
	gun[5][21] = gun[5][22] = 255
	gun[6][23] = gun[6][25] = 255
	gun[7][25] = 255

	gun[3][35] = gun[3][36] = 255
	gun[4][35] = gun[4][36] = 255

	grid[i:i+11, j:j+38] = gun 

def update(grid): 
    # copy grid since we require 8 neighbors 
    # for calculation and we go line by line 
    N = len(grid)
    
    newGrid = grid.copy() 
    for i in range(N): 
        for j in range(N): 
            # compute 8-neghbor sum 
            # using toroidal boundary conditions - x and y wrap around 
            # so that the simulaton takes place on a toroidal surface. 
            eight_neighbors = np.array([ grid[i, (j-1)%N], grid[i, (j+1)%N],
            						grid[(i-1)%N, j], grid[(i+1)%N, j],
            						grid[(i-1)%N, (j-1)%N], grid[(i-1)%N, (j+1)%N],
            						grid[(i+1)%N, (j-1)%N], grid[(i+1)%N, (j+1)%N] ]) 
    
            nonzero_array = np.nonzero(eight_neighbors)[0]
            total = len(nonzero_array)
            # apply Conway's rules 
            if grid[i, j] > 0: 
                #cell currently alive
                if (total < 2) or (total > 3): 
                    newGrid[i, j] = 0
            else: 
                #cell currently dead
                if total == 3: 
                    old_colors = eight_neighbors[nonzero_array]
                    newGrid[i, j] = get_new_color(old_colors,5)
    grid[:] = newGrid[:] 
    
    #music
    notes = {}
    for x in range(N): 
        for y in range(N): 
            if grid[x,y] > 0:
                if x not in notes:
                    notes[x] = []
                notes[x].append(y+OFFSET)
    play_midi(notes, default_scale)    
    
    return grid


# call main 
if __name__ == '__main__': 
	iteration_count = 5
 
	# more off than on 
	grid = randomGrid(N) 

	for iteration_number in range(iteration_count):
		# set up animation 
		fig, ax = plt.subplots() 
		img = ax.imshow(grid, interpolation='nearest') 
		img = update(grid)
    
		plt.show() 
