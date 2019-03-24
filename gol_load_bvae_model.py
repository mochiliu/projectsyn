# coding: utf-8
import os
import tensorflow as tf
from tensorflow.python.keras import backend as K
from tensorflow.python.keras.models import Model
#from keras.models import load_model

import numpy as np
from PIL import Image
from simple_models import OptimalEncoder, OptimalDecoder

class AutoEncoder(object):
    def __init__(self, encoderArchitecture, 
                 decoderArchitecture):
        self.encoder = encoderArchitecture.model
        self.decoder = decoderArchitecture.model
        self.ae = Model(self.encoder.inputs, self.decoder(self.encoder.outputs))

fit_path = 'C:\\Users\\Mochi\\Dropbox\\personal stuff\\BVAE-tf\\output_models\\'
epoch_number = '100'

encoder_model_path = os.path.join(fit_path + epoch_number + '_encoder.h5')
decoder_model_path = os.path.join(fit_path + epoch_number + '_decoder.h5')
ae_model_path = os.path.join(fit_path + epoch_number +  '_autoencoder.h5')

batchSize = 4*64
inputShape = (32, 32, 3)
intermediateSize = 900
latentSize = 32


# This is how you build the autoencoder
encoder = OptimalEncoder(inputShape, batchSize, latentSize, intermediateSize, 'vae', beta=69, capacity=15, randomSample=True)
decoder = OptimalDecoder(inputShape, batchSize, latentSize, intermediateSize)
bvae = AutoEncoder(encoder, decoder)

bvae.ae.compile(optimizer='adam', loss='mean_absolute_error')

#bvae.ae.load_weights(ae_model_path)
bvae.encoder.load_weights(encoder_model_path)
bvae.decoder.load_weights(decoder_model_path)
#
bvae.ae.summary()
bvae.encoder.summary()
bvae.decoder.summary()

latentVec = np.zeros((batchSize,latentSize), dtype=np.float32)

for dim in range(latentSize):
    for shift in range(-200, 201, 200):
        latentVecPrime = latentVec.copy()
        latentVecPrime[0][dim] = latentVecPrime[0][dim] + shift
        #latentVecPrime[0][1] = latentVecPrime[0][1] + 5
        pred = bvae.decoder.predict(latentVecPrime, batch_size=batchSize)[0] # get the reconstructed image

        pred[pred > 0.5] = 0.5 # clean it up a bit
        pred[pred < -0.5] = -0.5
        pred = np.uint8((pred + 0.5)* 255) # convert to regular image values
        
        pred_img = Image.fromarray(pred)
    #    pred_img.show()
        pred_img.save(fit_path + epoch_number + 'epoch_' + str(dim) + 'dim_' + str(shift) + 'shift.bmp')