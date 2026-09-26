byte PORT =0;

import processing.serial.*;
Serial myPort;
PFont myFont;

int count=0;
String strGO="GO";
String strWAIT = "WAIT";
String msg;
int stato=0;

int inizio_scritte = 80;
int passo_grafica = 100;
float x0 = 780, y0=600;   // posizione centro del grafico

int max_XY, min_Z, max_Z ;

// posizione ripiegata: base  spalla  gomito  polso rot.polso pinza
int angoli[] ={ 90,   130,    0,      0,      90,     70};

int[][] matrice = 
{
  {25, 35+passo_grafica*5, 100, 80},    // 11 + base
  {250, 35+passo_grafica*5, 100, 80},   // 10 - base
  {25, 35+passo_grafica*4, 100, 80},    // 9 - spalla
  {250, 35+passo_grafica*4, 100, 80},   // 8 + spalla
  {25, 35+passo_grafica*3, 100, 80},    // 7 - gomito
  {250, 35+passo_grafica*3, 100, 80},   // 6 + gomito
  {25, 35+passo_grafica*2, 100, 80},    // 4 - polso
  {250, 35+passo_grafica*2, 100, 80},   // 4 + polso
  {25, 35+passo_grafica*1, 100, 80},    // 3 + polso rot
  {250, 35+passo_grafica*1, 100, 80},   // 2 - spalla
  {25, 35+passo_grafica*0, 100, 80},    // 1 pinza chiudi
  {250, 35+passo_grafica*0, 100, 80},   // 0 pinza apri
};

float theta2 = PI/2, theta3 = 0, theta4=0;

float d1 = 70;   // PARTENZA
float a2 = 125;  // BRACCIO
float a3 = 125;  // AVAMBRACCIO
float a4 = 185;  // MANO

//-------------------------------------------------------------
void setup() 
{  
  myPort = new Serial(this, "COM5", 115200);  // aggiornare COM
 // myPort = new Serial(this, Serial.list()[0], 115200);
 
  size(1200, 650);
  myFont = createFont("Impact", 15);
  textFont(myFont);
  background(0,0,0); // colore sfondo nero
  strokeWeight(6);  // dimensione lineare

  fill(255, 255, 255);  // colore riempimento bianco
 for(int i = 0; i < 6; i++) // scrive angoli
    text(angoli[i], 165, inizio_scritte + (5-i)*passo_grafica);

  msg = strWAIT;

  pulsanti();
  scritte_pulsanti();
  disegna_simulazione();
}

// --------------------------------------------------
void draw()
{
  switch(stato)
  {
    case 0:
      aspettaGO();
     if(msg.equals("GO") == true) stato = 1;
      break;

    case 1:
      if(myPort.available() > 0)
      {
        String inBuffer = myPort.readString();
        int[] nums = int(split(inBuffer, ','));
        max_XY = nums[0];
        min_Z = nums[1];
        max_Z = nums[2];
        print(max_XY, "-", min_Z, "-", max_Z);
        stato = 2;
      }
      break;

    case 2:
      for(int i = 0; i < 12 ; i++)
      {
        if(mouseSopraArea(matrice[i][0], matrice[i][1], 
          matrice[i][2], matrice[i][3] ))
        {
          stroke(250, 250, 250); // colore bordo bianco
          fill(0, 0, 255);  // colore riempimento blu
          rect(matrice[i][0], matrice[i][1],
               matrice[i][2], matrice[i][3]);

          if (mousePressed)
          {
            myPort.write(i);
            delay(40);
            fill(0);  // colore riempimento nero
            rect(matrice[i][0], matrice[i][1],
                   matrice[i][2], matrice[i][3]);
          }
        }
        else
        {
          stroke(255, 0, 0);  // colore bordo rosso
          fill(0, 0, 255);  // colore riempimento blu
          rect(matrice[i][0], matrice[i][1],
              matrice[i][2], matrice[i][3]);
        }
      }

      if(myPort.available() > 0)
      {
        String inBuffer = myPort.readStringUntil('\n');
        if(inBuffer != null)
        {         // parsing della stringa ricevuta
          inBuffer = trim(inBuffer);  // toglie spazi bianchi
          String[] list = split(inBuffer, ',');
                      // è una stringa corretta
          if((list.length==3)  && (list[0].equals("X")) )
          {
            stroke(0);  // colore linee nero
            fill(0);  // sfondo rettangolo nero
                      // cancella scritta precedente
            rect(150, 40 + passo_grafica*(5-int(list[1])), 50, 50);
            fill(255);  // colore scritta bianco
                        // assegnazione angolo nel vettore
            int giunto = int(list[1]);
            angoli[giunto] = int(list[2]);
            int a = angoli[giunto];
            text(str(a), 165, 
                  inizio_scritte+(5-giunto)*passo_grafica);
          }
        }
        disegna_simulazione();
      }
      scritte_pulsanti();
      break;
  }
}

