'''
models.py
contains models for use with the BVAE experiments.

created by shadySource

THE UNLICENSE
'''
import tensorflow as tf
import numpy as np
from tensorflow.python.keras import Input
from tensorflow.python.keras.layers import (InputLayer, Dense, Conv2D, Conv2DTranspose,
            BatchNormalization, LeakyReLU, MaxPool2D, UpSampling2D,
            Reshape, MaxPooling2D, GlobalAveragePooling2D,Flatten)
from tensorflow.python.keras.models import Model

from model_utils_mod import SampleLayer

class Architecture(object):
    '''
    generic architecture template
    '''
    def __init__(self, inputShape=None, batchSize=None, latentSize=None, intermediateSize=900):
        '''
        params:
        ---------
        inputShape : tuple
            the shape of the input, expecting 3-dim images (h, w, 3)
        batchSize : int
            the number of samples in a batch
        latentSize : int
            the number of dimensions in the two output distribution vectors -
            mean and std-deviation
        '''
        self.inputShape = inputShape
        self.batchSize = batchSize
        self.latentSize = latentSize
        self.intermediateSize = intermediateSize

        self.model = self.Build()

    def Build(self):
        raise NotImplementedError('architecture must implement Build function')


class Encoder(Architecture):
    def __init__(self, inputShape=(256, 256, 3), batchSize=1,
                 latentSize=1000, latentConstraints='bvae', beta=100., capacity=0.,
                 randomSample=True):
        '''
        params
        -------
        latentConstraints : str
            Either 'bvae', 'vae', or 'no'
            Determines whether regularization is applied
                to the latent space representation.
        beta : float
            beta > 1, used for 'bvae' latent_regularizer
            (Unused if 'bvae' not selected, default 100)
        capacity : float
            used for 'bvae' to try to break input down to a set number
                of basis. (e.g. at 25, the network will try to use 
                25 dimensions of the latent space)
            (unused if 'bvae' not selected)
        randomSample : bool
            whether or not to use random sampling when selecting from distribution.
            if false, the latent vector equals the mean, essentially turning this into a
                standard autoencoder.
        '''
        self.latentConstraints = latentConstraints
        self.beta = beta
        self.latentCapacity = capacity
        self.randomSample = randomSample
        super().__init__(inputShape, batchSize, latentSize)

    def Build(self):
        # create the input layer for feeding the netowrk
        inLayer = Input(self.inputShape)
        net = Reshape((np.prod(self.inputShape),))(inLayer)
        #net = Dense(self.latentSize, activation='relu')(net)
        
        mean = Dense(self.latentSize, activation='relu')(net)
        stddev = Dense(self.latentSize, activation='relu')(net)
#        net = Dense(self.intermediateSize, activation='relu')(inLayer)

#        # variational encoder output (distributions)
#        mean = Conv2D(filters=self.latentSize, kernel_size=(1, 1),
#                      padding='same')(net)
#        mean = GlobalAveragePooling2D()(mean)
#        stddev = Conv2D(filters=self.latentSize, kernel_size=(1, 1),
#                        padding='same')(net)
#        stddev = GlobalAveragePooling2D()(stddev)

        sample = SampleLayer(self.latentConstraints, self.beta,
                            self.latentCapacity, self.batchSize, self.latentSize, self.randomSample)([mean, stddev])

        return Model(inputs=inLayer, outputs=sample) #variational
        #return Model(inLayer, net) #nonvariational

class Decoder(Architecture):
    def __init__(self, inputShape=(256, 256, 3), batchSize=1, latentSize=1000):
        super().__init__(inputShape, batchSize, latentSize)

    def Build(self):
        # input layer is from GlobalAveragePooling:
        inLayer = Input([self.latentSize])
        # reexpand the input from flat:
        net = Dense(self.intermediateSize, activation='relu')(inLayer)
        net = Dense(np.prod(self.inputShape), activation='sigmoid')(net)
        net = Reshape(self.inputShape)(net)
        
        return Model(inLayer, net)

class ConvEncoder(Architecture):
    '''
    This encoder predicts distributions then randomly samples them.
    Regularization may be applied to the latent space output

    a simple, fully convolutional architecture inspried by 
        pjreddie's darknet architecture
    https://github.com/pjreddie/darknet/blob/master/cfg/darknet19.cfg
    '''
    def __init__(self, inputShape=(256, 256, 3), batchSize=1,
                 latentSize=1000, latentConstraints='bvae', beta=100., capacity=0.,
                 randomSample=True):
        
        self.latentConstraints = latentConstraints
        self.beta = beta
        self.latentCapacity = capacity
        self.randomSample = randomSample
        super().__init__(inputShape, batchSize, latentSize)

    def Build(self):
        # create the input layer for feeding the netowrk
        inLayer = Input(self.inputShape) #(32,32,3)
        net = Conv2D(32, (3, 3), activation='relu', padding='same')(inLayer)
        net = MaxPooling2D((2, 2), padding='same')(net) #(16,16,3)
        
        net = Conv2D(16, (3, 3), activation='relu', padding='same')(net)
        net = MaxPooling2D((2, 2), padding='same')(net) #(8,8,3)
        
        net = Conv2D(16, (3, 3), activation='relu', padding='same')(net)
        net = MaxPooling2D((2, 2), padding='same')(net) #(4,4,3)
        
        mean = Conv2D(filters=self.latentSize, kernel_size=(1, 1),
                      padding='same')(net) #4*4*3=48
        mean = GlobalAveragePooling2D()(mean)
        stddev = Conv2D(filters=self.latentSize, kernel_size=(1, 1),
                        padding='same')(net)
        stddev = GlobalAveragePooling2D()(stddev)
        


        sample = SampleLayer(self.latentConstraints, self.beta,
                            self.latentCapacity, self.batchSize, self.latentSize, self.randomSample)([mean, stddev])

        return Model(inputs=inLayer, outputs=sample) #variational

