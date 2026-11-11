#include <blendixserial.h>

/*
  Blender-to-Arduino | Servo Braccio Control v1

  Author   : Enrico Sailis
  Date     : 31 October 2026
  Website  : 
  Email    : enricosailis@gmail.com

  Description
  -----------
  This example demonstrates how to use the BlendixSerial library
  to receive object rotation data from Blender and control six servo motors
  of Tinkerkit Braccio connected to an Arduino.

  Blender sends the X,Y,Z‑rotation of Object 0,1,2,3,4,5 over the USB connection.
  The Arduino reads the incoming value and maps it to the servo angle: for example
      Rotation Z =   0°   →  Servo at   0°
      Rotation Z = 180°   →  Servo at 180°

  The servo signal wires are connected to pin 11, 10, 9, 6, 5, 3 


  Wiring
  ------

  | Servo                | Arduino                |
  |----------------------|------------------------|
  | Signal               | Pin 11, 10, 9, 6, 5, 3 |
  | VCC                  | 5V                     |
  | GND                  | GND                    |

 
  Note
  ----
  This sketch uses the hardware serial port (USB) for Blender communication.
  Do **not** open the Serial Monitor or any other program that uses the
  same COM port while Blender is connected, the port can only be used
  by one application at a time.
*/

#include "blendixserial.h"  
#include <Servo.h>          

blendixserial blendix;       // Instance to parse Blender data

#define ABILITAZIONE 12

// Numerazione giunti
// 0 Base
// 1 Spalla
// 2 Gomito
// 3 Polso
// 4 Rotazione Polso
// 5 Pinza

// Pin di Arduino
#define BASE 11         // Base
#define SPALLA 10       // Arm
#define GOMITO 9        // Forearm
#define POLSO 6         // Wrist_vertical
#define POLSO_ROT 5     // Wrist_rotation
#define PINZA 3         // Gear_gripper_2

int servoPin[6] = {11, 10, 9, 6, 5, 3}; // Braccio Shield

Servo myServo[6];             // Servo object

// posizione raccolta:    base  spalla  gomito  polso rot.polso pinza
int posizioneIniziale[6]={ 0,   130,     0,      0,     0,     70};
int posizioneMax[6]={     180,   165,   180,    180,    180,    125};
int posizioneMin[6]={        0,    15,    0,       0,      0,     20};

//int passiRampa = STEP/5;   // passi nella rampa di rallentamento
int delta = 6;  // riduzione di velocità ad ogni passo nella rampa
int delayMin = 20;  // rallentamento iniziale degi spostamenti
int delaySafeStart = 1000;  // rallentamento safeStart (ms)



int lastServoPos[6] = {-1, -1, -1, -1, -1, -1};       // Stores last servo angle to avoid repeated writes
int servoPos = -1;

void setup()
{
  // Hardware serial (USB) receives data from Blender
  Serial.begin(115200);

  pinMode(ABILITAZIONE, OUTPUT);
  digitalWrite(ABILITAZIONE,HIGH);


 // posizionamento iniziale in sicurezza e attacco del servo ai pin

  for (int j=1; j<6; j++)
  {
    myServo[j].write(posizioneIniziale[j]);
    myServo[j].attach(servoPin[j]);
  }
  // l'attach della base si fa per ultima per evitare
  // che il braccio spazzi il tavolo
  myServo[0].write(posizioneIniziale[0]);
  myServo[0].attach(servoPin[0]) ;
  delay(delaySafeStart);
}

void loop()
{
  // Read all available bytes from the hardware serial (Blender data)
  while (Serial.available())
  {
    // Feed each byte to the Blendix parser; if a complete frame is received...
    if (blendix.bodParse(Serial.read()))
    {
      // ...update the servo position
      updateServo();
    }
  }
}

// Function to read the latest rotation data and move the servo accordingly
void updateServo()
{
  float x, y, z;   // Variables to hold rotation angles

  // Check if Y‑rotation data for object 0 (Cubo_Dati_Base) is available
  if (blendix.axisAvailable(0, Rotation, Y))
  {
    // Retrieve the y rotation  for object 0. 
    //blendix.getRotation(0, x, y, z);
    blendix.getValue(0, Rotation, y);

    // Convert Y rotation (expected range 0–180) to servo angle,
    // then constrain to valid servo range (0–180)
    servoPos = constrain((int)y, 0, 180);

    // Only move the servo if the angle actually changed
    if (servoPos != lastServoPos[0])
    {
      myServo[0].write(servoPos);   // Command the servo to the new angle
      lastServoPos[0] = servoPos;   // Update last stored position
    }
  }


   // Check if X‑rotation data for object 1 (Cubo_Dati_Arm) is available
  if (blendix.axisAvailable(1, Rotation, X))
  {
    // Retrieve the X rotation  for object 1
    //blendix.getRotation(1, x, y, z);
    blendix.getValue(1, Rotation, x);

    // Convert X rotation (expected range 0–180) to servo angle,
    // then constrain to valid servo range (15–165)
    servoPos = constrain((int)x, 15, 165);

    // Only move the servo if the angle actually changed
    if (servoPos != lastServoPos[1])
    {
      myServo[1].write(servoPos);   // Command the servo to the new angle
      lastServoPos[1] = servoPos;   // Update last stored position
    }
  }
  
 
  
   // Check if X‑rotation data for object 2 (Cubo_Dati_Forearm) is available
  if (blendix.axisAvailable(2, Rotation, X))
  {
    // Retrieve the X rotation  for object 2
    //blendix.getRotation(2, x, y, z);
    blendix.getValue(2, Rotation, x);

    // Convert X rotation (expected range 0–180) to servo angle,
    // then constrain to valid servo range (0–180)
    int servoPos = constrain((int)(x), 0, 180);

    // Only move the servo if the angle actually changed
    if (servoPos != lastServoPos[2])
    {
      myServo[2].write(servoPos);   // Command the servo to the new angle
      lastServoPos[2] = servoPos;   // Update last stored position
    }
   }
   
  
    // Check if X‑rotation data for object 3 (Cubo_Dati_Wrist_Vertical) is available
  if (blendix.axisAvailable(3, Rotation, X))
  {
    // Retrieve the full rotation triplet for object 3
    //blendix.getRotation(3, x, y, z);
    blendix.getValue(3, Rotation, x);

    // Convert X rotation (expected range 0–180) to servo angle,
    // then constrain to valid servo range (0–180)
    int servoPos = constrain((int)x, 0, 180);

    // Only move the servo if the angle actually changed
    if (servoPos != lastServoPos[3])
    {
      myServo[3].write(servoPos);   // Command the servo to the new angle
      lastServoPos[3] = servoPos;   // Update last stored position
    }
  }
  
  
    // Check if Y‑rotation data for object 4 (Cubo_Dati_Gripper) is available
  if (blendix.axisAvailable(4, Rotation, Z))
  {
    // Retrieve the Z rotation triplet for object 4
    //blendix.getRotation(4, x, y, z);
    blendix.getValue(4, Rotation, z);

    // Convert Y rotation (expected range 0–180) to servo angle,
    // then constrain to valid servo range (0–180)
    int servoPos = constrain((int)(z), 0, 55);

    // Only move the servo if the angle actually changed
    if (servoPos != lastServoPos[4])
    {
      myServo[4].write(servoPos);   // Command the servo to the new angle
      lastServoPos[4] = servoPos;   // Update last stored position
    }
  }

}
