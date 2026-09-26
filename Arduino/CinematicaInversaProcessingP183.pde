PFont myFont;

int stato=0;

int altezzaZ = 270;
int raggio = 35;
int Cx = 53;
int Cy = 53;

float x_e;
float y_e;
float z_e;
int angolo = 0;

// posizione verticale: base  spalla  gomito  polso   rot.polso    pinza
int[] servo={0, 90, 90, 90, 0, 0 };

float d1 = 44;
float a2 = 78;
float a3 = 78;
float a4 = 116;

int inizioScritteX=281;
int inizioScritteA=831;
int inizioScritteY=63;
int distanzaScritte=31;
int x0Grafico=625;
int y0Grafico=437;

float theta1=HALF_PI, theta2=0,  theta3=0,   theta4=0;
int theta1degrees, theta2degrees, theta3degrees, theta4degrees;

// valori impostati fissi
float phi=HALF_PI;   // angolo pinza 1.57 = 90 gradi

//------------------------------------------------------------------------------
void setup()
{
  size(1000, 594); // dimensioni finestra
  myFont = createFont("Impact", 16);
  textFont(myFont);
  background(0);  // colore sfondo grigio
  strokeWeight(3);  // dimensione linee
}

//--------------------------------------------------------------------------------
void draw()
{
  switch(stato)
  {
    case 0: //scritte assi
    fill(255,255, 255); // colore riempimento bianco
    text("Angoli dei giunti", inizioScritteA+10,
                              inizioScritteY-1*distanzaScritte);
    text("Base",    inizioScritteA, inizioScritteY+0*distanzaScritte);
    text("Spalla",  inizioScritteA, inizioScritteY+1*distanzaScritte);
    text("Gomito",  inizioScritteA, inizioScritteY+2*distanzaScritte);
    text("Polso",   inizioScritteA, inizioScritteY+3*distanzaScritte);
    
    text("x", inizioScritteX-31, inizioScritteY+0*distanzaScritte);
    text("y", inizioScritteX-31, inizioScritteY+1*distanzaScritte);
    text("gradi", inizioScritteX-56, inizioScritteY+2*distanzaScritte);
    text("Proiezione sul piano del braccio", x0Grafico-88,y0Grafico+31);
    
    fill(0, 255, 255); // colore riempimento bianco
    textSize(25);  // dimensione caratteri
    text("SOLO SIMULAZIONE", x0Grafico-100, y0Grafico+63);
    textSize(16);   // dimensione caratteri
    fill(255,255,255); // colore riempimento bianco
    
    stroke(120);
    noFill();
    arc(31, 313, 538, 538, -HALF_PI, HALF_PI);
    
    stroke(255,255,255);  // colore contorno bianco
    fill(255,255,255);  // colore riempimento bianco
    line(13, 313,344, 313);  // asse x
    line(344, 313, 338, 319);
    line(344, 313, 338, 306);
    line(31, 31, 31, 581);
    line(31, 31, 38, 38);
    line(31, 31, 25, 38);
    text("y", 50, 31);
    text("x", 338, 288);
    text("z", 591, 44);
    text("xy", 869, 413);
    text("Fronte >>>", 38, 338);
    text("Vista dall'alto",38, 375);
    stato = 1;
    break;
    
    case 1:
      calcolo_posizioni();
      cinematica_inversa();
      
      servo[0]=90-theta1degrees;
      servo[1]=theta2degrees;
      servo[2]=90+theta3degrees;
      servo[3]=90+theta4degrees;
      fill(255, 255, 255);  // colore riempimento bianco
      for(int i=0; i < 4; i++) // angoli servomotori
      {
        fill(0);  // colore riempimento nero
        stroke(120);  // colore contorno  grigio
        rect(inizioScritteA+63, 
             inizioScritteY-25+i*distanzaScritte, 63, 31);
        fill(255, 255, 255);  
        text(servo[i], inizioScritteA+75,
            inizioScritteY+i*distanzaScritte);
      }
      disegna_robot();
      // delay(50); // eventuale rallentamento
      break;
  }
}

