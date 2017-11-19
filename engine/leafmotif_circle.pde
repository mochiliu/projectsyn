class leafmotif_Circle extends Motif {
  float radius;
  color my_color;
  
  
  void animate(float[] input_features) {
    my_graphic.beginDraw();

    ellipse(xpos, ypos, radius*2, radius*2);
    my_graphic.endDraw();    

  }
}