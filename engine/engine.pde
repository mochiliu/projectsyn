// intialize sound feature extraction
import processing.sound.*;
AudioIn in;
Amplitude amp;
FFT fft;
int bands = 512;
float[] spectrum = new float[bands];

float[] features = new float[1];

// initialize udp port
import hypermedia.net.*;    // import UDP library
UDP udp;  // define the UDP object (sets up)
final String ip       = "192.168.1.247";  // the remote IP address of Host
final int port        = 5005;    // the destination port
final int framerate = 11; // in Hz
final int panel_width = 30;

// initialize motif tree
Motif root_motif;
Motif leaf_motif;

void setup() {
  size(30, 30);
  background(0);
  frameRate(framerate);  
  udp = new UDP(this, 6000);
  udp.setBuffer(panel_width*panel_width*3);
  
  int[] relevant_features = {0};
  leaf_motif = new leafmotif_Circle(5,color(255, 0, 0),5,5,relevant_features);
  root_motif = new nodemotif_Translate(0.01, 0.01, leaf_motif,relevant_features);

  getVolume();
  getFFT();
}      

void draw() {
  //feature extract
  extractFeatures();
 
  background(0);
  root_motif.animate(features);
  image(root_motif.my_graphic,root_motif.xpos,root_motif.ypos);
  send_image();
}

void extractFeatures() {
  features[0] = amp.analyze()*20;
}

void getVolume() {
  // Create amplitude object
  amp = new Amplitude(this);
  // Create the Input stream
  in = new AudioIn(this, 0);
  // to start input audio stream
  in.start();
  amp.input(in); 
}

void getFFT() {
  // Create an Input stream which is routed into the Amplitude analyzer
  fft = new FFT(this, bands);
  in = new AudioIn(this, 0);
  // start the Audio Input
  in.start();
  // patch the AudioIn
  fft.input(in);
}

void send_image() {
  //sends the canvas to the pi via UDP communication
  loadPixels(); 
  byte[] RGB_array = new byte[pixels.length * 3];
  for (int i=0; i < pixels.length; i++) { 
    RGB_array[i*3] = byte(red(pixels[i]));
    RGB_array[i*3+1] = byte(green(pixels[i]));      
    RGB_array[i*3+2] = byte(blue(pixels[i]));
  }    
  //println(RGB_array[0]);
  // send to pi
  udp.send(RGB_array, ip, port);
}