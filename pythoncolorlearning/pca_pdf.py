# do a PCA on the dataset
pca = PCA(n_components=3)
pca.fit(np.transpose(median_pixels))
pca_std = np.sqrt(pca.explained_variance_)

# generate pdf
color_pdf = np.zeros([256,256,256])
resolution = 8
h_r = int(resolution / 2)
for r_index in range(h_r,256-h_r+1,resolution):
    for g_index in range(h_r,256-h_r+1,resolution):
        for b_index in range(h_r,256-h_r+1,resolution):
            # get new coordinate system
            new_coordinates_lower_bound = np.squeeze(pca.transform(np.array([[r_index-h_r,g_index-h_r,b_index-h_r]])))
            new_coordinates_upper_bound = np.squeeze(pca.transform(np.array([[r_index+h_r,g_index+h_r,b_index+h_r]])))
            # rescale to std
            coordinate_stds_lower_bound = new_coordinates_lower_bound / pca_std
            coordinate_stds_upper_bound = new_coordinates_upper_bound / pca_std
            # find cdf for each dimension and multiply them
            r_pixel_cum_prob = abs(norm.cdf(coordinate_stds_lower_bound[0]) - norm.cdf(coordinate_stds_upper_bound[0]))
            g_pixel_cum_prob = abs(norm.cdf(coordinate_stds_lower_bound[1]) - norm.cdf(coordinate_stds_upper_bound[1]))
            b_pixel_cum_prob = abs(norm.cdf(coordinate_stds_lower_bound[2]) - norm.cdf(coordinate_stds_upper_bound[2]))
            color_pdf[r_index-h_r:r_index+h_r, g_index-h_r:g_index+h_r, b_index-h_r:b_index+h_r] = r_pixel_cum_prob*g_pixel_cum_prob*b_pixel_cum_prob/np.double(resolution*resolution*resolution)
    print(r_index)
    
# generate pdf with edge probs
resolution = 8
small_color_pdf = np.zeros([256//resolution,256//resolution,256//resolution])
for r_index in range(0,256//resolution):
    for g_index in range(0,256//resolution):
        for b_index in range(0,256//resolution):
            # get new coordinate system
            new_coordinates_lower_bound = np.squeeze(pca.transform(np.array([[r_index*resolution,g_index*resolution,b_index*resolution]])))
            new_coordinates_upper_bound = np.squeeze(pca.transform(np.array([[(r_index+1)*resolution,(g_index+1)*resolution,(b_index+1)*resolution]])))
            # rescale to std
            coordinate_stds_lower_bound = new_coordinates_lower_bound / pca_std
            coordinate_stds_upper_bound = new_coordinates_upper_bound / pca_std
            # find cdf for each dimension and multiply them
            if r_index == 0 or r_index == 256//resolution:
                #at an edge bin
                lowerbound_cdf = norm.cdf(coordinate_stds_lower_bound[0])
                lowerbound_cdf = min(lowerbound_cdf, 1-lowerbound_cdf)
                upperbound_cdf = norm.cdf(coordinate_stds_upper_bound[0])
                upperbound_cdf = min(upperbound_cdf, 1-upperbound_cdf)
                r_pixel_cum_prob = max(lowerbound_cdf,upperbound_cdf)
            else:
                r_pixel_cum_prob = abs(norm.cdf(coordinate_stds_lower_bound[0]) - norm.cdf(coordinate_stds_upper_bound[0]))
                
            if g_index == 0 or g_index == 256//resolution:
                #at an edge bin
                lowerbound_cdf = norm.cdf(coordinate_stds_lower_bound[1])
                lowerbound_cdf = min(lowerbound_cdf, 1-lowerbound_cdf)
                upperbound_cdf = norm.cdf(coordinate_stds_upper_bound[1])
                upperbound_cdf = min(upperbound_cdf, 1-upperbound_cdf)
                g_pixel_cum_prob = max(lowerbound_cdf,upperbound_cdf)
            else:
                g_pixel_cum_prob = abs(norm.cdf(coordinate_stds_lower_bound[1]) - norm.cdf(coordinate_stds_upper_bound[1]))

            if b_index == 0 or b_index == 256//resolution:
                #at an edge bin
                lowerbound_cdf = norm.cdf(coordinate_stds_lower_bound[2])
                lowerbound_cdf = min(lowerbound_cdf, 1-lowerbound_cdf)
                upperbound_cdf = norm.cdf(coordinate_stds_upper_bound[2])
                upperbound_cdf = min(upperbound_cdf, 1-upperbound_cdf)
                b_pixel_cum_prob = max(lowerbound_cdf,upperbound_cdf)
            else:
                b_pixel_cum_prob = abs(norm.cdf(coordinate_stds_lower_bound[2]) - norm.cdf(coordinate_stds_upper_bound[2]))
                
            small_color_pdf[r_index, g_index, b_index] = r_pixel_cum_prob*g_pixel_cum_prob*b_pixel_cum_prob
    print(r_index)
        
color_pdf = ndimage.zoom(small_color_pdf, (8,8,8), order=0)
color_pdf = ndimage.filters.gaussian_filter(color_pdf, resolution, mode='reflect')  