//--------------------------------------------------------------------
void calcolo_posizioni()
{
  angolo++;
  if(angolo == 361) angolo = 0;
  
  fill(0);
  stroke(120);
  for(int i=0;  i<3;  i++)
    rect(inizioScritteX-10, 
             inizioScritteY-25+i*distanzaScritte, 75, 31);
  fill(255);         // colore riempimento bianco
  stroke(255);     // colore contorno bianco
  text(x_e, inizioScritteX, inizioScritteY+0*distanzaScritte);
  text(y_e, inizioScritteX, inizioScritteY+1*distanzaScritte);
  text(angolo, inizioScritteX, inizioScritteY+2*distanzaScritte);
    
  x_e = Cx + raggio*cos(radians(angolo));
  y_e = Cy + raggio*sin(radians(angolo));
  z_e = altezzaZ;
  
  stroke(0);  // colore riempimento nero
  fill(0);   // colore contorno nero
  // posizione e dimensioni cancellazione
  rect(25 + x_e, 306 - y_e, 13, 13);
  fill(255, 255, 0);  // colore riempimento giallo
  stroke(255, 255, 0); // colore contorno giallo
  ellipse(31 + x_e, 313 - y_e, 3, 3);
}

//----------------------------------------------------------------------------
void cinematica_inversa()
{
  // costanti geometriche a2, a3, a4, d1
  // parametri: x_e, y_e, z_e, phi
  // restituisce i valori di theta1, theta2, theta3, theta4
  
  if((y_e == 0) && (x_e == 0))
  {
    theta1 =  PI/2;
    theta1degrees = 90;
  }
  else
  {
    theta1 = atan2(y_e, x_e);
    theta1degrees = int(degrees(theta1));
  }
  
  float x_e_primo = sqrt(pow(x_e, 2)+pow(y_e,2));
  float y_e_primo = z_e - d1;
  
  float x_w_primo = x_e_primo-a4*cos(phi);
  float y_w_primo = y_e_primo- a4*sin(phi);
  
  // c3 può risultare > 1 se il punto non è raggiungibile
  float c3 = (pow(x_w_primo, 2) + pow(y_w_primo, 2)
             -pow(a2, 2)-pow(a3, 2))/(2*a2*a3);
             
  float s3 = - sqrt(1- pow(c3, 2));
  theta3 = atan2(s3, c3);
  
  theta3degrees = int(degrees(theta3));
  
  
  float beta = atan2( a3 * s3, a2 + a3 * c3);
  float gamma = atan2( y_w_primo, x_w_primo );
  theta2 = gamma - beta;
  theta2degrees = int (degrees(theta2));
  
  theta4 = phi - (theta2 + theta3);
  theta4degrees = int(degrees(theta4));
}

//-----------------------------------------------------------------
void disegna_robot()
{
  float xx0 = x0Grafico, yy0 = y0Grafico;
  float xx1 = xx0+a2*cos(theta2);
  float yy1 = yy0+a2*sin(theta2);
  float xx2 = xx1+a3*cos(theta2 + theta3);
  float yy2 = yy1+a3*sin(theta2 + theta3);
  float xx3 = xx2+a4*cos(theta2 + theta3 + theta4);
  float yy3 = yy2+a4*sin(theta2 + theta3 + theta4 );
  
  stroke(120); // cancella disegno
  fill(0);
  arc(xx0, yy0-d1, 538, 538, PI, TWO_PI);
  
  fill(255);
  stroke(255);
  line(xx0-250, yy0, xx0 + 250, yy0);   // asse xy
  line(xx0+250, yy0, xx0 + 244, yy0-6); 
  line(xx0+250, yy0, xx0 + 244, yy0+6); 
  line(xx0, 31, xx0 , 481);    // asse z
  line(xx0, 31, xx0 + 6, 38);            
  line(xx0, 31, xx0 - 6, 38);            
          
  stroke(255, 255, 0);  // colore giallo
  strokeWeight(10);  // dimensione linee
  line(xx0-19, yy0, xx0+19, yy0); // linea piano di appoggio
  line(xx0,yy0,xx0,yy0-d1);       // elevazione della base
  circle(xx0, yy0-d1, 3);
  
  line(xx0, 2*yy0-yy0-d1, xx1, 2*yy0-yy1-d1);  // segmenti del robot
  circle(xx1, 2*yy0 -yy1 -d1, 3);
  line(xx1, 2*yy0-yy1-d1, xx2, 2*yy0-yy2-d1); 
  circle(xx2, 2*yy0 -yy2 -d1, 3);
  line(xx2,2*yy0-yy2-d1, xx3, 2*yy0-yy3-d1);
  strokeWeight(3);  // dimensione linee
}
             
    
    
    
  
  
  
  
