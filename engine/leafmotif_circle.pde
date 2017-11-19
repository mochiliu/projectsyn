class leafmotif_Circle extends Motif {
  float radius;
  color my_color;
  
  leafmotif_Circle(float input_radius, color input_color, float inputx, float inputy, int[] input_feature_indecies) {
    // more explicit constructor
    super(inputx, inputy, ceil(input_radius*2), ceil(input_radius*2), input_feature_indecies);
    radius = input_radius;
    my_color = input_color;
  }
  
  void animate(float[] input_features) {
    //println(xpos+ypos+radius);
    my_graphic.beginDraw();
    //my_graphic.fill(my_color);
    my_graphic.ellipse(radius, radius, radius*2, radius*2);
    my_graphic.endDraw();
  }
}