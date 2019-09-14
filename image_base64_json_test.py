# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 13:43:55 2019

@author: Mochi
"""

import numpy as np


def randomGrid(N): 
    """returns a grid of NxN random values"""
    grid = np.zeros((N,N), dtype=int)
    for i in range(N): 
        for j in range(N): 
            if np.random.uniform() < 0.1:
                # cell alive
                grid[i,j] = int(np.random.uniform(low=1, high=(256*256*256)-1))
    return grid

