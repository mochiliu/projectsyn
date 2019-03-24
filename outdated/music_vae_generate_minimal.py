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

from magenta import music as mm
from magenta.models.music_vae import configs
from magenta.models.music_vae import TrainedModel
import numpy as np
import tensorflow as tf

flags = tf.app.flags
logging = tf.logging
FLAGS = flags.FLAGS
cwd = os.getcwd()

if os.name == 'nt':
    flags.DEFINE_string(
        'checkpoint_file', 'C:\\Users\\Mochi\\Downloads\\hierdec-mel_16bar.tar',
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
    'config', 'hierdec-mel_16bar',
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
    'temperature', 0.5,
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


logging.info('Loading model...')
checkpoint_dir_or_path = os.path.expanduser(FLAGS.checkpoint_file)


class MusicVAE:
    def __init__(self):
        self.model = TrainedModel(
            config, batch_size=min(FLAGS.max_batch_size, FLAGS.num_outputs),
            checkpoint_dir_or_path=checkpoint_dir_or_path)
        self.z_size=config.hparams.z_size
        self.max_seq_len = config.hparams.max_seq_len
        
    def decode_model(self,z):
        results = self.model.decode(
            length=config.hparams.max_seq_len,
            z=z,
            temperature=FLAGS.temperature)
        for i, ns in enumerate(results):
            return ns.notes
        
    def random_sample_model(self):
        z=np.random.normal(size=(1,self.z_size)) #random z
        ns = self.decode_model(z)
        return ns

if __name__ == '__main__':
    test = MusicVAE()
    ns = test.random_sample_model()
    print(ns)
    #exit()
    
