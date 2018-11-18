# Python code to implement Conway's Game Of Life 
import numpy as np 
import time
from display import LEDdisplay
import threading

def grid_to_linear_color_array(grid):
    N = len(grid)
    linear_array = np.zeros((N*N*3,), dtype=np.intc)
    pixel_index = 0
    for i in range(N):
        for j in range(N):
            pixel_color = rgb_int2tuple(grid[i,j])
            linear_array[pixel_index*3] = pixel_color[0]
            linear_array[(pixel_index*3)+1] = pixel_color[1]
            linear_array[(pixel_index*3)+2] = pixel_color[2] 
            pixel_index += 1
    return linear_array
    
def rgb_int2tuple(rgbint):
    return (rgbint // 256 // 256 % 256, rgbint // 256 % 256, rgbint % 256)

def rgb2int(rint, gint, bint):
    return int(rint*256*256 + (gint*256) + bint)

def color_drift(color, distance):
    drift_direction = np.random.uniform(low=-1,high=1,size=3)
    drift_direction = drift_direction / np.linalg.norm(drift_direction)
    newcolor = np.int32(np.abs(drift_direction*distance + color))
    newcolor[newcolor > 255] = 255
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
    chance_of_glider = 0.05
    threshold_for_adding_glider = 0.1
    
    newGrid = grid.copy() 
    
    if np.count_nonzero(grid) / (N*N) < threshold_for_adding_glider and np.random.uniform() < chance_of_glider:
        addGlider(np.random.randint(N-3), np.random.randint(N-3), newGrid)
    else:
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
                        newGrid[i, j] = get_new_color(old_colors, np.random.uniform(low=0, high=10))
    
    return newGrid

class GameOfLife:
    def __init__(self, disp, frame_rate):
        self.disp = disp
        self.frame_period = 1.0 / frame_rate 
        self.N = 30
        self.grid = randomGrid(self.N)
        self.nextgrid = update(self.grid)
        self.grid_linear_color_array = grid_to_linear_color_array(self.grid)
        self.next_grid_linear_color_array = grid_to_linear_color_array(self.nextgrid)
        self.interp_frame_count = 5
        
    def start_game(self, running):
        self.stop_requested = False
        current_interpframe = 0
        
        last_frame_time = time.clock()
        while running.is_set():
            current_time = time.clock()
            if (current_time - last_frame_time > self.frame_period):
                #time to update
                if current_interpframe >= self.interp_frame_count:
                    #get the next cycle of the game
                    self.grid = self.nextgrid.copy()
                    self.nextgrid = update(self.grid)
                    self.grid_linear_color_array = grid_to_linear_color_array(self.grid)
                    self.next_grid_linear_color_array = grid_to_linear_color_array(self.nextgrid)
                    single_color_linear_array = self.grid_linear_color_array.copy()
                    current_interpframe = 0
                    #print('next cycle')
                else:
                    #interpolate between the two grids
                    interpolation_ratio = current_interpframe / self.interp_frame_count
                    grid_interp_array = (1-interpolation_ratio) * self.grid_linear_color_array
                    next_grid_interp_array = interpolation_ratio * self.next_grid_linear_color_array
                    single_color_linear_array = np.intc(grid_interp_array + next_grid_interp_array)
                    
                self.disp.set_from_array(single_color_linear_array)
                last_frame_time = current_time
                current_interpframe += 1
                
                
# call main 
if __name__ == '__main__': 
    running = threading.Event()
    disp = LEDdisplay()
    game = GameOfLife(disp,10)
    running.set()
    game.start_game(running)
    
