import hypermedia.net.*;    // import UDP library
import processing.video.*;
Movie myMovie;
float gamma = 1.2;
float thresh = 50;

UDP udp;  // define the UDP object (sets up)
String ip       = "192.168.1.247";  // the remote IP address of Host
int port        = 5005;    // the destination port
String movieFile;

void fileSelected(File selection) {
  if (selection == null) {
    println("Window was closed or the user hit cancel.");
  } else {
    movieFile = selection.getAbsolutePath();
  }
}

void setup() {
  size(30,30);
  frameRate(1);
  udp = new UDP( this, 6000 );
  udp.setBuffer(2700);
  selectInput("Select a file to process:", "fileSelected");
  delay(10000);
  myMovie = new Movie(this, movieFile);
  myMovie.play();
}



void draw() {
  
  image(myMovie, -625, -345);
  send_image();
}    //process events

void movieEvent(Movie m) {
  m.read();
}


void send_image() {
  //sends the canvas to the pi via UDP communication
  float gammaCorrection = 1 / gamma;
  loadPixels(); 
  byte[] RGB_array = new byte[pixels.length * 3];
  for (int i=0; i < pixels.length; i++) {
    int red_val = int(pow(255*(red(pixels[i])/255),gammaCorrection));
    if (red_val < thresh) {
      red_val = 0;
    }
    int green_val = int(pow(255*(green(pixels[i])/255),gammaCorrection));
    if (green_val < thresh) {
      green_val = 0;
    }
    int blue_val = int(pow(255*(blue(pixels[i])/255),gammaCorrection));
    if (blue_val < thresh) {
      blue_val = 0;
    }
    
    RGB_array[i*3] = byte(red_val);
    RGB_array[i*3+1] = byte(green_val);      
    RGB_array[i*3+2] = byte(blue_val);
  }    
  //println(RGB_array[0]);
  // send to pi
  udp.send(RGB_array, ip, port);
 
}

  