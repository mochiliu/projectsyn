class leafmotif_Circle extends Motif {
  float base_radius;
  color my_color;
  
  leafmotif_Circle(float initial_radius, color initial_color, float inputx, float inputy, int[] input_feature_indecies) {
    // more explicit constructor
    super(inputx, inputy, 30, 30, input_feature_indecies);
    base_radius = initial_radius;
    my_color = initial_color;
  }
  
  void animate(float[] input_features) {
    float radius = base_radius * input_features[my_feature_indecies[0]];
    my_graphic.beginDraw();
    my_graphic.clear();
    //my_graphic.fill(my_color);
    my_graphic.ellipse(my_width/2, my_height/2, radius*2, radius*2);
    my_graphic.endDraw();
  }
}