import processing.sound.*;

// initialize udp port
import hypermedia.net.*;    // import UDP library
UDP udp;  // define the UDP object (sets up)
final String ip       = "192.168.1.247";  // the remote IP address of Host
final int port        = 5005;    // the destination port
final int framerate = 11; // in Hz
final int panel_width = 30;

Motif root_motif;

void setup() {
  size(30, 30);
  background(0);
  frameRate(framerate);  
  udp = new UDP(this, 6000);
  udp.setBuffer(panel_width*panel_width*3);
  
  root_motif = new leafmotif_Circle(5,color(255, 0, 0),15,15,new int[0]);
}      

void draw() {
  background(0);
  root_motif.animate(new float[0]);
  image(root_motif.my_graphic,root_motif.xpos-(root_motif.my_width/2),root_motif.ypos-(root_motif.my_height/2));
  send_image();
}

void send_image() {
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