// intialize sound feature extraction
import processing.sound.*;
AudioIn in;
Amplitude amp;
FFT fft;
int bands = 512;
float[] spectrum = new float[bands];

interface feature_descriptions {
  int
  constant = 0, 
  audio_amplitude = 1;
  
}
float[] features = new float[2];


void setup_features() {
  getVolume();
  //getFFT();
  features[feature_descriptions.constant] = 1; // the first feature is a constant
}

void extract_features() {
  features[feature_descriptions.audio_amplitude] = amp.analyze()*500;
  
}

void getVolume() {
  // Create amplitude object
  amp = new Amplitude(this);
  // Create the Input stream
//  in = new AudioIn(this, 0); //microphone
  in = new AudioIn(this, 1); //stereo mix
  // to start input audio stream
  in.start();
  amp.input(in); 
}

void getFFT() {
  // Create an Input stream which is routed into the Amplitude analyzer
  fft = new FFT(this, bands);
  in = new AudioIn(this, 1);
  // start the Audio Input
  in.start();
  // patch the AudioIn
  fft.input(in);
}//set up features
