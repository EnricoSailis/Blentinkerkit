byte PORT =0;

import processing.serial.*;
Serial myPort;
PFont myFont;

int count=0, stato = 0;
String strGO=" GO ";
String strWAIT = "WAIT";
String msg;

int altezzaZ = 430;
int raggio = 55;
int Cx = 85;
int Cy = 85;

float x_e;
float y_e;
float z_e;
int angolo = 0;

// posizione verticale: base spalla  gomito  polso  rot.polso  pinza
int[] servo = {0, 90, 90, 90, 0, 0};

float d1 = 70;   // PARTENZA
float a2 = 125;  // BRACCIO
float a3 = 125;  // AVAMBRACCIO
float a4 = 185;  // MANO

int inizio_scritteX = 450;
int inizio_scritteA = 1330;
int inizio_scritteY = 100;
int distanzaScritte = 50;
int x0Grafico = 1000;
int y0Grafico = 700;

float theta1 = HALF_PI, theta2 = 0, theta3 = 0, theta4=0;
int theta1degrees, theta2degrees,theta3degrees,theta4degrees;

// valori impostati fissi
float phi = HALF_PI;  // angolo pinza 1.57 = 90 gradi

//-------------------------------------------------------------
void setup() 
{  
  myPort = new Serial(this, "COM5", 115200);  // aggiornare COM // myPort = new Serial(this, Serial.list()[0], 115200);
  size(1600, 950);  // dimensioni finestra
  myFont = createFont("Impact", 25);
  textFont(myFont);
  background(0); // colore sfondo grigio
  strokeWeight(3);  // dimensione lineare
  
  msg = strWAIT;
}

// --------------------------------------------------
void draw()
{
  switch(stato)
  {
    case 0:
      aspettaGO();
      if(msg.equals(" GO ") == true) stato = 1;
      break;

    case 1:    // scritte e assi
      fill(255, 255, 255); // colore riempimento bianco
      text("Angoli dei giunti", inizio_scritteA +10,
                               inizio_scritteY-1*distanzaScritte);
      text("Base", inizio_scritteA +10, inizio_scritteY+0*distanzaScritte);
      text("Spalla", inizio_scritteA, inizio_scritteY+1*distanzaScritte);
      text("Gomito", inizio_scritteA, inizio_scritteY+2*distanzaScritte);
      text("Polso", inizio_scritteA, inizio_scritteY+3*distanzaScritte);
      
      text("x", inizio_scritteX -50, inizio_scritteY+0*distanzaScritte);
      text("y", inizio_scritteX -50, inizio_scritteY+1*distanzaScritte);
      text("gradi", inizio_scritteX -90, inizio_scritteY+2*distanzaScritte);
      text("Proiezione sul piano del braccio", x0Grafico-140, y0Grafico+50);
    
      stroke(120);  
      noFill();
      arc(50, 500, 860, 860, -HALF_PI, HALF_PI);
    
      stroke(255, 255, 255);   // colore contorno bianco
      fill(255, 255, 255);      // colore riempimento bianco
      line(20, 500, 550, 500); // asse x
      line(550, 500, 540, 510);
      line(550, 500, 540, 490);
      line(50, 50, 50, 930);     // asse y
      line(50, 50, 60, 60);
      line(50, 50, 40, 60);
      text("y", 80, 50);
      text("x", 540, 460);
      text("z", 945, 70);
      text("xy", 1390, 660);
      text("Fronte >>>", 60, 540);
      text("Vista dall'ato", 60, 600);
      stato = 2 ;
      break;

    case 2:
      calcolo_posizioni();
      cinematica_inversa();
      
      servo[0]=90-theta1degrees ;
      servo[1]=theta2degrees ;
      servo[2]=90+theta3degrees ;
      servo[3]=90+theta4degrees ;
    
      // spedisco a Arduino la posizione di tutti i servi
      for(int i = 0; i < 4 ; i++)
      {
        myPort.write(servo[i]);
        // delay(10)
      }

      for(int i = 0; i < 4 ; i++) println(servo[i]); 
      myPort.write(255);
      println(255);
      delay(10);

      fill(255, 255, 255); // colore riempimento bianco
      
      for(int i = 0; i < 4 ; i++)   // angoli servomotori
      {
        fill(0);       // colore riempimento nero
        stroke(120);   // colore contorno grigio
        rect(inizio_scritteA+100, 
            inizio_scritteY-40+i*distanzaScritte, 100, 50);
        fill(255, 255, 255);
        text(servo[i], inizio_scritteA+120, 
          inizio_scritteY+i*distanzaScritte);
      }
      disegna_robot();
      // delay(50); // eventuale rallentamento
      break;
  }    
}

