import hypermedia.net.*;    // import UDP library
import java.nio.ByteBuffer;
import java.nio.IntBuffer;

PGraphics pg;
UDP udp;  // define the UDP object (sets up)
String ip       = "192.168.1.247";  // the remote IP address of Host
int port        = 5005;    // the destination port

void setup() {
  size(30,30);
  pg = createGraphics(30, 30);
  frameRate(11);
  udp = new UDP( this, 6000 );
  udp.setBuffer(2700);
}



void draw() {
  background(0);
  pg.beginDraw();
  pg.stroke(0, 255, 0);
  pg.line(0, 0, mouseX, mouseY);
  pg.endDraw();
  image(pg, 0, 0); 

  
  // formats the message for Pd
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
  
}    //process events



  

void mousePressed (){

    // ellipse(mouseX, mouseY, 5, 5);
    pg.beginDraw(); 
    pg.clear();
    pg.endDraw(); 
    


  
}