# Copyright 2018 The Magenta Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from magenta.models.music_vae import configs
from magenta.models.music_vae import TrainedModel
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.models import Model
from simple_models import OptimalEncoder, OptimalDecoder

#load musicVAE model
flags = tf.app.flags
logging = tf.logging
FLAGS = flags.FLAGS
cwd = os.getcwd()
if os.name == 'nt':
    flags.DEFINE_string(
        'checkpoint_file', 'C:\\Users\\Mochi\\Downloads\\cat-mel_2bar_big.tar',
        'Path to the checkpoint file. run_dir will take priority over this flag.')
else:
    flags.DEFINE_string(
        'checkpoint_file', cwd + '/hierdec-mel_16bar.tar',
        'Path to the checkpoint file. run_dir will take priority over this flag.')
flags.DEFINE_string(
    'run_dir', None,
    'Path to the directory where the latest checkpoint will be loaded from.')
flags.DEFINE_string(
    'output_dir', cwd,
    'The directory where MIDI files will be saved to.')
flags.DEFINE_string(
    'config', 'cat-mel_2bar_big',
    'The name of the config to use.')
flags.DEFINE_string(
    'mode', 'sample',
    'Generate mode (either `sample` or `interpolate`).')
flags.DEFINE_integer(
    'num_outputs', 1,
    'In `sample` mode, the number of samples to produce. In `interpolate` '
    'mode, the number of steps (including the endpoints).')
flags.DEFINE_integer(
    'max_batch_size', 1,
    'The maximum batch size to use. Decrease if you are seeing an OOM.')
flags.DEFINE_float(
    'temperature', 0.2,
    'The randomness of the decoding process.')
flags.DEFINE_string(
    'log', 'INFO',
    'The threshold for what messages will be logged: '
    'DEBUG, INFO, WARN, ERROR, or FATAL.')
if FLAGS.run_dir is None == FLAGS.checkpoint_file is None:
    raise ValueError('Exactly one of `--run_dir` or `--checkpoint_file` must be specified.')
logging.set_verbosity(FLAGS.log)
config_map = configs.CONFIG_MAP
if FLAGS.config not in config_map:
    raise ValueError('Invalid config name: %s' % FLAGS.config)
config = config_map[FLAGS.config]
config.data_converter.max_tensors_per_item = None
logging.info('Loading MusicVAE model...')
checkpoint_dir_or_path = os.path.expanduser(FLAGS.checkpoint_file)

#load Game of Life decoder
class AutoEncoder(object):
    def __init__(self, encoderArchitecture, 
                 decoderArchitecture):
        self.encoder = encoderArchitecture.model
        self.decoder = decoderArchitecture.model
        self.ae = Model(self.encoder.inputs, self.decoder(self.encoder.outputs))
        
fit_path = 'C:\\Users\\Mochi\\Dropbox\\personal stuff\\BVAE-tf\\output_models\\'
epoch_number = '100'

gol_encoder_model_path = os.path.join(fit_path + epoch_number + '_encoder.h5')
#gol_decoder_model_path = os.path.join(fit_path + epoch_number + '_decoder.h5')
batchSize = 4*64
inputShape = (32, 32, 3)
intermediateSize = 900
latentSize = 32

#bvae.decoder.load_weights(decoder_model_path)

def gram_schmidt(vectors):
    #gets a set of orthonormal vectors in euclidean space from any set of spanning vectors
    basis = []
    for v in vectors:
        w = v - sum( np.dot(v,b)*b  for b in basis )
        if (w > 1e-10).any():
            basis.append(w/np.linalg.norm(w))
    return np.array(basis)

def rand_subspace(num_vec, num_dim):
    #gets a random set of num_vec orthonormal vectors in num_dim space
    vecs = np.random.uniform(size=(num_vec,num_dim))
    return gram_schmidt(vecs)
    

class Life2Music:
    def __init__(self):
        self.music_vae_model = TrainedModel(
            config, batch_size=min(FLAGS.max_batch_size, FLAGS.num_outputs),
            checkpoint_dir_or_path=checkpoint_dir_or_path)
        self.music_vae_z_size=config.hparams.z_size
        self.music_squence_length = config.hparams.max_seq_len
        
        self.gol_bvae_z_size = latentSize
        gol_encoder = OptimalEncoder(inputShape, batchSize, latentSize, intermediateSize, 'vae', beta=69, capacity=15, randomSample=True)
        gol_decoder = OptimalDecoder(inputShape, batchSize, latentSize, intermediateSize)
        self.gol_bvae = AutoEncoder(gol_encoder, gol_decoder)
        self.gol_bvae.ae.compile(optimizer='adam', loss='mean_absolute_error')
        self.gol_bvae.encoder.load_weights(gol_encoder_model_path)
        self.random_subspace = rand_subspace(self.gol_bvae_z_size, self.music_vae_z_size)
        
        self.music_seed_z = np.random.normal(size=self.music_vae_z_size)
        self.scaling = 0.5
        
    def make_music_from_GOL(self, img):
        lifez = self.encode_GOL(img)
        music_z_delta = np.dot(lifez,self.random_subspace) #maybe scale?
        music_z = self.scaling*music_z_delta + self.music_seed_z 
        return self.decode_MVAE(music_z)
        
    def encode_GOL(self, img):
        img_shape = np.shape(img)
        batched_img = np.zeros((batchSize, img_shape[0], img_shape[1], img_shape[2]), dtype=np.float32)
        batched_img[0,:,:,:] = img
        return self.gol_bvae.encoder.predict(batched_img, batch_size=batchSize)[0]
        
    def decode_MVAE(self, z):
        z = np.reshape(z,(1,self.music_vae_z_size))
        results = self.music_vae_model.decode(
            length=config.hparams.max_seq_len,
            z=z,
            temperature=FLAGS.temperature)
        for i, ns in enumerate(results):
            return ns.notes
        
    def random_music_sample(self):
        z=np.random.normal(size=(1,self.music_vae_z_size)) #random z
        ns = self.decode_model(z)
        return ns

if __name__ == '__main__':
    test = Life2Music()
    ns = test.make_music_from_GOL(np.zeros((32,32,3), dtype=np.float32))
    print(ns)
    #exit()
    