// ------------------------------------------------------------------
void calcolo_posizioni()
{
  angolo++ ;
  if(angolo == 361) angolo = 0;
  
  fill(0);   // colore riempimento nero
  stroke(120);     // colore contorno grigio
  for(int i=0; i < 3 ; i++)
     rect(inizio_scritteX-10, 
            inizio_scritteY-40+i*distanzaScritte, 120, 50);
  fill(255);    // colore riempimento bianco
  stroke(255); // colore contorno bianco
  text(x_e, inizio_scritteX, inizio_scritteY+0*distanzaScritte);
  text(y_e, inizio_scritteX, inizio_scritteY+1*distanzaScritte); 
  text(angolo, inizio_scritteX, inizio_scritteY+2*distanzaScritte);  
    
  x_e = Cx+raggio * cos(radians(angolo));
  y_e = Cy+raggio * sin(radians(angolo));
  z_e = altezzaZ;
     
  stroke(0);    // colore riempimento nero
  fill(0);      // colore contorno nero
       // posizione e dimensioni cancellazione
  rect(40+x_e, 490-y_e, 20, 20);
  fill(0, 255, 255);   // colore riempimento celeste
  stroke(0, 255, 255);  // colore contorno celeste
  ellipse(50+x_e, 500-y_e, 5, 5);    
}

//-------------------------------------------------------------------
void cinematica_inversa()
{
  // costanti geometriche a2, a3, a4, d1
  // parametri: x_e, y_e, z_e, phi
  // restituisce i valori di theta1, theta2, theta3, theta4
  
  if((y_e == 0) && (x_e == 0))
  {
    theta1 = PI/2;
    theta1degrees = 90;
  }
  else
  {
    theta1 = atan2(y_e, x_e);
    theta1degrees = int(degrees(theta1));
  }
  
  float x_e_primo = sqrt(pow(x_e,2)+pow(y_e, 2));
  float y_e_primo = z_e - d1;
  
  float x_w_primo = x_e_primo-a4*cos(phi);
  float y_w_primo = y_e_primo-a4*sin(phi);
  
  // c3 può risultare >1 se il punto non è raggiungibile
  float c3 = (pow(x_w_primo,2)+pow(y_w_primo,2)
              - pow(a2,2)-pow(a3,2))/(2*a2*a3);
              
  float s3 = -sqrt(1 - pow(c3,2));
  theta3 = atan2(s3, c3);
  theta3degrees = int (degrees(theta3));
  
  float beta = atan2(a3 * s3 , a2 + a3*c3);
  float gamma = atan2(y_w_primo, x_w_primo);
  theta2 = gamma - beta;
  theta2degrees = int(degrees(theta2));
  
  theta4 = phi - (theta2 + theta3);
  theta4degrees = int(degrees(theta4));
}

// ------------------------------------------------------------------
void aspettaGO() 
{
  fill(100);
  stroke(0, 255, 0);
  rect(1500, 693, 80, 50);

  count++;
  delay(20);
  if(count < 10)
  {
    fill(255, 255, 0); // colore riempimento giallo
    text(msg, 1518, 730);
  }
  if(count > 20) count=0;

  while (myPort.available() > 0)
  {
    String inBuffer = myPort.readString();    
    if(inBuffer.equals("go") == true)
    {
      println("GO RICEVUTO");
      msg = strGO;
      fill(100);
      stroke(0, 255,0);
      rect(1500, 693, 80, 50);
      fill(0, 255, 0);
      text(msg, 1518, 730);
      myPort.write(255);
    }
  }
}

// ------------------------------------------------------------
void disegna_robot()
{
  float x0 = x0Grafico, y0 = y0Grafico;
  float x1 = x0+a2*cos(theta2);
  float y1 = y0+a2*sin(theta2);
  float x2 = x1+a3*cos(theta2+theta3);
  float y2 = y1+a3*sin(theta2+theta3);
  float x3 = x2+a4*cos(theta2+theta3+theta4);
  float y3 = y2+a4*sin(theta2+theta3+theta4);

  fill(0);   // colore riempimento nero  cancella disegno
  stroke(120); 
  arc(x0, y0 -d1, 860, 860, PI, TWO_PI);

  fill(255);
  stroke(255);
  line( x0-400, y0, x0+400, y0 );   // asse xy
  line( x0+400, y0, x0+390, y0-10 ); 
  line( x0+400, y0, x0+390, y0 +10); 
  line( x0, 50, x0, 770 ); 
  line( x0, 50, x0+10, 60 ); 
  line( x0, 50, x0-10, 60 ); 
  
  stroke(255, 255, 0);   // colore giallo
  strokeWeight(10);     // dimensione linee
  line( x0-30, y0, x0+30, y0 );           // linea piano d'appoggio
  line(x0, y0, x0, y0-d1);   // elevazione della base
  circle(x0, y0-d1, 5);
  
  line(x0, 2*y0-y0-d1, x1, 2*y0-y1-d1);  // disegna robot
  circle(x1, 2*y0-y1-d1, 5);
  line(x1, 2*y0-y1-d1, x2, 2*y0-y2-d1);
  circle(x2, 2*y0-y2-d1, 5);
  line(x2, 2*y0-y2-d1, x3, 2*y0-y3-d1);
  strokeWeight(3);  // dimensione linee
}
