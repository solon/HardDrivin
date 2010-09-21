import processing.core.*; 
import processing.xml.*; 

import oscP5.*; 
import netP5.*; 

import java.applet.*; 
import java.awt.*; 
import java.awt.image.*; 
import java.awt.event.*; 
import java.io.*; 
import java.net.*; 
import java.text.*; 
import java.util.*; 
import java.util.zip.*; 
import java.util.regex.*; 

public class HardDrivinDisplay extends PApplet {




OscP5 oscP5;
NetAddress myRemoteLocation; 

public void setup() {
  size(1024, 600, P3D);
  // receive OSC messages from HardDrivin.py
  oscP5 = new OscP5(this,9002);
  // Load the font from the sketch's data directory
  textFont(loadFont("Ceriph0756-32.vlw"));

  background(0);
  drawTweet("harddrivin","Control the cars with Twitter! Use the hashtag #harddrivin - or get the cars to follow a user: @harddrivin follow @tweakfestival");
}

public void draw() {
}

public void drawTweet(String user, String tweet) {
  background(0);
  fill(255);
  text("@"+user, 24, 100);
  fill(0,255,0);
  text(tweet, 24, 160, 960, 400);
}

public void oscEvent(OscMessage theOscMessage) {
  /* check if theOscMessage has the address pattern we are looking for. */
  
  if (theOscMessage.checkAddrPattern("/tweet")==true || theOscMessage.checkAddrPattern("/hashtag")==true) {
    /* check if the typetag is the right one. */
    if(theOscMessage.checkTypetag("sis")) {
      /* parse theOscMessage and extract the values from the osc message arguments. */
      String user = theOscMessage.get(0).stringValue();  
      int tweetLength = theOscMessage.get(1).intValue();
      String tweet = theOscMessage.get(2).stringValue();
      //print("### received an osc message /tweet with typetag sis.");
      //println(" values: "+firstValue+", "+secondValue+", "+thirdValue);
      
      drawTweet(user, tweet);
      
      return;
    }      
  }
  println("### received an osc message. with address pattern "+theOscMessage.addrPattern());
}


  static public void main(String args[]) {
    PApplet.main(new String[] { "--bgcolor=#FFFFFF", "HardDrivinDisplay" });
  }
}
