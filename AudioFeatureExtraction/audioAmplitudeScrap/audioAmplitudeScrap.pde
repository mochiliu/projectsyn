import processing.sound.*;
AudioIn in;
Amplitude amp;

import hypermedia.net.*;    // import UDP library
import java.nio.ByteBuffer;
import java.nio.IntBuffer;

PGraphics pg;
UDP udp;  // define the UDP object (sets up)
String ip       = "192.168.1.247";  // the remote IP address of Host
int port        = 5005;    // the destination port

void setup() {
  size(30, 30);
  background(0);
  frameRate(11);
  
  udp = new UDP( this, 6000 );
  udp.setBuffer(2700);
  
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
  
  loadPixels(); 
  byte[] RGB_array = new byte[pixels.length * 3];
  for (int i=0; i < pixels.length; i++) { 
    RGB_array[i*3] = byte(red(pixels[i]));
    RGB_array[i*3+1] = byte(green(pixels[i]));      
    RGB_array[i*3+2] = byte(blue(pixels[i]));
  }    
  //println(byte(int(red(pixels[0]))));
  //println(RGB_array[0]);
  // send the message
  
  udp.send(RGB_array, ip, port );
}

//void mousePressed(){
//  in.set(mouseX);
//}