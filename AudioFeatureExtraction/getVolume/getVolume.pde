import processing.sound.*;
AudioIn in;
Amplitude amp;

float getVolume() {
  // Create amplitude object
  amp = new Amplitude(this);
  
  // Create the Input stream
  in = new AudioIn(this,0);
  
  // to start playing what is coming into mic
  //in.play();
  
  // to start input audio stream
  in.start();
  amp.input(in);
  
  float vol;
  vol = amp.analyze();
  return vol;
}