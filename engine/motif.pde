class Motif {
  float xpos, ypos; //the x and y positions of this motif inside either canvas or another motif
  int my_width, my_height; 

  PGraphics my_graphic;
  
  Motif[] my_childern;
  //float[] input_features;
  float[] my_feature_indecies; //the features that this particular motif cares about
  


  Motif() {
    // default constructor
    xpos = 0;
    ypos = 0;
    my_width = 0;
    my_height = 0;
    my_graphic = createGraphics(my_width, my_height);
    my_childern = new Motif[0];
    my_feature_indecies = new float[0];
  }
  
  Motif(float inputx, float inputy, int inputw, int inputh, float[] input_feature_indecies) {
    // more explicit constructor
    xpos = inputx;
    ypos = inputy;
    my_width = inputw;
    my_height = inputh;
    my_graphic = createGraphics(my_width, my_height);
    my_childern = new Motif[0];
    my_feature_indecies = input_feature_indecies;
  }
  
  void animate(float[] input_features) {
    // draw the class's graphic based on its childern and itself
    // default is just to draw the childern
    my_graphic.beginDraw();
    for (int i=0; i < my_childern.length; i++) { 
      my_childern[i].animate(input_features); //animate the child
      image(my_childern[i].my_graphic, my_childern[i].xpos, my_childern[i].ypos, my_childern[i].my_width, my_childern[i].my_height);
    }  
    my_graphic.endDraw();    
  }
  
}