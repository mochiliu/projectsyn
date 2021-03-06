import pyaudio
import struct
import math
import wave
import audioop
import io
from collections import deque
import os
import time
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from clap import ClapAnalyzer


client = speech.SpeechClient()
LANG_CODE = 'en-US'  # Language to use
CHANNELS = 1
RATE = 44100  
CHUNK = 1024 #CHUNKS of bytes to read each time from mic for google cloud speech
THRESHOLD = 3000  # The threshold intensity that defines silence
SILENCE_LIMIT = 2  # Silence limit in seconds to stop the recording
PREV_AUDIO = 0.5  #seconds of audo to prepend to the sending data
MAX_RECORD_TIME = 5 # max seconds to record audio for speech detection

INITIAL_TAP_THRESHOLD = 0.05
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
INPUT_BLOCK_TIME = 0.05 #float(RATE) / CHUNK
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if we get this many noisy blocks in a row, increase the threshold
OVERSENSITIVE = 15.0/INPUT_BLOCK_TIME                    
# if we get this many quiet blocks in a row, decrease the threshold
UNDERSENSITIVE = 120.0/INPUT_BLOCK_TIME 
# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME


def get_rms( block ):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...

    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )


def stt_google_wav(audio_fname):
    """ Sends audio file (audio_fname) to Google's text to speech
        service and returns service's response. We need a FLAC
        converter if audio is not FLAC (check FLAC_CONV). """

    print ("Sending ", audio_fname)
    #Convert to flac first
    with io.open(audio_fname, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)
        config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate_hertz=RATE, language_code=LANG_CODE)
        response = client.recognize(config, audio)
        return response


class VoiceController(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS+1 
        self.quietcount = 0 
        self.errorcount = 0
        self.clap_sequences_detected = False
        self.clap_start_time = time.clock()
        self.clap_analyzer = ClapAnalyzer(
            note_lengths=[1./4, 1./8, 1./8, 1./4, 1./4],
            deviation_threshold=0.2
        )
        self.clap_analyzer.on_clap_sequence(self.clapSequenceCallBack)

    def clapSequenceCallBack(self):
        #print("clap sequence detected")
        self.clap_sequences_detected = True
        
    def tapDetected(self): #One tap DETECTED
        time_diff = time.clock() - self.clap_start_time
        self.clap_analyzer.clap(time_diff)
        print(str(time_diff))

    def resetClapSequence(self):
        self.clap_sequences_detected = False
        self.clap_start_time = time.clock()
        
    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )
            for keyword in ["mic","input","default"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index
        if device_index == None:
            print( "No preferred input found; using default input device." )
        return device_index

    def open_tap_mic_stream( self ):
        device_index = self.find_input_device()
        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)
        self.clap_sequences_detected = False
        self.clap_start_time = time.clock()
        self.stream = stream

    def open_speech_mic_stream( self ):
        device_index = self.find_input_device()
        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = CHUNK)
        self.stream = stream


    def listen_for_tap(self):
#        try:
        block = self.stream.read(INPUT_FRAMES_PER_BLOCK, exception_on_overflow = False)
#        except:
#            # dammit. 
#            self.errorcount += 1
#            print( "(%d) Error recording"%(self.errorcount) )
#            self.noisycount = 1
#            return False

        amplitude = get_rms( block )
        if amplitude > self.tap_threshold:
            # noisy block
            self.quietcount = 0
            self.noisycount += 1
        else:            
            # quiet block.
            if 1 <= self.noisycount <= MAX_TAP_BLOCKS:
                self.tapDetected()

            self.noisycount = 0
            self.quietcount += 1

        return self.clap_sequences_detected

    def listen_for_speech(self):
        #Open stream
        self.open_speech_mic_stream()
        print ("* Listening mic. ")
        audio2send = []
        cur_data = ''  # current chunk  of audio data
        rel = RATE/CHUNK
        slid_win = deque(maxlen=math.floor(SILENCE_LIMIT * rel))
        #Prepend audio from 0.5 seconds before noise was detected
        prev_audio = deque(maxlen=math.floor(PREV_AUDIO * rel))
        started = False
        response = []
        start_time = time.clock()
        
        while (True):
            cur_data = self.stream.read(CHUNK, exception_on_overflow = False)
            slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
            current_time = time.clock()
            #print slid_win[-1]
            if((sum([x > THRESHOLD for x in slid_win]) > 0) and ((current_time - start_time) < MAX_RECORD_TIME)):
                if(not started):
                    print ("Starting record of phrase")
                    started = True
                    start_time = time.clock()
                audio2send.append(cur_data)
            elif ((current_time - start_time) < MAX_RECORD_TIME):
                prev_audio.append(cur_data)
            elif started is True:
                self.stream.stop_stream()
                self.stop()
                print ("Finished")
                filename = self.save_speech(list(prev_audio) + audio2send)
                response = stt_google_wav(filename)
                os.remove(filename)
                # Remove temp file. Comment line to review.
                return response

    
    def save_speech(self, data):
        filename = 'output_'+str(int(time.time()))
        # writes data to WAV file
        data = b''.join(data)
        wf = wave.open(filename + '.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)  # TODO make this value a function parameter?
        wf.writeframes(data)
        wf.close()
        return filename + '.wav'


if __name__ == "__main__":
    vc = VoiceController()
    vc.find_input_device()


