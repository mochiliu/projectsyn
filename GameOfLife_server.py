# Python code to implement Conway's Game Of Life 
import numpy as np 
import time
import threading
import socket
from music_vae_generate_minimal import MusicVAE

#from PIL import Image

UDP_IP = "192.168.1.247"
UDP_PORT = 5005
BUFFER_SIZE = 3200

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
IMG_SIZE = 32
N = 30


CYCLE_PERIOD = 10 #seconds


def sendUDP(linear_light_array, ns):
    msg = np.zeros((BUFFER_SIZE,), dtype=np.uint8)
    msg[0:(N*N*3)] = linear_light_array
    index = N*N*3
    for n in ns:
        msg[index] = n.pitch
        msg[index+1] = n.velocity
        try:
            msg[index+2] = np.uint8(n.start_time * 8.0)
        except:
            msg[index+2] = 0
        try:
            msg[index+3] = np.uint8(min(n.end_time * 8.0,255))
        except:
            msg[index+3] = 255
        index += 4
        if index >= BUFFER_SIZE:
            break
        
    sock.sendto(msg, (UDP_IP, UDP_PORT))

def grid_to_linear_color_array(grid):
    N = len(grid)
    linear_array = np.zeros((N*N*3,), dtype=np.uint8)
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
            if np.random.uniform() < 0.1:
                # cell alive
                grid[i,j] = int(np.random.uniform(low=1, high=(256*256*256)-1))
    return grid

def addGlider(i, j, grid): 
    """adds a glider with top left cell at (i, j)"""
    color = int(np.random.uniform(low=1, high=(256*256*256)-1))
    glider = np.array([[0, 0, color], [color, 0, color], [0, color, color]]) 
    rotation_number = np.random.randint(4)
    glider = np.rot90(glider, rotation_number)
    grid[i:i+3, j:j+3] = glider 

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
                    if total == 3 or total == 6:  #hi-life is with 3 or 6
                        old_colors = eight_neighbors[nonzero_array]
                        newGrid[i, j] = get_new_color(old_colors, np.random.uniform(low=0, high=10))
        
    return newGrid

def grid2colorgrid(grid, colorscheme):
    N = len(grid)
    color_grid = np.zeros((N,N,3), dtype=np.float32)
    if colorscheme == 'soft':
        for i in range(N): 
            for j in range(N): 
                pixel_color = rgb_int2tuple(grid[i,j])
                color_grid[i,j,0] = pixel_color[0] / 255 # grid[i,j] > 0
                color_grid[i,j,1] = pixel_color[1] / 255 # grid[i,j] > 0
                color_grid[i,j,2] = pixel_color[2] / 255 # grid[i,j] > 0 
    elif colorscheme == 'hard':
        for i in range(N): 
            for j in range(N): 
                pixel_color = rgb_int2tuple(grid[i,j])
                if ~np.any([np.array(pixel_color) > 0.5]):
                    #none of the colors are bigger than 0.5, take the brightest channel
                    color_grid[i,j,np.argmax(np.array(pixel_color))] = 1
                color_grid[i,j,0] = pixel_color[0] / 255 > 0.5
                color_grid[i,j,1] = pixel_color[1] / 255 > 0.5
                color_grid[i,j,2] = pixel_color[2] / 255 > 0.5 
    else: #binary
        for i in range(N): 
            for j in range(N): 
                color_grid[i,j,0] = grid[i,j] > 0
                color_grid[i,j,1] = grid[i,j] > 0
                color_grid[i,j,2] = grid[i,j] > 0     
    return color_grid

def grid2img(grid, img_size, colorscheme='soft'):
    img = np.zeros((img_size,img_size,3), dtype=np.float32)
    img[1:img_size-1, 1:img_size-1,:] = grid2colorgrid(grid, colorscheme)
    
    # continuous boundaries
    img[0,:,:] = img[img_size-2,:,:]
    img[img_size-1,:,:] = img[1,:,:]
    img[:,0,:] = img[:,img_size-2,:]
    img[:,img_size-1,:] = img[:,1,:]
    return img


class GameOfLife:
    def __init__(self, frame_period=10):
        self.N = N
        self.frame_period = frame_period
        self.grid = randomGrid(self.N)
        self.nextgrid = update(self.grid)
        self.grid_linear_color_array = grid_to_linear_color_array(self.grid)
        self.next_grid_linear_color_array = grid_to_linear_color_array(self.nextgrid)
        self.music_model = MusicVAE()
        self.notes = self.music_model.random_sample_model()
        
        
    def start_game(self, running):
        last_frame_time = time.clock()
        
        while running.is_set():
            current_time = time.clock()        
            if (current_time - last_frame_time > self.frame_period):
                #time to send info
                sendUDP(self.grid_linear_color_array.copy(), self.notes)

                #get the next cycle of the game
                self.grid = self.nextgrid.copy()
                self.nextgrid = update(self.grid)
                self.notes = self.music_model.random_sample_model() #need to be threaded?
                self.grid_linear_color_array = grid_to_linear_color_array(self.grid)
                self.next_grid_linear_color_array = grid_to_linear_color_array(self.nextgrid)
                last_frame_time = current_time
# call main 
if __name__ == '__main__': 
    running = threading.Event()
    game = GameOfLife(CYCLE_PERIOD)
    running.set()
    game.start_game(running)
