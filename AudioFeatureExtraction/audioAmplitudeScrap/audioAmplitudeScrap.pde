import processing.sound.*;
AudioIn in;
Amplitude amp;
FFT fft;
int bands = 512;
float[] spectrum = new float[bands];

int[] colors = new int[255];{
for (int i=0;i <255;++i){
colors[i]=i;
}}

import hypermedia.net.*;    // import UDP library
import java.nio.ByteBuffer;
import java.nio.IntBuffer;
PGraphics pg;
UDP udp;  // define the UDP object (sets up)
String ip       = "192.168.1.247";  // the remote IP address of Host
int port        = 5005;    // the destination port

void setup() {
  size(30, 30);
  surface.setResizable(true);
  background(0);
  frameRate(11);
  
  udp = new UDP( this, 6000 );
  udp.setBuffer(2700);
  
  getVolume();
  
  getFFT();
  
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


void draw() {
  
  //println(amp.analyze());
  
  int scale=1000;
  float vol = amp.analyze();
  float radius = vol*scale;
  
  fill(0,0,0);
  ellipse(mouseX,mouseY,radius, radius);
  
  fill(0,255,0);
  ellipse(mouseX-5,mouseY-5,radius,radius);
  
  fill(0,0,255);
  ellipse(mouseX+5,mouseY+5,radius,radius);
  
  fill(255,255,0);
  ellipse(mouseX+5,mouseY-5,radius,radius);
  
  fill(0,255,255);
  ellipse(mouseX-5,mouseY+5,radius,radius);
  
  fill(255,255,255);
  ellipse(mouseX,mouseY+7.07,radius/2,radius/2);
  
  fill(255,255,255);
  ellipse(mouseX,mouseY-7.07,radius/2,radius/2);
  
  fill(255,255,255);
  ellipse(mouseX+7.07,mouseY,radius/2,radius/2);
  
  fill(255,255,255);
  ellipse(mouseX-7.07,mouseY,radius/2,radius/2);
  
  //background(0);
  
  
  //background(255);
  fft.analyze(spectrum);

  for(int i = 0; i < 30; i++){
  // The result of the FFT is normalized
  // draw the line for frequency band i scaling it up by 5 to get more amplitude.
  stroke(colors[i*8],0,0);
  println(colors[i*8]);
  //println(i);
  line( i, height, i, height - spectrum[i]*height*70 );
  } 
  
  
  
  
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