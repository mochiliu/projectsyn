class nodemotif_Translate extends Motif {
  float x_speed, y_speed;
  float original_xpos, original_ypos;
  nodemotif_Translate(float initial_x_speed, float initial_y_speed, Motif child, int[] input_feature_indecies) {
    // more explicit constructor
    super(child.xpos-(child.my_width/2), child.ypos-(child.my_height/2), child.my_width, child.my_height, input_feature_indecies);
    // takes over the child's x and y positions
    child.xpos = 0;
    child.ypos = 0;
    x_speed = initial_x_speed;
    y_speed = initial_y_speed;
    original_xpos = child.xpos-(child.my_width/2);
    original_ypos = child.ypos-(child.my_height/2);
    my_childern.add(child);
  }
  
  void animate(float[] input_features) {
    if (ypos > my_height) {
      ypos = original_ypos;
    }
    if (xpos > my_width) {
      xpos = original_xpos;
    }
    
    xpos = xpos + (x_speed*input_features[my_feature_indecies[0]]);
    ypos = ypos + (y_speed*input_features[my_feature_indecies[0]]);
    super.animate(input_features);
     ///println(itimenput_features[my_feature_indecies[0]]);
  }
}