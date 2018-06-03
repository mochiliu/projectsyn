final boolean debug_mode = true;
final int screen_size = 300;

// initialize motif tree
Motif root_motif;
Motif leaf_motif;

void setup() {

  size(300, 300);
  background(0);
  
  int[] leaf_relevant_features = {feature_descriptions.audio_amplitude,feature_descriptions.audio_amplitude};
  int[] node_relevant_features = {feature_descriptions.constant,feature_descriptions.audio_amplitude};
//  leaf_motif = new leafmotif_Circle(5,color(255, 0, 0),0,0,leaf_relevant_features);
  leaf_motif = new leafmotif_Rectangle(5,5,color(255, 0, 0),0,0,leaf_relevant_features);
  root_motif = new nodemotif_Translate(0.1, 0.1, leaf_motif,node_relevant_features);
  
 if (!debug_mode) {
    setup_sendudp();
  } 
  setup_features();
}      

void draw() {
  //feature extract
  extract_features();
 
  background(0);
  root_motif.animate(features);
  image(root_motif.my_graphic,root_motif.xpos,root_motif.ypos);
  if (!debug_mode) {
    send_image();
  }
}
