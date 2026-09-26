// Sketch per gestione di Arduino Braccio mediante Processing
// in cinematica diretta

#include <Servo.h>

#define ABILITAZIONE 12

// Numerazione giunti
// 0 Base
// 1 Spalla
// 2 Gomito
// 3 Polso
// 4 Rotazione polso
// 5 Pinza

// lunghezza
#define PARTENZA      75    // [mm]
#define BRACCIO       125
#define AVAMBRACCIO   125
#define MANO          185

// pin di Arduino
#define BASE  11
#define SPALLA  10
#define GOMITO  9
#define POLSO   6
#define POLSO_ROT 5
#define PINZA 3

int servoPin[6] = {11,  10, 9,  6,  5,  3}; // Braccio Shield
Servo myservo[6];

// posizione raccolta:    base  spalla  gomito  polso rot.polso pinza
int posizioneIniziale[6]={ 90,   130,     0,      0,     90,     70};
int posizioneMax[6]={     180,   165,   180,    180,    180,    125};
int posizioneMin[6]={        0,    15,    0,       0,      0,     55};

int posizioneAttuale[6];
int posizioneVoluta[6];

int max_XY = 300;  // [mm]
int max_Z = 510;
int min_Z = 10;

int delayMin = 20;   // rallentamento degli spostamenti
int delaySafeStart = 1000;  // rallentamento safeStart (ms)

//---------------------------------------------------------
void setup() 
{
  Serial.begin(115200);

  pinMode(ABILITAZIONE, OUTPUT);
  digitalWrite(ABILITAZIONE, HIGH);

  safeStart();
  Serial.println("go");
  delay(1000);        // attende che Processing sia pronto
  Serial.print(max_XY);
  Serial.print(",");
  Serial.print(min_Z);
  Serial.print(",");
  Serial.print(max_Z);
  Serial.println(",");
  delay(1000);

  // aggiorno Processing sulla posizione iniziale impostata da Arduino
  for(int i=0; i<6; i++)
  {
    Serial.print("X,");
    Serial.print(i);  // invia sul seriale il giunto
    Serial.print(",");
    Serial.println(posizioneIniziale[i]);  // invia sul seriale l'angolo
  }
}

//-----------------------------------------------------
void loop() 
{
  // attesa sincronizzazione
  while(Serial.available() == 0)  
  {
    if(Serial.read() == 255) break;
  }

  while(1)
  {
    while(Serial.available() == 0) {}  // aspetto caratteri

    char pulsante = Serial.read();
    if (pulsante >= 0  && pulsante < 12) // scarto valori anomali
    {
      int giunto = pulsante/2;        // calcolo il numero del giunto
      if((pulsante % 2) == 0)         // guardo se è decremento
      {
        if(posizioneAttuale[giunto] > posizioneMin[giunto])
          posizioneVoluta[giunto] = posizioneAttuale[giunto]-1;
      }
      else
      {
        if(posizioneAttuale[giunto] < posizioneMax[giunto])
          posizioneVoluta[giunto] = posizioneAttuale[giunto]+1;
      }

      Serial.print("X,");
      Serial.print(giunto);     // invia su seriale il giunto
      Serial.print(",");
      Serial.println(posizioneAttuale[giunto]);  // invia angolo su seriale
    }    

    // se il punto da raggiungere non esce
    // dallo spazio di lavoro massimo muovo i servi
    if(checkPosizione()) muovi();

  }
}

// ------------------------------------------------------------
void muovi()
{
  for(int j=0; j < 6; j++)
  {
    myservo[j].write(posizioneVoluta[j]);
    posizioneAttuale[j] = posizioneVoluta[j];
  }
  delay(delayMin);
}

// -------------------------------------------------------------
// posizionamento iniziale in sicurezza
void safeStart()
{
  for(int i=1 ; i < 6; i++)
  {
    myservo[i].write(posizioneIniziale[i]);
    myservo[i].attach(servoPin[i]) ;
    delay(delaySafeStart);
  }
  // l'attach della base di fa per ultima per evitare
  // che il braccio spazzi il tavolo
  myservo[0].write(posizioneIniziale[0]);
  myservo[0].attach(servoPin[0]) ;

  for(int i=0 ; i < 6; i++) posizioneAttuale[i] = posizioneIniziale[i] ;
  for(int i=0 ; i < 6; i++) posizioneVoluta[i] = posizioneIniziale[i] ;
}

// -------------------------------------------------------------------
boolean checkPosizione()
{
  // limita lo spazio di lavoro
  // a un cilindro (R = max_XY, Hmin = min_Z, Hmax = max_Z)
  int richiesto_XY =  abs(BRACCIO * cos(radians(posizioneVoluta[1]))
  + AVAMBRACCIO*cos(radians(posizioneVoluta[1]+ posizioneVoluta[2] - 90))
  + MANO * cos(radians(posizioneVoluta[1]+posizioneVoluta[2]-90
  + posizioneVoluta[3]-90)));

  int richiesto_Z = PARTENZA + BRACCIO * sin(radians(posizioneVoluta[1]))
  + AVAMBRACCIO*sin(radians(posizioneVoluta[1]+posizioneVoluta[2]-90))
  + MANO * sin(radians(posizioneVoluta[1]+ posizioneVoluta[2]-90
  + posizioneVoluta[3]-90 )) ;

  if((richiesto_XY > max_XY) | (richiesto_Z > max_Z)
      | (richiesto_Z < min_Z))
    return false;
  else
    return true ;
}











