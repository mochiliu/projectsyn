class nodemotif_Translate extends Motif {
  float x_speed, y_speed;
  
  nodemotif_Translate(float initial_x_speed, float initial_y_speed, Motif child, int[] input_feature_indecies) {
    // more explicit constructor
    super(child.xpos, child.ypos, child.my_width, child.my_height, input_feature_indecies);
    // takes over the child's x and y positions
    child.xpos = 0;
    child.ypos = 0;
    x_speed = initial_x_speed;
    y_speed = initial_y_speed;
    my_childern.add(child);
  }
  
  void animate(float[] input_features) {
    xpos = xpos + (x_speed*input_features[my_feature_indecies[0]]);
    ypos = ypos + y_speed;
    if (ypos > my_height) {
      ypos = 0;
    }
    if (xpos > my_width) {
      xpos = 0;
    }
    super.animate(input_features);
    //println(time);
  }
}