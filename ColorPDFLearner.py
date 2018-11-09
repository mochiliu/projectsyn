# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 20:58:55 2018

@author: Mochi
"""
import os
import cv2
import numpy as np
from scipy.spatial.distance import cdist, euclidean
from scipy.stats import norm
from scipy import ndimage
from google_images_download import google_images_download   #importing the library
from sklearn.decomposition import PCA
import shutil
import copy

#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D

def geometric_median(X, eps=1e-2):
    y = np.mean(X, 0)
    while True:
        D = cdist(X, [y])
        nonzeros = (D != 0)[:, 0]
        Dinv = 1 / D[nonzeros]
        Dinvs = np.sum(Dinv)
        W = Dinv / Dinvs
        T = np.sum(W * X[nonzeros], 0)
        num_zeros = len(X) - np.sum(nonzeros)
        if num_zeros == 0:
            y1 = T
        elif num_zeros == len(X):
            return y
        else:
            R = (T - y) * Dinvs
            r = np.linalg.norm(R)
            rinv = 0 if r == 0 else num_zeros/r
            y1 = max(0, 1-rinv)*T + min(1, rinv)*y
        if euclidean(y, y1) < eps:
            return y1
        y = y1

def NN(A, start):
    start = start-1 #To compensate for the python index starting at 0.
    n = len(A)
    path = [start]
    costList = []
    tmp = copy.deepcopy(start)
    B = copy.deepcopy(A)
    #This block eliminates the startingnode, by setting it equal to inf.
    for h in range(n):
        B[h][start] = np.inf

    for i in range(n):
        # This block appends the visited nodes to the path, and appends
        # the cost of the path.
        for j in range(n):
            if B[tmp][j] == min(B[tmp]):
                costList.append(B[tmp][j])
                path.append(j)
                tmp = j
                break
        # This block sets the current node to inf, so it can't be visited again.
        for k in range(n):
            B[k][tmp] = np.inf
#    # The last term adds the weight of the edge connecting the start - and endnote.
#    cost = sum([i for i in costList if i < np.inf]) + A[path[len(path)-2]][start]
    # The last element needs to be popped, because it is equal to inf.
    path.pop(n)
    # Because we want to return to start, we append this node as the last element.
    path.insert(n, start)

    return path

def interp_path(sampled_colors, max_distance):
    #this function interploates the sampled colors such that the transitions are smooth, each change less than max_distance
    number_of_samples = np.shape(sampled_colors)
    number_of_samples = number_of_samples[1]
    dis = np.zeros([number_of_samples,1])
    #print(sampled_colors)
    for sample_index in range(number_of_samples-1):
        #calculate the cumulative distance
        dis[sample_index+1] = dis[sample_index] + euclidean(sampled_colors[:,sample_index],sampled_colors[:,sample_index+1])    
        
    number_in_path = int(np.ceil(dis[-1] / max_distance))
    if number_in_path < 1:
        number_in_path = 1
    red_path = np.interp(np.linspace(0,dis[-1],number_in_path), np.squeeze(dis), np.squeeze(sampled_colors[0,:]))
    green_path = np.interp(np.linspace(0,dis[-1],number_in_path), np.squeeze(dis), np.squeeze(sampled_colors[1,:]))
    blue_path = np.interp(np.linspace(0,dis[-1],number_in_path), np.squeeze(dis), np.squeeze(sampled_colors[2,:]))
    new_path = np.vstack((red_path,green_path,blue_path))
    return new_path

class ColorPDFLearner(object):
    def __init__(self):
        self.pca_pdf = True
        self.color_resolution = 8
        self.num_traing_imgs = 100
        self.edge_pdf_limit = 0.3

    def quicklearnword(self, search_term):
        cwd = os.getcwd()
        imagedir = os.path.join(cwd, 'images')
        pdfdir = os.path.join(cwd, 'colorpdfs')
        search_term_plus_color = search_term +' color'
        response = google_images_download.googleimagesdownload()   #class instantiation
        arguments = {"keywords":search_term_plus_color,"limit":1,"print_urls":True,"output_directory":imagedir,"no_numbering":True,"no_directory":True}   #creating list of arguments
        paths = response.download(arguments)   #passing the arguments to the function
        small_color_pdf = np.ones([256//self.color_resolution,256//self.color_resolution,256//self.color_resolution])
        small_color_pdf = small_color_pdf / np.sum(small_color_pdf)       
        
        try:
            paths = paths[search_term_plus_color]
            path = paths[0]
            #get geometic median pxel of the iimage
            bgr_img = cv2.imread(path, cv2.IMREAD_COLOR)
            bgr_img = cv2.resize(bgr_img, dsize=(50, 50), interpolation=cv2.INTER_NEAREST)
            pixels = np.reshape(bgr_img, (-1,3))
            median_pixel = geometric_median(pixels)
            median_pixel = np.round(median_pixel)
            median_pixel = np.array([median_pixel[2], median_pixel[1], median_pixel[0]],dtype=int)
            small_color_pdf = np.zeros([256//self.color_resolution,256//self.color_resolution,256//self.color_resolution])
            small_color_pdf[median_pixel[0]//self.color_resolution, median_pixel[1]//self.color_resolution, median_pixel[2]//self.color_resolution] = 1
        except:
            print('error quick learning')
            
        #save and clean up
        save_path = os.path.join(pdfdir, search_term+'.npy')
        np.save(save_path,small_color_pdf)
        shutil.rmtree(imagedir)
        
    def learnword(self, search_term):
        cwd = os.getcwd()
        imagedir = os.path.join(cwd, 'images')
        pdfdir = os.path.join(cwd, 'colorpdfs')
        
        search_term_plus_color = search_term +' color'
        response = google_images_download.googleimagesdownload()   #class instantiation
        arguments = {"keywords":search_term_plus_color,"limit":self.num_traing_imgs,"print_urls":True,"output_directory":imagedir,"no_numbering":True,"no_directory":True}   #creating list of arguments
        paths = response.download(arguments)   #passing the arguments to the function
        
        image_index = 0
        median_pixels = np.zeros((3,len(paths[search_term_plus_color])))
        for path in paths[search_term_plus_color]:
            #get geometic median pixel of the image
            if path != "":
                try:
                    bgr_img = cv2.imread(path, cv2.IMREAD_COLOR)
                    if bgr_img is not None:
                        bgr_img = cv2.resize(bgr_img, dsize=(50, 50), interpolation=cv2.INTER_NEAREST)
                        pixels = np.reshape(bgr_img, (-1,3))
                        median_pixel = geometric_median(pixels)
                        median_pixel = np.round(median_pixel)
                        median_pixel = np.array([median_pixel[2], median_pixel[1], median_pixel[0]])
                        if not np.array_equal(median_pixel, np.array([255,255,255])):
                            median_pixels[:,image_index] = median_pixel
                            image_index += 1
                except:
                    print('error loading file')
                    
        median_pixels = np.int16(median_pixels[:,0:image_index])
        
        #color_pdf = np.zeros([256,256,256],dtype=float)
        small_color_pdf = np.zeros([256//self.color_resolution,256//self.color_resolution,256//self.color_resolution])
        
        if self.pca_pdf:
            # do a PCA on the dataset
            pca = PCA(n_components=3)
            pca.fit(np.transpose(median_pixels))
            pca_std = np.sqrt(pca.explained_variance_)
            
            edge_pdf_sum = 0
            # generate pdf with edge probs, but only for dimensions with small variance
            for r_index in range(0,256//self.color_resolution):
                for g_index in range(0,256//self.color_resolution):
                    for b_index in range(0,256//self.color_resolution):
                        # get new coordinate system
                        new_coordinates_lower_bound = np.squeeze(pca.transform(np.array([[r_index*self.color_resolution,g_index*self.color_resolution,b_index*self.color_resolution]])))
                        new_coordinates_upper_bound = np.squeeze(pca.transform(np.array([[(r_index+1)*self.color_resolution,(g_index+1)*self.color_resolution,(b_index+1)*self.color_resolution]])))
                        # rescale to std
                        coordinate_stds_lower_bound = -np.abs(new_coordinates_lower_bound / pca_std)
                        coordinate_stds_upper_bound = -np.abs(new_coordinates_upper_bound / pca_std)
        
                        if r_index == 0 or r_index == 256//self.color_resolution-1 or g_index == 0 or g_index == 256//self.color_resolution-1 or b_index == 0 or b_index == 256//self.color_resolution-1:
                            #at an edge bin and we have dimensions with small variances
                            firstpc_cum_prob = max(norm.cdf(coordinate_stds_lower_bound[0]),norm.cdf(coordinate_stds_upper_bound[0]))
                            secondpc_cum_prob = max(norm.cdf(coordinate_stds_lower_bound[1]),norm.cdf(coordinate_stds_upper_bound[1]))
                            thirdpc_cum_prob = max(norm.cdf(coordinate_stds_lower_bound[2]),norm.cdf(coordinate_stds_upper_bound[2]))
                            edge_pdf_sum = edge_pdf_sum + (firstpc_cum_prob*secondpc_cum_prob*thirdpc_cum_prob)
                        else:
                             # find cdf for each dimension and multiply them                    
                            firstpc_cum_prob = abs(norm.cdf(coordinate_stds_lower_bound[0]) - norm.cdf(coordinate_stds_upper_bound[0]))
                            secondpc_cum_prob = abs(norm.cdf(coordinate_stds_lower_bound[1]) - norm.cdf(coordinate_stds_upper_bound[1]))
                            thirdpc_cum_prob = abs(norm.cdf(coordinate_stds_lower_bound[2]) - norm.cdf(coordinate_stds_upper_bound[2]))
                           
                        small_color_pdf[r_index, g_index, b_index] = firstpc_cum_prob*secondpc_cum_prob*thirdpc_cum_prob
                print(r_index)

            small_color_pdf_sum = np.sum(small_color_pdf)
            if edge_pdf_sum / small_color_pdf_sum > self.edge_pdf_limit:
                #the edges have more than the threshold probability, bring it down to the limit
                middle_sum = (small_color_pdf_sum-edge_pdf_sum)
                total_target = middle_sum / (1-self.edge_pdf_limit)
                edge_target = total_target - middle_sum
                correction_factor = edge_target/edge_pdf_sum
                for r_index in range(0,256//self.color_resolution):
                    for g_index in range(0,256//self.color_resolution):
                        for b_index in range(0,256//self.color_resolution):
                            if r_index == 0 or r_index == 256//self.color_resolution-1 or g_index == 0 or g_index == 256//self.color_resolution-1 or b_index == 0 or b_index == 256//self.color_resolution-1:
                                small_color_pdf[r_index, g_index, b_index] = small_color_pdf[r_index, g_index, b_index] * correction_factor
        #    color_pdf = ndimage.zoom(small_color_pdf, (8,8,8), order=0)
        #    color_pdf = ndimage.filters.gaussian_filter(color_pdf, color_resolution, mode='reflect')  
        else:
            #generate pdf by blurring sampled data
            for sample_index in range(image_index): 
                small_color_pdf[median_pixels[0,sample_index]//self.color_resolution,median_pixels[1,sample_index]//self.color_resolution,median_pixels[2,sample_index]//self.color_resolution] = small_color_pdf[median_pixels[0,sample_index]//self.color_resolution,median_pixels[1,sample_index]//self.color_resolution,median_pixels[2,sample_index]//self.color_resolution] + 1
            small_color_pdf = ndimage.filters.gaussian_filter(small_color_pdf, 24//self.color_resolution, mode='reflect')
            
        #renormalize color_pdf
        small_color_pdf = small_color_pdf / np.sum(small_color_pdf)
        
        #save and clean up
        save_path = os.path.join(pdfdir, search_term+'.npy')
        np.save(save_path,small_color_pdf)
        shutil.rmtree(imagedir)
    
    def getwordscdf(self, wordorwords):
        cwd = os.getcwd()
        pdfdir = os.path.join(cwd, 'colorpdfs')
        words_to_learn = []
        if isinstance(wordorwords, (list,)):
            #many words
            small_color_pdf = np.ones([256//self.color_resolution,256//self.color_resolution,256//self.color_resolution])
            for word in wordorwords:
                load_path = os.path.join(pdfdir, word+'.npy')
                if not os.path.isfile(load_path):
                    #this word is new, quick learn it first, real learn later
                    print('learning ' + word)
                    self.quicklearnword(word)
                    words_to_learn.append(word)
                small_color_pdf = small_color_pdf * np.load(load_path) #load the cdf
            small_color_pdf = small_color_pdf / np.sum(small_color_pdf) #normalize
        else:
            #one word
            load_path = os.path.join(pdfdir, wordorwords+'.npy')
            if not os.path.isfile(load_path):
                #this word is new, quick learn it first, real learn later
                print('learning ' + wordorwords)
                self.quicklearnword(word)
                words_to_learn.append(word)
            small_color_pdf = np.load(load_path) #load the cdf
        return small_color_pdf, words_to_learn
    
    def maxlikelihoodcolor(self, wordorwords):
        small_color_pdf, words_to_learn = self.getwordscdf(wordorwords)
        sampled_index = np.argmax(small_color_pdf)
        sampled_color = np.array(np.unravel_index(sampled_index, (256//self.color_resolution, 256//self.color_resolution, 256//self.color_resolution)))
        sampled_color = sampled_color * self.color_resolution
        return sampled_color, words_to_learn

    def sampleonce(self, wordorwords):
        small_color_pdf, words_to_learn = self.getwordscdf(wordorwords)
        linearized_pdf_cumsum = np.cumsum(small_color_pdf.flatten())  #linearize pdf
        sampled_index = np.argmax(linearized_pdf_cumsum > np.random.uniform())
        sampled_color = np.array(np.unravel_index(sampled_index, (256//self.color_resolution, 256//self.color_resolution, 256//self.color_resolution)))
        sampled_color = sampled_color * self.color_resolution
        return sampled_color, words_to_learn

    def samplemultiple(self, wordorwords, number_of_samples):
        small_color_pdf, words_to_learn = self.getwordscdf(wordorwords)
        sampled_colors = np.zeros([3,number_of_samples])
        linearized_pdf_cumsum = np.cumsum(small_color_pdf.flatten())  #linearize pdf
        for sample_index in range(number_of_samples):
            sampled_index = np.argmax(linearized_pdf_cumsum > np.random.uniform())
            sampled_color = np.array(np.unravel_index(sampled_index, (256//self.color_resolution, 256//self.color_resolution, 256//self.color_resolution)))
            sampled_color = sampled_color * self.color_resolution
            sampled_colors[:,sample_index] = sampled_color
        return sampled_colors, words_to_learn
    
    def sortedsamplemultiple(self, wordorwords, number_of_samples):
        sampled_colors, words_to_learn = self.samplemultiple(wordorwords, number_of_samples)
        #calculated distances in color space
        A = np.zeros([number_of_samples,number_of_samples])
        #calculated distances in color space
        for x in range(number_of_samples):
            for y in range(number_of_samples):
                A[x,y] = euclidean(sampled_colors[:,x],sampled_colors[:,y])
        # Nearest neighbour algorithm
        path = NN(A, 0)
        sorted_colors = np.zeros((3,number_of_samples+1))
        # Final array
        sorted_color_index = 0
        for sampled_color_index in path:
            sorted_colors[:,sorted_color_index] = sampled_colors[:,sampled_color_index]
            sorted_color_index += 1
        sampled_colors = interp_path(sampled_colors, 5)
        print(sampled_colors)
        return sampled_colors, words_to_learn

if __name__ == "__main__":
    number_of_samples = 20
    words = 'red'
    color_learner = ColorPDFLearner()
#    ml_color = color_learner.maxlikelihoodcolor(words)
#    print(ml_color)
    color_learner.learnword(words)
    sampled_colors, words_to_learn = color_learner.sortedsamplemultiple(words, number_of_samples)
#
    number_of_samples = np.shape(sampled_colors)
    number_of_samples = number_of_samples[1]
    # plot the sampled points
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for sample_index in range(number_of_samples):
        ax.scatter(sampled_colors[0,sample_index], sampled_colors[1,sample_index], sampled_colors[2,sample_index], c=np.array([sampled_colors[0,sample_index], sampled_colors[1,sample_index], sampled_colors[2,sample_index]])/255)
    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')
    plt.show()

    # plot the sampled points in sorted order
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for sample_index in range(number_of_samples):
        ax.scatter(sample_index, sample_index, sample_index, c=np.array([sampled_colors[0,sample_index], sampled_colors[1,sample_index], sampled_colors[2,sample_index]])/255)
    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')
    plt.show()
