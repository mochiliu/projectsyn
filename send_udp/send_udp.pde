import hypermedia.net.*;    // import UDP library
import java.nio.ByteBuffer;
import java.nio.IntBuffer;

PGraphics pg;
UDP udp;  // define the UDP object (sets up)

void setup() {
  size(30,30);
  pg = createGraphics(30, 30);

  udp = new UDP( this, 6000 );
  udp.setBuffer(2700);
}



void draw() {
  background(204);
  pg.beginDraw();
  pg.stroke(0, 102, 153);
  pg.line(0, 0, mouseX, mouseY);
  pg.endDraw();
  image(pg, 0, 0); 
//  PImage img = pg.get();

  
}    //process events



  

void mousePressed (){
     String ip       = "192.168.1.247";  // the remote IP address of Host
     int port        = 5005;    // the destination port
    
    // formats the message for Pd
     loadPixels(); 
    //color[] message = pixels;
     ByteBuffer byteBuffer = ByteBuffer.allocate(pixels.length * 4);       
     IntBuffer intBuffer = byteBuffer.asIntBuffer();
     intBuffer.put(pixels);
    
    byte[] ARGB_array = byteBuffer.array();
    byte[] RGB_array = new byte[pixels.length * 3];
    for (int i=0; i < pixels.length; i++) {         
      RGB_array[i*3] = ARGB_array[i*4];
      RGB_array[i*3+1] = ARGB_array[i*4+1];      
      RGB_array[i*3+2] = ARGB_array[i*4+2];
    }    
    println(RGB_array);
    // send the message
    
    udp.send(RGB_array , ip, port );
    // ellipse(mouseX, mouseY, 5, 5);
    pg.beginDraw(); 
    pg.clear();
    pg.endDraw(); 
    


  
}