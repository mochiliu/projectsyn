# Python code to implement Conway's Game Of Life 
import numpy as np 
import time
import threading
import socket
#from PIL import Image

UDP_IP = "192.168.1.247"
UDP_PORT = 5005
BUFFER_SIZE = 3000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
IMG_SIZE = 32
N = 30

#presets
SCALE = 'MAJORPENT'
#piano(0,0) rhodesep(0,4) legendep(0,5) glockenspiel (0,9) vibraphone (0,11) xylophone (0,13) tubularbells (0,14) 
        #percussive organ (0,17) churchorgan (0,19) accordian (0,21) gitar (0,25) bass gitar (0,34) synth bass (0,38) violin (0,40) strings (0,48) ahhchoir (0,52) 
        #trumpet (0,56) tuba (0,58) brasssection (0,61)
FRAMERATE = 3 #Hz
MAXVELOCITY = 100
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
OFFSET = 0 #keys on midi offset

def sendUDP(linear_light_array, keys_on, keys_off):
    msg = np.zeros((BUFFER_SIZE,), dtype=np.uint8)
    msg[0:(N*N*3)] = linear_light_array
    index = N*N*3
    for pitch, velocity in keys_on:
        msg[index] = pitch
        msg[index+1] = velocity
        index += 2
    index += 2 #skip two spaces as signifier that keys_on is done
    for pitch, velocity in keys_off:
        msg[index] = pitch
        msg[index+1] = velocity
        index += 2
    #watch for overflow error?
    #print(len(msg))
    sock.sendto(msg, (UDP_IP, UDP_PORT))

def highlight_linear_color_array(N, linear_array, highlightx):
    pixel_index = 0
    for x in range(N):
        for y in range(N):
            if x == highlightx:
                if not (linear_array[pixel_index] > 0 or linear_array[pixel_index+1] > 0 or linear_array[pixel_index+2] > 0):
                    linear_array[pixel_index] = 50
                    linear_array[pixel_index+1] = 50
                    linear_array[pixel_index+2] = 50
            pixel_index += 3
    return linear_array

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
                    if total == 3 or total == 6:  #hi-life is with 3 or 6
                        old_colors = eight_neighbors[nonzero_array]
                        newGrid[i, j] = get_new_color(old_colors, np.random.uniform(low=0, high=10))
                        
    #music
    notes = {}
    for x in range(N): 
        for y in range(N): 
            if grid[x,y] > 0:
                if x not in notes:
                    notes[x] = []
                notes[x].append((y+OFFSET, grid[x,y])) #x is in time, tuple is (note, color)
        
    return newGrid, notes

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
    def __init__(self, frame_rate=10, music=True):
        self.N = N
        self.frame_period = 1.0 / frame_rate 
        self.interp_frame_count = self.N # how many notes in music sequence
        
        self.grid = randomGrid(self.N)
        self.nextgrid, self.notes = update(self.grid)
        self.grid_linear_color_array = grid_to_linear_color_array(self.grid)
        self.next_grid_linear_color_array = grid_to_linear_color_array(self.nextgrid)
        self.scale = SCALES[SCALE] # Pick a scale from above or manufacture your own
        self.music = music
            
    def start_game(self, running):
        current_interpframe = 0
        last_frame_time = time.clock()
        
        last_keys = []
        keys = []
        while running.is_set():
            current_time = time.clock()        
            if (current_time - last_frame_time > self.frame_period):
                #time to update light board
                if current_interpframe >= self.interp_frame_count:
                    #get the next cycle of the game
                    self.grid = self.nextgrid.copy()
                    self.nextgrid, self.notes = update(self.grid)
                    self.grid_linear_color_array = grid_to_linear_color_array(self.grid)
                    self.next_grid_linear_color_array = grid_to_linear_color_array(self.nextgrid)
                    single_color_linear_array = self.grid_linear_color_array.copy()
                    current_interpframe = 0
                    #print('next cycle')
                    
                if self.music:
                    #time to update music
                    last_keys = keys.copy()
                    keys = []
                    if current_interpframe in self.notes:
                        for note, color in self.notes[current_interpframe]:
                            pitch = round(12 * (note / len(self.scale)) + (self.scale[round(note % len(self.scale))])) #convert note into key using the prechoosen scale
                            veolcity = int(round(np.mean(rgb_int2tuple(color))/255*MAXVELOCITY))
                            keys.append((pitch, veolcity))
                            
                    single_color_linear_array = highlight_linear_color_array(self.N, self.grid_linear_color_array.copy(), max(0, current_interpframe-1))
                    
                sendUDP(single_color_linear_array, keys, last_keys)
                last_frame_time = current_time
                current_interpframe += 1
                
                #debug
#                img_array = grid2img(self.grid, IMG_SIZE)
#                img_array = np.uint8(img_array* 255) # convert to regular image values
#                img = Image.fromarray(img_array)
#                img.show()
#                running.clear()
        #if self.music:
            #turn off the last set of keys before aborting
            #STREAM END
            #sendUDP(np.zeros((self.N*self.N*3,), dtype=np.uint8), [], last_keys)

# call main 
if __name__ == '__main__': 
    running = threading.Event()
    game = GameOfLife(FRAMERATE,music=True)
    running.set()
    game.start_game(running)