// ------------------------------------------------------------------
// sottoprogramma di controllo posizione mouse
boolean mouseSopraArea(int PosizioneX, 
                int PosizioneY, int Larghezza, int Altezza)
{
  if(mouseX >= PosizioneX  &&  mouseX <= PosizioneX+Larghezza
          && mouseY >= PosizioneY  && mouseY <= PosizioneY+Altezza )
    return true;
  else
    return false;
}

// ------------------------------------------------------------------

void aspettaGO() 
{
  fill(100);
  stroke(0, 255, 0);
  rect(440, 30, 80, 40);

  count++;
  delay(20);
  if(count < 10)
  {
    fill(255, 255, 0); // colore riempimento giallo
    text(msg, 465, 60);
  }
  if(count > 20) count=0;

  while (myPort.available() > 0)
  {
    String inBuffer = myPort.readString();
    
    println("Attendo go");
    print(inBuffer);
    
    //if(inBuffer.equals("go") == true)
    {
      println("GO RICEVUTO");
      msg = strGO;
      fill(100);
      stroke(0, 255,0);
      rect(440, 30, 80, 40);
      fill(0, 255, 0);
      text(msg, 475, 60);
      myPort.write(255);
    }
  }
}

//-------------------------------------------------------


void scritte_pulsanti()
{
  fill(255, 255, 255);  // colore riempimento bianco
  text("Base",       30,    70 + passo_grafica*5);
  text("Sinistra",   30,   100 + passo_grafica*5);
  text("Base",      255,    70 + passo_grafica*5);
  text("Destra",    255,   100 + passo_grafica*5);
  text("Spalla",     30,    70 + passo_grafica*4);
  text("in basso",   30,   100 + passo_grafica*4);
  text("Spalla",    255,    70 + passo_grafica*4);
  text("in alto",   255,   100 + passo_grafica*4);
  text("Gomito",     30,    70 + passo_grafica*3);
  text("in basso",   30,   100 + passo_grafica*3);
  text("Gomito",    255,    70 + passo_grafica*3);
  text("in alto",   255,   100 + passo_grafica*3);
  text("Polso1",     30,    70 + passo_grafica*2);
  text("in basso",   30,   100 + passo_grafica*2);
  text("Polso1",    255,    70 + passo_grafica*2);
  text("in alto",   255,   100 + passo_grafica*2);
  text("Polso2",     30,    70 + passo_grafica*1);
  text("orario",     30,   100 + passo_grafica*1);
  text("Polso2",    255,    70 + passo_grafica*1);
  text("antior.",    255,   100 + passo_grafica*1);
  text("Pinza",      30,    70 + passo_grafica*0);
  text("Chiudi",     30,   100 + passo_grafica*0);
  text("Pinza",     255,    70 + passo_grafica*0);
  text("Apri",      255,   100 + passo_grafica*0);
  
}
// ---------------------------------------------------- 
void pulsanti()
{
  for(int i = 0; i < 12 ; i++)
  {
    stroke(255, 0, 0);  // colore bordo rosso
    fill(0, 0, 255); // colore riempimento blu
    rect(matrice[i][0], matrice[i][1],
         matrice[i][2], matrice[i][3]);
  }
}

// ------------------------------------------------------------
void disegna_simulazione()
{
  theta2 = radians(angoli[1]);
  theta3 = radians(angoli[2])-PI/2;
  theta4 = radians(angoli[3])-PI/2;
  
  float x1 = x0+a2*cos(theta2);
  float y1 = y0+a2*sin(theta2);
  float x2 = x1+a3*cos(theta2+theta3);
  float y2 = y1+a3*sin(theta2+theta3);
  float x3 = x2+a4*cos(theta2+theta3+theta4);
  float y3 = y2+a4*sin(theta2+theta3+theta4);

  // cancella disegno
  fill(0);   // colore riempimento nero
  stroke(120); 
  rect(430, 80, 700, 520);

  // traccia area di lavoro
  fill(100);
  stroke(0, 255, 0);
  rect(x0-max_XY, y0-max_Z, 2*max_XY, max_Z - min_Z);

  // disegna braccio
  stroke(255, 255, 0);   // colore giallo
  line( x0-30, y0, x0+30, y0 );           // linea piano d'appoggio
  fill(255); 
  text("Fronte >>> ", x0+8, y0-10);

  line(x0, y0, x0, y0-d1);   // elevazione della base
  circle(x0, y0-d1,10);

  line(x0, 2*y0-y0-d1, x1, 2*y0-y1-d1);  // disegna robot
  circle(x1, 2*y0-y1-d1, 10);
  line(x1, 2*y0-y1-d1, x2, 2*y0-y2-d1);
  circle(x2, 2*y0-y2-d1, 10);
  line(x2, 2*y0-y2-d1, x3, 2*y0-y3-d1);
}
