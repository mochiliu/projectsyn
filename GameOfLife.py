# Python code to implement Conway's Game Of Life 
import numpy as np 
import time
import threading
#import sys
import os
is_windows_machine = False
if os.name == 'nt':
    is_windows_machine = True
    
if is_windows_machine:
    import pygame
    import pygame.midi
    import pygame_display_init
else:
    import fluidsynth
    from display import LEDdisplay

#presets
SCALE = 'MAJORPENT'
INSTRUMENT = 11
BANK = 0 #128 # (128,0) for precussion (0, INSTRUMENT) for melody

#piano(0,0) rhodesep(0,4) legendep(0,5) glockenspiel (0,9) vibraphone (0,11) xylophone (0,13) tubularbells (0,14) 
        #percussive organ (0,17) churchorgan (0,19) accordian (0,21) gitar (0,25) bass gitar (0,34) synth bass (0,38) violin (0,40) strings (0,48) ahhchoir (0,52) 
        #trumpet (0,56) tuba (0,58) brasssection (0,61) oboe (0,68) pan flute (0,75) goblin (0,101) banjo (0,105) fiddle (0,110) seashore (0,122) birdtweet (0,123) 
        #out of index (0,128) see General MIDI for full list
FRAMERATE = 10 #Hz
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


def play_midi_fs(last_keys, keys, fs):
    for pitch, velocity in last_keys:
        # turn off the last set of keys
        fs.noteoff(0, pitch)
    for pitch, v in keys:
        # turn on the next set of keys
        fs.noteon(0, pitch, v) #instument keys, and velocity

def play_midi_pygame(last_keys, keys, midi_out):
    for pitch, velocity in last_keys:
        # turn off the last set of keys
        midi_out.note_off(pitch, 127)        
    for pitch, v in keys:
        # turn on the next set of keys
        midi_out.note_on(pitch, v)

def local_GOL_display(screen, gol_board, magnifcation):
    #display the board
    magnified_board = np.repeat(gol_board, magnifcation, axis=0)
    magnified_board = np.repeat(magnified_board, magnifcation, axis=1)  
    
    screen.fill((0,0,0))
    pxarray = pygame.PixelArray(screen)
    for x in range(len(pxarray)):
        for y in range(len(pxarray)):
            pxarray[x,y] = rgb_int2tuple(magnified_board[x,y])
    del pxarray
    pygame.display.update()


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
    
def linear_color_array_to_grid(N, linear_array):
    three_color_mat = np.reshape(linear_array, (N,N,3))
    grid = np.zeros((N,N), dtype=int)
    for i in range(N):
        for j in range(N):
            grid[i,j] = rgb2int(three_color_mat[i,j,0],three_color_mat[i,j,1],three_color_mat[i,j,2])
    return grid

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

def setGrid(N): 
    """returns a grid of NxN random values"""
    grid = np.zeros((N,N), dtype=int)
    for i in range(N):
        for j in range(N):
            if (i == j) or (i == (N-j-1)):
                grid[i,j] = 1
    grid = 255*255*grid
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

class GameOfLife:
    def __init__(self, disp, frame_rate=10, music=True, is_windows=False):
        self.disp = disp
        self.frame_period = 1.0 / frame_rate 
        self.N = 30
        self.grid = randomGrid(self.N)
        self.nextgrid, self.notes = update(self.grid)
        self.grid_linear_color_array = grid_to_linear_color_array(self.grid)
        self.next_grid_linear_color_array = grid_to_linear_color_array(self.nextgrid)
        self.interp_frame_count = 119
        self.note_length = self.frame_period * (self.interp_frame_count + 1) / self.N
        self.scale = SCALES[SCALE] # Pick a scale from above or manufacture your own
        if is_windows:
            self.is_windows = True
            self.magnifcation = 5
            self.midi_out = []
        else:
            self.is_windows = False
            self.midi_out = fluidsynth.Synth(gain=3)
        self.music = music
            
    def start_game(self, running):
        if self.is_windows:
            pygame.init()
            self.disp = pygame.display.set_mode((self.N*self.magnifcation,self.N*self.magnifcation), pygame.HWSURFACE)
            pygame.display.set_caption('Pygame')
            pygame.mouse.set_visible(0)
            pygame.midi.init()
            port = pygame.midi.get_default_output_id()
            print ("using output_id :%s:" % port)
            self.midi_out = pygame.midi.Output(port, 0)
            self.midi_out.set_instrument(INSTRUMENT)
        else:
            self.midi_out.start(driver='alsa')
            sfid = self.midi_out.sfload('/usr/share/sounds/sf2/FluidR3_GM.sf2')
            self.midi_out.program_select(0, sfid, BANK, INSTRUMENT) #instrument selection
            #self.midi_out.program_select(0, sfid, 10, 0) 
            print(self.midi_out.channel_info(0))
        self.stop_requested = False
        current_interpframe = 0
        last_frame_time = time.clock()
        
        last_note_time = last_frame_time + self.note_length + 1 #always start with turning a note on
        last_keys = []
        keys = []
        cursor = 0
        while running.is_set():
            current_time = time.clock()        
            if self.music and (current_time - last_note_time) > self.note_length:
                #time to update music
                last_keys = keys.copy()
                keys = []
                if cursor in self.notes:
                    for note, color in self.notes[cursor]:
                        pitch = round(12 * (note / len(self.scale)) + (self.scale[round(note % len(self.scale))])) #convert note into key using the prechoosen scale
                        veolcity = int(round(np.mean(rgb_int2tuple(color))/255*MAXVELOCITY))
                        keys.append((pitch, veolcity))
                #play_midi_fs(last_keys, keys, self.midiout)
                if self.is_windows:
                    play_midi_pygame(last_keys, keys, self.midi_out)
                else:
                    play_midi_fs(last_keys, keys, self.midi_out)
                cursor += 1
                last_note_time = current_time
                
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
                    cursor = 0
                    #print('next cycle')
                else:
                    #interpolate between the two grids
                    interpolation_ratio = current_interpframe / self.interp_frame_count
                    grid_interp_array = (1-interpolation_ratio) * self.grid_linear_color_array
                    next_grid_interp_array = interpolation_ratio * self.next_grid_linear_color_array
                    if self.music:
                        single_color_linear_array = highlight_linear_color_array(self.N, self.grid_linear_color_array.copy(), max(0, cursor-1))
                    else:
                        single_color_linear_array = np.intc(grid_interp_array + next_grid_interp_array)
                    #single_color_linear_array = self.grid_linear_color_array.copy()
                
                if self.is_windows:
                    local_GOL_display(self.disp, linear_color_array_to_grid(self.N, single_color_linear_array), self.magnifcation)
                else:
                    self.disp.set_from_array(single_color_linear_array)
                last_frame_time = current_time
                current_interpframe += 1
        
        if self.music:
            #turn off the last set of keys before aborting
            if self.is_windows:
                play_midi_pygame(last_keys, [], self.midi_out)
            else:
                play_midi_fs(last_keys, [], self.midi_out)
        if self.is_windows:
            del self.midi_out
            pygame.midi.quit()
        else:
            self.midi_out.delete()

# call main 
if __name__ == '__main__': 
    running = threading.Event()
    if is_windows_machine:
        disp = []
    else:
        disp = LEDdisplay()
    game = GameOfLife(disp,FRAMERATE,music=True,is_windows=is_windows_machine)
    running.set()
    game.start_game(running)
