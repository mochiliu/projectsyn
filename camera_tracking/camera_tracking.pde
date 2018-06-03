// Daniel Shiffman
// http://codingtra.in
// http://patreon.com/codingtrain
// Code for: https://youtu.be/o1Ob28sF0N8

import processing.video.*;

Capture video;

int blobCounter = 0;

int maxLife = 50;

color trackColor = color(255, 255, 255); // 183.0 12.0 83.0
float threshold = 25; //distance in color space
float distThreshold = 5;
float sizeThreshold = 30;
int camera_width = 176;
int camera_height = 144;
int canvas_width;
int canvas_height;

PGraphics reflected_video;
ArrayList<Blob> blobs = new ArrayList<Blob>();


// initialize udp port
import hypermedia.net.*;    // import UDP library
UDP udp;  // define the UDP object (sets up)
final String ip       = "192.168.1.247";  // the remote IP address of Host
final int port        = 5005;    // the destination port
final int framerate = 11; // in Hz
final int panel_width = 30;

void setup() {
  fullScreen(2);
  canvas_width = width;
  canvas_height = height;
  String[] cameras = Capture.list();
  printArray(cameras);
  video = new Capture(this, cameras[5]);
  video.start();
  
  //frameRate(framerate);  
  udp = new UDP(this, 6000);
  udp.setBuffer(panel_width*panel_width*3);
}

void captureEvent(Capture video) {
  video.read();
}

void keyPressed() {
  if (key == 'a') {
    distThreshold+=5;
  } else if (key == 'z') {
    distThreshold-=5;
  }
  if (key == 's') {
    threshold+=5;
  } else if (key == 'x') {
    threshold-=5;
  }
}

void mousePressed() {
  // Save color where the mouse is clicked in trackColor variable
  int loc = mouseX + mouseY*reflected_video.width;
  trackColor = reflected_video.pixels[loc];
  println(red(trackColor), green(trackColor), blue(trackColor));
}

void draw() {
  clear();
  background(0);
  //rotate(HALF_PI);
  video.loadPixels();
  if (video.width > 0) {
    //make sure we are receiving a stream 

    track();
    //image(reflected_video, 0, 0);

    for (Blob b : blobs) {
      b.relative_show();
    } 
    
    //send_image();
  }
}


float distSq(float x1, float y1, float x2, float y2) {
  float d = (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1);
  return d;
}


float distSq(float x1, float y1, float z1, float x2, float y2, float z2) {
  float d = (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) +(z2-z1)*(z2-z1);
  return d;
}


void track() {
  ArrayList<Blob> currentBlobs = new ArrayList<Blob>();
  camera_width = video.width;
  camera_height = video.height;

  //reflect the image horizontally
  reflected_video = createGraphics(camera_width, camera_height);
  reflected_video.beginDraw();
  reflected_video.pushMatrix();
  reflected_video.translate(0,video.height);
  reflected_video.scale(1,-1); 
  reflected_video.image(video, 0, 0);
  reflected_video.endDraw();
    
  // Begin loop to walk through every pixel
  for (int x = 0; x < reflected_video.width; x++ ) {
    for (int y = 0; y < reflected_video.height; y++ ) {
      int loc = x + y * reflected_video.width;
      // What is current color
      color currentColor = reflected_video.pixels[loc];
      float r1 = red(currentColor);
      float g1 = green(currentColor);
      float b1 = blue(currentColor);
      float r2 = red(trackColor);
      float g2 = green(trackColor);
      float b2 = blue(trackColor);

      float d = distSq(r1, g1, b1, r2, g2, b2); 

      if (d < threshold*threshold) {
        boolean found = false;
        for (Blob b : currentBlobs) {
          if (b.isNear(x, y)) {
            b.add(x, y);
            found = true;
            break;
          }
        }

        if (!found) {
          Blob b = new Blob(x, y);
          currentBlobs.add(b);
        }
      }
    }
  }

  for (int i = currentBlobs.size()-1; i >= 0; i--) {
    //remove any objects smaller than a preset size
    if (currentBlobs.get(i).size() < sizeThreshold) {
      currentBlobs.remove(i);
    }
  }

  // There are no blobs!
  if (blobs.isEmpty() && currentBlobs.size() > 0) {
    println("Adding blobs!");
    for (Blob b : currentBlobs) {
      b.id = blobCounter;
      blobs.add(b);
      blobCounter++;
    }
  } else if (blobs.size() <= currentBlobs.size()) {
    // Match whatever blobs you can match
    for (Blob b : blobs) {
      float recordD = 1000;
      Blob matched = null;
      for (Blob cb : currentBlobs) {
        PVector centerB = b.getCenter();
        PVector centerCB = cb.getCenter();         
        float d = PVector.dist(centerB, centerCB);
        if (d < recordD && !cb.taken) {
          recordD = d; 
          matched = cb;
        }
      }
      matched.taken = true;
      b.become(matched);
    }

    // Whatever is leftover make new blobs
    for (Blob b : currentBlobs) {
      if (!b.taken) {
        b.id = blobCounter;
        blobs.add(b);
        blobCounter++;
      }
    }
  } else if (blobs.size() > currentBlobs.size()) {
    for (Blob b : blobs) {
      b.taken = false;
    }

    // Match whatever blobs you can match
    for (Blob cb : currentBlobs) {
      float recordD = 1000;
      Blob matched = null;
      for (Blob b : blobs) {
        PVector centerB = b.getCenter();
        PVector centerCB = cb.getCenter();         
        float d = PVector.dist(centerB, centerCB);
        if (d < recordD && !b.taken) {
          recordD = d; 
          matched = b;
        }
      }
      if (matched != null) {
        matched.taken = true;
        matched.lifespan = maxLife;
        matched.become(cb);
      }
    }

    for (int i = blobs.size() - 1; i >= 0; i--) {
      //
      Blob b = blobs.get(i);
      if (!b.taken) {
        if (b.checkLife()) {
          blobs.remove(i);
        }
      }
    }
  }
}

void send_image() {
  //sends the canvas to the pi via UDP communication
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