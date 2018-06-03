boolean gameStart = false;

float x;
float y;
float speedX;
float speedY;
int leftColor = 255;
int rightColor = 255;
float diam;
float rectSize;
float diamHit;

import java.awt.MouseInfo;
import java.awt.Point;

void setup() {
  size(30,30);
  reset_game();
  noStroke();
  smooth();
  ellipseMode(CENTER);
  setup_sendudp();//set up sendudp
}

void draw() { 
  background(0);
  Point mouse;
  mouse = MouseInfo.getPointerInfo().getLocation();
  //print(mouse);
  fill(128,128,128);
  diam = 20/500.0*height;
  ellipse(x, y, diam, diam);

  fill(leftColor);
  rect(0, 0, 20/500.0*width, height); // left wall
  fill(rightColor);
  rect(width-(30/500.0*width), (float(mouse.y)/displayHeight*height)-rectSize/2, (10/500.0*width), rectSize);

  if (gameStart) {
    x = x + speedX;
    y = y + speedY;

    // if ball hits movable bar, invert X direction and apply effects
    if ( x > width-(30/500.0*width) && x < width - (20/500.0*width) && y > (float(mouse.y)/displayHeight*height)-rectSize/2 && y < (float(mouse.y)/displayHeight*height)+rectSize/2) {
      speedX = speedX * -1;
      x = x + speedX;
      rightColor = 0;
      fill(random(0,128),random(0,128),random(0,128));
      diamHit = random(75,150)/500.0*height;
      ellipse(x,y,diamHit,diamHit);
      rectSize = rectSize-(10/500.0*height);
      rectSize = constrain(rectSize, (10/500.0*height),(150/500.0*height));      
    } 

    // if ball hits wall, change direction of X
    else if (x < (25/500.0*width)) {
      speedX = speedX * -1.1;
      x = x + speedX;
      leftColor = 0;
    }

    else {     
      leftColor = 128;
      rightColor = 128;
    }
    // resets things if you lose
    if (x > width) { 
      gameStart = false;
      reset_game();
    }

    // if ball hits up or down, change direction of Y   
    if ( y > height || y < 0 ) {
      speedY = speedY * -1;
      y = y + speedY;
    }
  }
  send_image();
}

void mousePressed() {
  gameStart = !gameStart;
}

void reset_game() {
  x = 150/500.0*width;
  y = 150/500.0*height;
  speedY = random(3, 5)/500.0*height;
  speedX = random(3, 5)/500.0*width;
  rectSize = 150/500.0*height;
}