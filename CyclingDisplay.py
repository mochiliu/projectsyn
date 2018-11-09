import numpy as np
import time
from display import LEDdisplay
import threading

class CyclingDisplay:
    def __init__(self, disp, frame_rate, sampled_colors):
        self.disp = disp
        self.frame_period = 1.0 / frame_rate 
        self.sampled_colors = sampled_colors
        self.number_of_samples = np.shape(sampled_colors)
        self.number_of_samples = self.number_of_samples[1]
        
    def start_cycling(self, running):
        self.stop_requested = False
        sample_number = 0
        last_frame_time = time.clock()
        while running.is_set():
            current_time = time.clock()
            if (current_time - last_frame_time > self.frame_period):
                #time to update
                sampled_color = np.intc(self.sampled_colors[:,sample_number])
                #print(sampled_color)
                single_color_linear_array = np.tile(sampled_color, 900)
                self.disp.set_from_array(single_color_linear_array)
                sample_number = (sample_number + 1) % self.number_of_samples
                last_frame_time = current_time
