# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 20:58:55 2018

@author: Mochi
"""
import os
import cv2
import numpy as np
from scipy.spatial.distance import cdist, euclidean
from google_images_download import google_images_download   #importing the library
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from scipy.stats import norm
from scipy import ndimage
import shutil

pca_pdf = True
color_resolution = 8
num_traing_imgs = 100
cwd = os.getcwd()
imagedir = os.path.join(cwd, 'images')
search_term = "yellow"
search_term_plus_color = search_term +' color'
edge_pdf_limit = 0.3

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

response = google_images_download.googleimagesdownload()   #class instantiation
arguments = {"keywords":search_term_plus_color,"limit":num_traing_imgs,"print_urls":True,"output_directory":imagedir,"no_numbering":True,"no_directory":True}   #creating list of arguments
paths = response.download(arguments)   #passing the arguments to the function
#print(paths)   #printing absolute paths of the downloaded images

median_pixels = np.zeros((3,len(paths[search_term_plus_color])))
image_index = 0
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
                    print(image_index)
                    image_index += 1
        except:
            print('error loading file')
            
median_pixels = np.int16(median_pixels[:,0:image_index])
# plot the points in color space
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for sample_index in range(image_index):
    ax.scatter(median_pixels[0,sample_index], median_pixels[1,sample_index], median_pixels[2,sample_index], c=np.array([median_pixels[0,sample_index], median_pixels[1,sample_index], median_pixels[2,sample_index]])/255)
ax.set_xlabel('Red')
ax.set_ylabel('Green')
ax.set_zlabel('Blue')
plt.show()


#color_pdf = np.zeros([256,256,256],dtype=float)
small_color_pdf = np.zeros([256//color_resolution,256//color_resolution,256//color_resolution])
if pca_pdf:
    # do a PCA on the dataset
    pca = PCA(n_components=3)
    pca.fit(np.transpose(median_pixels))
    pca_std = np.sqrt(pca.explained_variance_)
    
    edge_pdf_sum = 0
    # generate pdf with edge probs, but only for dimensions with small variance
    for r_index in range(0,256//color_resolution):
        for g_index in range(0,256//color_resolution):
            for b_index in range(0,256//color_resolution):
                # get new coordinate system
                new_coordinates_lower_bound = np.squeeze(pca.transform(np.array([[r_index*color_resolution,g_index*color_resolution,b_index*color_resolution]])))
                new_coordinates_upper_bound = np.squeeze(pca.transform(np.array([[(r_index+1)*color_resolution,(g_index+1)*color_resolution,(b_index+1)*color_resolution]])))
                # rescale to std
                coordinate_stds_lower_bound = -np.abs(new_coordinates_lower_bound / pca_std)
                coordinate_stds_upper_bound = -np.abs(new_coordinates_upper_bound / pca_std)

                if r_index == 0 or r_index == 256//color_resolution-1 or g_index == 0 or g_index == 256//color_resolution-1 or b_index == 0 or b_index == 256//color_resolution-1:
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
    if edge_pdf_sum / small_color_pdf_sum > edge_pdf_limit:
        #the edges have more than the threshold probability, bring it down to the limit
        middle_sum = (small_color_pdf_sum-edge_pdf_sum)
        total_target = middle_sum / (1-edge_pdf_limit)
        edge_target = total_target - middle_sum
        correction_factor = edge_target/edge_pdf_sum
        for r_index in range(0,256//color_resolution):
            for g_index in range(0,256//color_resolution):
                for b_index in range(0,256//color_resolution):
                    if r_index == 0 or r_index == 256//color_resolution-1 or g_index == 0 or g_index == 256//color_resolution-1 or b_index == 0 or b_index == 256//color_resolution-1:
                        small_color_pdf[r_index, g_index, b_index] = small_color_pdf[r_index, g_index, b_index] * correction_factor
#    color_pdf = ndimage.zoom(small_color_pdf, (8,8,8), order=0)
#    color_pdf = ndimage.filters.gaussian_filter(color_pdf, color_resolution, mode='reflect')  
else:
    #generate pdf by blurring sampled data
    for sample_index in range(image_index): 
        small_color_pdf[median_pixels[0,sample_index]//color_resolution,median_pixels[1,sample_index]//color_resolution,median_pixels[2,sample_index]//color_resolution] = small_color_pdf[median_pixels[0,sample_index]//color_resolution,median_pixels[1,sample_index]//color_resolution,median_pixels[2,sample_index]//color_resolution] + 1
    small_color_pdf = ndimage.filters.gaussian_filter(small_color_pdf, 24//color_resolution, mode='reflect')
    
#renormalize color_pdf
small_color_pdf = small_color_pdf / np.sum(small_color_pdf)

#sample from pdf and display some points
number_of_samples = 100
sampled_colors = np.zeros([3,number_of_samples])
#linearize pdf
linearized_pdf_cumsum = np.cumsum(small_color_pdf.flatten())
for sample_index in range(number_of_samples):
    sampled_index = np.argmax(linearized_pdf_cumsum > np.random.uniform())
    sampled_color = np.array(np.unravel_index(sampled_index, (256//color_resolution, 256//color_resolution, 256//color_resolution)))
    sampled_color = sampled_color * color_resolution
    sampled_colors[:,sample_index] = sampled_color
    
# plot the sampled points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for sample_index in range(number_of_samples):
    ax.scatter(sampled_colors[0,sample_index], sampled_colors[1,sample_index], sampled_colors[2,sample_index], c=np.array([sampled_colors[0,sample_index], sampled_colors[1,sample_index], sampled_colors[2,sample_index]])/255)
ax.set_xlabel('Red')
ax.set_ylabel('Green')
ax.set_zlabel('Blue')
plt.show()


#show green-blue projection
green_blue_cdf = np.squeeze(np.sum(small_color_pdf, axis=0))
plt.imshow(green_blue_cdf);
plt.xlabel('Blue')
plt.ylabel('Green')
plt.colorbar()
plt.show()

#show red-blue projection
red_blue_cdf = np.squeeze(np.sum(small_color_pdf, axis=1))
plt.imshow(red_blue_cdf);
plt.xlabel('Blue')
plt.ylabel('Red')
plt.colorbar()
plt.show()

#show red-green projection
red_green_cdf = np.squeeze(np.sum(small_color_pdf, axis=2))
plt.imshow(red_green_cdf);
plt.xlabel('Green')
plt.ylabel('Red')
plt.colorbar()
plt.show()

save_path = os.path.join(cwd, search_term+'.npy')
np.save(save_path,small_color_pdf)

shutil.rmtree(imagedir)
#small_color_pdf = np.load(save_path)
