import processing.sound.*;
AudioIn in;
Amplitude amp;

void setup() {

  // Create amplitude object
  amp = new Amplitude(this);
  
  // Create the Input stream
  in = new AudioIn(this, 0);
  
  // to start input audio stream
  in.start();
  
  // to get amplitude or "volume" of the input stream
  amp.input(in);
}      