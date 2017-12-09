class Motif {
  float xpos, ypos; //the x and y positions of this motif inside either canvas or another motif
  int my_width, my_height; 

  PGraphics my_graphic;
  
  ArrayList<Motif> my_childern = new ArrayList<Motif>();
  //float[] input_features;
  int[] my_feature_indecies; //the features that this particular motif cares about
  
  Motif() {
    // default constructor
    xpos = 0;
    ypos = 0;
    my_width = 0;
    my_height = 0;
    my_graphic = createGraphics(my_width, my_height);
    my_feature_indecies = new int[0];
  }
  
  Motif(float inputx, float inputy, int inputw, int inputh, int[] input_feature_indecies) {
    // more explicit constructor
    xpos = inputx;
    ypos = inputy;
    my_width = inputw;
    my_height = inputh;
    my_graphic = createGraphics(my_width, my_height);
    my_feature_indecies = input_feature_indecies;
  }
  
  void animate(float[] input_features) {
    // draw the class's graphic based on its childern and itself
    // default is just to draw the childern on itself
//    my_graphic.background(0);
    my_graphic.beginDraw();
    my_graphic.clear();
    for (Motif child : my_childern) { 
      child.animate(input_features); //animate the child
      my_graphic.image(child.my_graphic, child.xpos, child.ypos,child.my_width,child.my_height);
    }
    my_graphic.endDraw();    
  }

}