class ConvDecoder(Architecture):
    def __init__(self, inputShape=(256, 256, 3), batchSize=1, latentSize=1000):
        super().__init__(inputShape, batchSize, latentSize)

    def Build(self):
        # input layer is from GlobalAveragePooling:
        inLayer = Input([self.latentSize])
        
        net = Reshape((1, 1, self.latentSize))(inLayer)
        # encoder downscales input by a factor of 2^3, so we upsample to the second to last output shape:
        net = UpSampling2D((self.inputShape[0]//8, self.inputShape[1]//8))(net)

        net = Conv2D(16, (3, 3), activation='relu', padding='same')(net)
        net = UpSampling2D((2, 2))(net)
        net = Conv2D(16, (3, 3), activation='relu', padding='same')(net)
        net = UpSampling2D((2, 2))(net)
        net = Conv2D(32, (3, 3), activation='relu', padding='same')(net)
        net = UpSampling2D((2, 2))(net)
        net = Conv2D(3, (3, 3), activation='sigmoid', padding='same')(net)
        
        return Model(inLayer, net)

class OptimalEncoder(Architecture):
    '''
    This encoder predicts distributions then randomly samples them.
    Regularization may be applied to the latent space output

    a simple, fully convolutional architecture inspried by 
        pjreddie's darknet architecture
    https://github.com/pjreddie/darknet/blob/master/cfg/darknet19.cfg
    '''
    def __init__(self, inputShape=(256, 256, 3), batchSize=1,
                 latentSize=1000, intermediateSize=900, latentConstraints='bvae', beta=100., capacity=0.,
                 randomSample=True):
        
        self.latentConstraints = latentConstraints
        self.beta = beta
        self.latentCapacity = capacity
        self.randomSample = randomSample
        self.intermediateSize = intermediateSize
        super().__init__(inputShape, batchSize, latentSize)

    def Build(self):
        # create the input layer for feeding the netowrk
        inLayer = Input(self.inputShape) #(32,32,3)
        net = Conv2D(96, (3, 3), activation='relu', padding='same')(inLayer)
        net = MaxPooling2D((2, 2), padding='same')(net) #(16,16,3)
        
#        net = Conv2D(32, (3, 3), activation='relu', padding='same')(net)
#        net = MaxPooling2D((2, 2), padding='same')(net) #(8,8,3)
        
        net = Flatten()(net)
        net = Dense(self.intermediateSize, activation='relu')(net)
        
        mean = Dense(self.latentSize, activation='relu')(net)
        stddev = Dense(self.latentSize, activation='relu')(net)
#        net = Dense(self.intermediateSize, activation='relu')(inLayer)

#        # variational encoder output (distributions)
#        mean = Conv2D(filters=self.latentSize, kernel_size=(1, 1),
#                      padding='same')(net)
#        mean = GlobalAveragePooling2D()(mean)
#        stddev = Conv2D(filters=self.latentSize, kernel_size=(1, 1),
#                        padding='same')(net)
#        stddev = GlobalAveragePooling2D()(stddev)

        sample = SampleLayer(self.latentConstraints, self.beta,
                            self.latentCapacity, self.batchSize, self.latentSize, self.randomSample)([mean, stddev])

        return Model(inputs=inLayer, outputs=sample) #variational

class OptimalDecoder(Architecture):
    def __init__(self, inputShape=(256, 256, 3), batchSize=1, latentSize=1000, intermediateSize=900):
        self.intermediateSize = intermediateSize
        super().__init__(inputShape, batchSize, latentSize)

    def Build(self):
        # input layer is from sampling:
        inLayer = Input([self.latentSize])
        
        net = Dense(self.intermediateSize, activation='relu')(inLayer)
        net = Dense(16*16*32, activation='relu')(inLayer)
        
        # encoder downscales input by a factor of 2, so we upsample to the second to last output shape:
        net = Reshape((16, 16, 32))(net)
        #net = UpSampling2D((self.inputShape[0]//2, self.inputShape[1]//2))(net)

#        net = Conv2D(32, (3, 3), activation='relu', padding='same')(net)
#        net = UpSampling2D((2, 2))(net)
        net = Conv2D(96, (3, 3), activation='relu', padding='same')(net) #(16,16,96)
        net = UpSampling2D((2, 2))(net)
        net = Conv2D(3, (3, 3), activation='sigmoid', padding='same')(net)
        
        return Model(inLayer, net)



#
#if __name__ == '__main__':
#    test()
