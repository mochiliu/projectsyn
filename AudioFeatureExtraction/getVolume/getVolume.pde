import processing.sound.*;
AudioIn in;
Amplitude amp;

void getVolume() {
  // Create amplitude object
  amp = new Amplitude(this);
  
  // Create the Input stream
  in = new AudioIn(this, 0);
  
  // to start input audio stream
  in.start();
  amp.input(in); 
}