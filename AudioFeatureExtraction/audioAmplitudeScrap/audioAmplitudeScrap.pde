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
  fill(0,255,0);
  ellipse(mouseX,mouseY,amp.analyze()*500,amp.analyze()*500);
  fill(255,0,0);
  ellipse(mouseX-5,mouseY-5,amp.analyze()*500,amp.analyze()*500);
  fill(0,0,255);
  ellipse(mouseX+5,mouseY+5,amp.analyze()*500,amp.analyze()*500);
  
  fill(255,255,0);
  ellipse(mouseX+5,mouseY-5,amp.analyze()*500,amp.analyze()*500);
  fill(0,255,255);
  ellipse(mouseX-5,mouseY+5,amp.analyze()*500,amp.analyze()*500);
  //background(0);
}

//void mousePressed(){
//  in.set(mouseX);
//}