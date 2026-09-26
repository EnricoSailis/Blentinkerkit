// Sketch per gestione di Arduino Braccio mediante Processing
// in cinematica inversa

#include <Servo.h>

#define ABILITAZIONE 12

// Numerazione giunti
// 0 Base
// 1 Spalla
// 2 Gomito
// 3 Polso
// 4 Rotazione polso
// 5 Pinza

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

int delayMin = 0;   // rallentamento degli spostamenti
                    // Attenzione: ritardi eccessivi potrebbero riempire
                    // il buffer di ricezione
int delaySafeStart = 1000;  // rallentamento safeStart (ms)
char stato = 0;
int i = 0;

//---------------------------------------------------------
void setup() 
{
  Serial.begin(115200);

  pinMode(ABILITAZIONE, OUTPUT);
  digitalWrite(ABILITAZIONE, HIGH);

  safeStart();
  Serial.print('go');
}

//-----------------------------------------------------
void loop() 
{
  switch(stato)
  {
    case 0:
      // attesa sincronizzazione
      if(Serial.available() > 0)
      {
        int seriale = Serial.read();
        if(seriale == 255) stato = 1;
      }
      break;

    case 1:
      if(Serial.available() > 0)
      {
        int seriale = Serial.read();
        if(seriale == 255) 
        {
          muovi();
          i=0;
        }
        else
        {
          if(seriale <= posizioneMax[i] && seriale >= posizioneMin[i])
            posizioneVoluta[i] = seriale;
          i++;
        }
        break;
      }
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
void safeStart()   // posizionamento iniziale in sicurezza
{
  // posizionamento iniziale in sicurezza
  // l'attach della base si fa per ultima per evitare
  // che il braccio spazzi il tavolo
  
  for(int i=1 ; i < 6; i++)
  {
    myservo[i].write(posizioneIniziale[i]);
    myservo[i].attach(servoPin[i]) ;
    delay(delaySafeStart);
  }
  myservo[0].write(posizioneIniziale[0]);
  myservo[0].attach(servoPin[0]) ;
  delay(delaySafeStart);

  for(int i=0 ; i < 6; i++) posizioneAttuale[i] = posizioneIniziale[i] ;
  for(int i=0 ; i < 6; i++) posizioneVoluta[i] = posizioneIniziale[i] ;
}









