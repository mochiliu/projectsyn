import processing.sound.*;
AudioIn in;
Amplitude amp;

void setup() {
  size(30, 30);
  background(0);
    
  // Create amplitude object
  amp = new Amplitude(this);
  
  // Create the Input stream
  in = new AudioIn(this, 0);
  
  // to start playing what is coming into mic
  //in.play();
  
  // to start input audio stream
  in.start();
  amp.input(in);
}      

void draw() {
  println(amp.analyze());
  //ellipse(100,100,100,100);
}

//void mousePressed(){
//  in.set(mouseX);
//}