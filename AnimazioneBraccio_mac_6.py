# Python script per Blender per la presa dell'oggetto Cube e lo spostamento di questo nel cerchio sulla base

import bpy
from mathutils import Matrix
import math


from PIL import Image
import matplotlib.pyplot as plt
import numpy as np



# parametri fisici del braccio tinkerkit
d1 = 0.075 # altezza del bone Base  (75 mm)
a2 = 0.125 # lunghezza del bone Arm (125 mm)
a3 = 0.125 # lunghezza del bone Forearm (125 mm)
a4 = 0.185 # lunghezza del bone Wrist_vertical + lunghezza della pinza (185 mm)

# Dimensioni dell'oggetto Cube: Dimensions: (dx = 58 mm, dy = 28 mm, dz = 72 mm)
dx = 0.075  
dy = 0.025
dz = 0.085

pez = dz/2 - d1     # altezza del centro dell'oggetto Cube - l'altezza del bone Base
phi = -3.1415/3     # angolo tra il bone Wrist_vertical e l'orizzontale, -3.1415/3  in radianti equivale a - 60°

# angoli della pinza
gripopen =  0.6981 # Angolo della pinza aperta gripopen, 0.6981 in radianti equivale a 40°  
gripeng = 0.2792   # Angolo della pinza in presa gripeng, 0.2792 in radianti equivale a 16°
gripclose = 0.0    # Angolo della pinza chiusa griclose, 0.0 in radianti equivale a 0°

# angoli di rotazione dei bones nella posizione a riposo del braccio
theta1 = 0.0        # angolo del bone Base (y_R)
theta2 = 2.3561     # angolo del bone Arm (z_R), 2.3561 corrisponde a 135°
theta3 = 0.0        # angolo del bone Forearm (z_R) rispetto all'asse del bone Arm
theta4 = 0.0        # angolo del bone Wrist_vertical (z_R) rispetto all'asse del bone Forearm
theta5 = 0.0        # angolo del bone Wrist_rotation (y_R)
theta6 = gripclose  # angolo del bone Gear_gripper_2 (x_R) per l'apertura e la chiusura della pinza



def angoliPresaRilascioCube(x, y, z):
    # vengono determinati gli angoli  theta1, theta2, theta3, tetha4 dei bone per la presa dell'oggetto Cube

    # Determinazione di theta1, angolo di rotazione del bone Base per raggiungere l'oggetto Cube da prendere
    # math.atan2() è la funzione arcotangente con gestione quadranti
    theta1 = math.atan2(y, x)  # in radianti
    
    # Calcolo degli angoli theta2, theta3 e theta4 per la rotazione dei bone Arm, Forearm e Wrist_vertical, chiamando phi l'angolo  tra la pinza (o il bone Wrist_vertical) e l'orizzontale. Le formule sono tratte dal testo RoboGame vol.4 pag. 176
   
    pek = pow( x**2 + y**2, 1/2)       # distanza dall'origine del centro dell'oggetto Cube
    
    # Calcolo della posizione (pwk, pwz) della base del bone Wrist_vertical  nel piano verticale che lo contiene, dove l'asse k è nel piano orizzontale X, Y  
    pwk = pek - a4*math.cos(phi)
    pwz = pez - a4*math.sin(phi)
    
    # Calcolo dell'angolo theta3 (del bone Forearm con l'asse del bone Arm)
    cos_theta3 = (pwk**2 + pwz**2 -a3**2 - a2**2)/(2*a3*a2)     #  cos_theta3 è uguale a math.cos(theta3)
    sin_theta3 = - pow( 1 - cos_theta3**2, 1/2)                        # sin_theta3 è uguale a math.sin(theta3)
    theta3 = math.atan2(sin_theta3, cos_theta3)
    
    # Calcolo dell'angolo theta2 che il bone Arm forma col piano orizzontale X, Y
    cos_theta2 = (pwk*(a2+a3*cos_theta3) + pwz*a3*sin_theta3)/((a2 + a3*cos_theta3)**2 + (a3*sin_theta3)**2)    #  cos_theta2 è uguale a math.cos(theta2)

    sin_theta2 = (pwz*(a2+a3*cos_theta3) - pwk*a3*sin_theta3)/((a2 + a3*cos_theta3)**2 + (a3*sin_theta3)**2)    # sin_theta2 è uguale a math.sin(theta2)
    
    theta2 = math.atan2(sin_theta2, cos_theta2)
    
    # Calcolo dell'angolo theta4 che il bone Wrist_vertical forma con l'asse del bone Forearm
    theta4 = phi - theta2 - theta3

    return (theta1, theta2, theta3, theta4)



def presaCube(theta1, theta2, theta3, theta4):
    
    '''
    Posizione dell'oggetto da prendere: Cube, Location: (x (mm), y (mm), z (mm)) 
    
    Calcolo degli angoli theta1, theta2, theta3, theta4, per la rotazione del braccio e la presa

    Sequenza di azioni per la presa dell'oggetto Cube:
    
    frames: 1   → 30:  Apertura pinza Gear_gripper_2: (x_R: 0° —> gripopen)
    frames: 30  → 60:  Piegamento polso Wrist_vertical: (z_R: 0° —> 45°)  
    frames: 60  → 90:  Rotazione bone Base: (y_R: 0° —> theta1)
    frames: 90  → 120: Rotazione polso Wrist_vertical: (z_R: 45° —> theta4 + 90°)
    frames: 120 → 150: Rotazione avambraccio Forearm: (z_R: 0° —> theta3 + 90°)
    frames: 150 → 180: Rotazione spalla Arm: (z_R: 135° → theta2)
    frames: 180 → 210: Chiusura pinza Gear_gripper_2 per la presa: (x_R: gripopen —> gripeng)
    '''
    
    
    # Selezione dell'oggetto armatura
    armature_name = "Armature"  # nome dell'oggetto armatura
    armature = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature

    # Passiamo in modalità 'POSE'
    bpy.ops.object.mode_set(mode='POSE')

    
    # Angolo pinza aperta: gripopen ; angolo pinza in presa: gripeng 
    # Apertura pinza Gear_gripper_2: (x_R: gripclose —> gripopen , frames: 1 —> 30), (x_R = gripopen, frames: 30 —> 180), (x_R:  gripopen —> gripeng, frames: 180 —> 210);

    # Riferimento al bone da animare
    bone_name = "Gear_gripper_2"          # bone da animare
    pose_bone = armature.pose.bones[bone_name]
    pose_bone.rotation_mode = 'XYZ'
    
    # Imposta rotazione al frame 1 
    pose_bone.rotation_euler = (gripclose, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=1)

    # Imposta rotazione al frame 30 
    pose_bone.rotation_euler = (gripopen, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=30)

    # Imposta costantemente l'apertura della pinza fino al frame 180 
    pose_bone.rotation_euler = (gripopen, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=180)

    # Chiusura pinza Gear_gripper_2 per la presa: (x_R: gripopen —> gripeng, frames: 180 —> 210)
    pose_bone.rotation_euler = (gripeng, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=210)




    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC 
    # Creiamo i frames per il Cubo_Dati_Gear_Gripper_2

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Arm da animare
    object_name = "Cubo_Dati_Gear_Gripper_2"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'

    # Imposta rotazione al frame 1 
    obj.rotation_euler = (gripclose, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Imposta rotazione al frame 30 
    obj.rotation_euler = (gripopen, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=30)

    # Imposta costantemente l'apertura della pinza fino al frame 180 
    obj.rotation_euler = (gripopen, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=180)

    # Chiusura pinza Gear_gripper_2 per la presa: (x_R: gripopen —> gripeng, frames: 180 —> 210)
    obj.rotation_euler = (gripeng, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=210)




      # Piegamento polso Wrist_vertical: (z_R = 0°, frames: 1 → 30), (z_R: 0° → 45°, frames: 30 → 60), (z_R = 45° , frames: 60 → 90 ), (z_R: 45° → theta4 + 90°, frames: 90 → 120 )

    # Riferimento al bone da animare
    bone_name = "Wrist_vertical" 
    pose_bone = armature.pose.bones[bone_name]
    pose_bone.rotation_mode = 'XYZ'  

    # Imposta rotazione al frame 1 
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=1)

    # Imposta rotazione al frame 30 
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=30)

    # Imposta rotazione al frame 60 
    pose_bone.rotation_euler = (0.0, 0.0, 0.7854)  # 0.7854 in radianti equivale a 45°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=60)
    
     # Imposta rotazione al frame 90 
    pose_bone.rotation_euler = (0.0, 0.0, 0.7854)  # 0.7854 in radianti equivale a 45°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=90)

     # Imposta rotazione al frame 120 
    pose_bone.rotation_euler = (0.0, 0.0, theta4 + 1.5708)  # 1.5708 in radianti equivale a 90°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=120)

     # Imposta rotazione al frame 210 
    pose_bone.rotation_euler = (0.0, 0.0, theta4 + 1.5708)  # 1.5708 in radianti equivale a 90°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=210)




    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC 
    # Creiamo i frames per il Cubo_Dati_Wrist_Vertical

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Arm da animare
    object_name = "Cubo_Dati_Wrist_Vertical"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'

    # Imposta rotazione al frame 1 
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Imposta rotazione al frame 30 
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=30)

    # Imposta rotazione al frame 60 
    obj.rotation_euler = (0.0, 0.0, 0.7854)  # 0.7854 in radianti equivale a 45°
    obj.keyframe_insert(data_path="rotation_euler", frame=60)
    
     # Imposta rotazione al frame 90 
    obj.rotation_euler = (0.0, 0.0, 0.7854)  # 0.7854 in radianti equivale a 45°
    obj.keyframe_insert(data_path="rotation_euler", frame=90)

     # Imposta rotazione al frame 120 
    obj.rotation_euler = (0.0, 0.0, theta4 + 1.5708)  # 1.5708 in radianti equivale a 90°
    obj.keyframe_insert(data_path="rotation_euler", frame=120)

     # Imposta rotazione al frame 210 
    obj.rotation_euler = (0.0, 0.0, theta4 + 1.5708)  # 1.5708 in radianti equivale a 90°
    obj.keyframe_insert(data_path="rotation_euler", frame=210)




   
    # Rotazione del bone Base: (y_R = 0° , frames: 0 → 60), (y_R = 0° → theta1 , frames: 60 → 90)

    # Riferimento al bone da animare
    bone_name = "Base"          # bone da animare
    pose_bone = armature.pose.bones[bone_name]
    pose_bone.rotation_mode = 'XYZ'  

    # Imposta rotazione al frame 1 
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=1)

    # Imposta rotazione al frame 60 
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=60)

    # Imposta rotazione al frame 90
    pose_bone.rotation_euler = (0.0, theta1, 0.0) # theta1 calcolato in radianti in base alla posizione dell'oggetto Cube
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=90)

    # Imposta rotazione al frame 210
    pose_bone.rotation_euler = (0.0, theta1, 0.0) # theta1 calcolato in radianti in base alla posizione dell'oggetto Cube
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=210)

    # Imposta rotazione al frame 240
    pose_bone.rotation_euler = (0.0, theta1, 0.0) # theta1 calcolato in radianti in base alla posizione dell'oggetto Cube
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=240)


    '''
    Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC ci si avvale dell'addon Blendixserial che purtroppo non consente di selezionare i Bone. Pertanto sono stati costruiti dei cubi "dati" che ruotano seguendo i bone corrispondenti da cui possiamo leggere frame per frame gli angoli theta1, theta2, theta3, theta4 dei bone che ruotano (Base, Arm, Forearm, Wrist_vertical). Creiamo i frames per il Cubo_Dati_Base 

    '''
    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Base da animare
    object_name = "Cubo_Dati_Base"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'

    # Imposta rotazione al frame 1 
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Imposta rotazione al frame 60 
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=60)

    # Imposta rotazione al frame 90
    obj.rotation_euler = (0.0, theta1, 0.0) # theta1 calcolato in radianti in base alla posizione dell'oggetto Cube
    obj.keyframe_insert(data_path="rotation_euler", frame=90)

    # Imposta rotazione al frame 210
    obj.rotation_euler = (0.0, theta1, 0.0) # theta1 calcolato in radianti in base alla posizione dell'oggetto Cube
    obj.keyframe_insert(data_path="rotation_euler", frame=210)

    # Imposta rotazione al frame 240
    obj.rotation_euler = (0.0, theta1, 0.0) # theta1 calcolato in radianti in base alla posizione dell'oggetto Cube
    obj.keyframe_insert(data_path="rotation_euler", frame=240)




# Rotazione dell'avambraccio Forearm: (z_R = 0°, frames: 1 → 120), (z_R: 0° → theta3 + 90°, frames: 120 → 150)

    # Riferimento al bone da animare
    bone_name = "Forearm"         
    pose_bone = armature.pose.bones[bone_name]
    pose_bone.rotation_mode = 'XYZ'  

    # Imposta rotazione al frame 1 
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=1)

    # Imposta rotazione al frame 120 
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=120)

    # Imposta rotazione al frame 150 
    pose_bone.rotation_euler = (0.0, 0.0, theta3 + 1.5708)  # 1.5708 in radianti equivale a 90°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=150)

    # Imposta rotazione al frame 210 
    pose_bone.rotation_euler = (0.0, 0.0, theta3 + 1.5708)  # 1.5708 in radianti equivale a 90°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=210)


    '''
    Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC creiamo i frames per il Cubo_Dati_ForeArm 

    '''
    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Base da animare
    object_name = "Cubo_Dati_ForeArm"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'

    # Imposta rotazione al frame 1 
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Imposta rotazione al frame 120 
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=120)

    # Imposta rotazione al frame 150 
    obj.rotation_euler = (0.0, 0.0, theta3 + 1.5708)  # 1.5708 in radianti equivale a 90°
    obj.keyframe_insert(data_path="rotation_euler", frame=150)

    # Imposta rotazione al frame 210 
    obj.rotation_euler = (0.0, 0.0, theta3 + 1.5708)  # 1.5708 in radianti equivale a 90°
    obj.keyframe_insert(data_path="rotation_euler", frame=210)





    # Rotazione spalla Arm: (z_R = 135°, frames: 1 → 150), ( z_R = 145° → theta2, frames: 150 → 180)

    # Riferimento al bone da animare
    bone_name = "Arm"         
    pose_bone = armature.pose.bones[bone_name]
    pose_bone.rotation_mode = 'XYZ'  

    # Imposta rotazione al frame 1 
    pose_bone.rotation_euler = (0.0, 0.0, 2.3561)  # 2.3561 in radianti equivalente a 135°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=1)

    # Imposta rotazione al frame 150 
    pose_bone.rotation_euler = (0.0, 0.0, 2.3561)  # 2.3561 in radianti equivalente a 145°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=150)

    # Imposta rotazione al frame 180 
    pose_bone.rotation_euler = (0.0, 0.0, theta2)  # 
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=180)

    # Imposta rotazione al frame 210 
    pose_bone.rotation_euler = (0.0, 0.0, theta2)  # 
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=210)
  
  
   # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')


    '''
    Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC ci si avvale dell'addon Blendixserial che purtroppo non consente di selezionare i Bone. Pertanto sono stati costruiti dei cubi "dati" che ruotano seguendo i bone corrispondenti da cui possiamo leggere frame per frame gli angoli theta1, theta2, theta3, theta4 dei bone che ruotano (Base, Arm, Forearm, Wrist_vertical). 

    '''

    # Creiamo i frames per il Cubo_Dati_Arm
    # Rotazione spalla Cubo_Dati_Arm: (z_R = 135°, frames: 1 → 150), ( z_R = 135° → theta2, frames: 150 → 180)    
    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Arm da animare
    object_name = "Cubo_Dati_Arm"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler = (0.0, 0.0, 2.3561) # 2.3561 in radianti equivalente a 145°

    # Inserisce il keyframe per la rotazione nel frame=1
    obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Imposta rotazione al frame 150 
    obj.rotation_euler = (0.0, 0.0, 2.3561)  # 2.3561 in radianti equivalente a 145°
    obj.keyframe_insert(data_path="rotation_euler", frame=150)

    # Imposta rotazione al frame 180 
    obj.rotation_euler = (0.0, 0.0, theta2)  # 
    obj.keyframe_insert(data_path="rotation_euler", frame=180)

    # Imposta rotazione al frame 210 
    obj.rotation_euler = (0.0, 0.0, theta2)  # 
    obj.keyframe_insert(data_path="rotation_euler", frame=210)

    


    '''
    Terminine delle azioni per la presa dell'oggetto!
    '''



def trasportoCube(theta1, theta2, theta3, theta4):

    '''
    Sequenza di azioni per il trasporto dell'oggetto:
    
    Rotazione spalla Arm:  (z_R : theta2_old —> 135° , frames: 210 —> 240)
    Rotazione dell'avambraccio Forearm: (z_R: theta3_old + 90° —> 0° , frames: 210 —> 240)
    Rotazione del polso Wrist_vertical: (z_R: theta4_old + 90° → 45°, frames: 210 → 240)
    Rotazione base Base:  (y_R: theta1_old —> theta1, frames: 240 —> 270) 
    Rotazione spalla Arm:  (z_R : 135° —> theta2, frames: 270 —> 300)
    Rotazione dell'avambraccio Forearm: (z_R: 0° —> theta3 + 90° , frames: 270 —> 300)
    Rotazione del polso Wrist_vertical: (z_R: 45° → theta4 + 90° , frames: 270 → 300)
    Apertura pinza Gear_gripper_2: (x_R : gripeng —> gripopen, frames: 300 —> 330)

    '''

    # Seleziona l'oggetto armatura
    armature_name = "Armature"  # nome dell'oggetto armatura
    armature = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature

    # Assicurati di essere in modalità 'POSE'
    bpy.ops.object.mode_set(mode='POSE')

    
    # Rotazione spalla Arm:  (z_R = theta2 , frames: 180 —> 210), (z_R : theta2 —> 135° , frames: 210 —> 240), (z_R : 135° —> theta2 , frames: 270 —> 300)

    # Riferimento al bone da animare
    bone_name = "Arm"
    pose_bone = armature.pose.bones[bone_name]
    pose_bone.rotation_mode = 'XYZ'


    # Imposta rotazione al frame 240 
    pose_bone.rotation_euler = (0.0, 0.0, 2.3561)  # 2.3561 in radianti equivalente a 135°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=240)

    # Imposta rotazione al frame 270 
    pose_bone.rotation_euler = (0.0, 0.0, 2.3561)  # 2.3561 in radianti equivalente a 135°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=270)

    # Imposta rotazione al frame 300 
    pose_bone.rotation_euler = (0.0, 0.0, theta2)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=300)
    
     # Imposta rotazione al frame 330 
    pose_bone.rotation_euler = (0.0, 0.0, theta2)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=330)

    
    
    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC Creiamo i frames per il Cubo_Dati_Arm
       
    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Arm da animare
    object_name = "Cubo_Dati_Arm"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'
    
    # Imposta rotazione al frame 240 
    obj.rotation_euler = (0.0, 0.0, 2.3561)  # 2.3561 in radianti equivalente a 135°
    obj.keyframe_insert(data_path="rotation_euler", frame=240)

    # Imposta rotazione al frame 270 
    obj.rotation_euler = (0.0, 0.0, 2.3561)  # 2.3561 in radianti equivalente a 135°
    obj.keyframe_insert(data_path="rotation_euler", frame=270)

    # Imposta rotazione al frame 300 
    obj.rotation_euler = (0.0, 0.0, theta2)  
    obj.keyframe_insert(data_path="rotation_euler", frame=300)
    
     # Imposta rotazione al frame 330 
    obj.rotation_euler = (0.0, 0.0, theta2)  
    obj.keyframe_insert(data_path="rotation_euler", frame=330)

    

    # Rotazione dell'avambraccio Forearm: (z_R: theta3 + 90° —> 0° , frames: 210 —> 240),  (z_R: 0° —> theta3 + 90° , frames: 270 —> 300)

    # Riferimento al bone da animare
    bone_name = "Forearm"         
    pose_bone = armature.pose.bones[bone_name]
    pose_bone.rotation_mode = 'XYZ'  
    
    # Imposta rotazione al frame 240 
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=240)
    
    # Imposta rotazione al frame 270 
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=270)
    
    # Imposta rotazione al frame 300 
    pose_bone.rotation_euler = (0.0, 0.0, theta3 + 3.1415/2)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=300)
    
    # Imposta rotazione al frame 330 
    pose_bone.rotation_euler = (0.0, 0.0, theta3 + 3.1415/2)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=330)


    
    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC creiamo i frames per il Cubo_Dati_ForeArm 

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Base da animare
    object_name = "Cubo_Dati_ForeArm"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'

    # Imposta rotazione al frame 240 
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=240)
    
    # Imposta rotazione al frame 270 
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=270)
    
    # Imposta rotazione al frame 300 
    obj.rotation_euler = (0.0, 0.0, theta3 + 3.1415/2)  
    obj.keyframe_insert(data_path="rotation_euler", frame=300)
    
    # Imposta rotazione al frame 330 
    obj.rotation_euler = (0.0, 0.0, theta3 + 3.1415/2)  
    obj.keyframe_insert(data_path="rotation_euler", frame=330)



    # Piegamento polso Wrist_vertical: (z_R = theta4 + 90° → 45°, frames: 210 → 240), (z_R: 45° → theta4 + 90° , frames: 270 → 300)

    # Riferimento al bone da animare
    bone_name = "Wrist_vertical" 
    pose_bone = armature.pose.bones[bone_name]
    pose_bone.rotation_mode = 'XYZ'  

    # Imposta rotazione al frame 240 
    pose_bone.rotation_euler = (0.0, 0.0, 3.1415/4)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=240)

    # Imposta rotazione al frame 270 
    pose_bone.rotation_euler = (0.0, 0.0, 3.1415/4)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=270)

    # Imposta rotazione al frame 300 
    pose_bone.rotation_euler = (0.0, 0.0, theta4 + 3.1415/2)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=300)

    # Imposta rotazione al frame 330 
    pose_bone.rotation_euler = (0.0, 0.0, theta4 + 3.1415/2)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=330)


    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC 
    # Creiamo i frames per il Cubo_Dati_Wrist_Vertical

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Arm da animare
    object_name = "Cubo_Dati_Wrist_Vertical"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'

    # Imposta rotazione al frame 240 
    obj.rotation_euler = (0.0, 0.0, 3.1415/4)  
    obj.keyframe_insert(data_path="rotation_euler", frame=240)

    # Imposta rotazione al frame 270 
    obj.rotation_euler = (0.0, 0.0, 3.1415/4)  
    obj.keyframe_insert(data_path="rotation_euler", frame=270)

    # Imposta rotazione al frame 300 
    obj.rotation_euler = (0.0, 0.0, theta4 + 3.1415/2)  
    obj.keyframe_insert(data_path="rotation_euler", frame=300)

    # Imposta rotazione al frame 330 
    obj.rotation_euler = (0.0, 0.0, theta4 + 3.1415/2)  
    obj.keyframe_insert(data_path="rotation_euler", frame=330)




    # Rotazione bone Base:  (y_R: theta1 —> 0°, frames: 240 —> 270)

    # Riferimento al bone da animare
    bone_name = "Base"
    pose_bone = armature.pose.bones[bone_name]
    pose_bone.rotation_mode = 'XYZ'
    
    # Imposta rotazione al frame 270 
    pose_bone.rotation_euler = (0.0, theta1, 0.0) 
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=270)

    # Imposta rotazione al frame 330 
    pose_bone.rotation_euler = (0.0, theta1, 0.0) 
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=330)



    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC 
    # Creiamo i frames per il Cubo_Dati_Base

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Arm da animare
    object_name = "Cubo_Dati_Base"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'

    # Imposta rotazione al frame 270 
    obj.rotation_euler = (0.0, theta1, 0.0) 
    obj.keyframe_insert(data_path="rotation_euler", frame=270)

    # Imposta rotazione al frame 330 
    obj.rotation_euler = (0.0, theta1, 0.0) 
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=330)




    # Apertura pinza Gear_gripper_2: (x_R : gripeng —> gripopen, frames: 300 —> 330 )

    # Riferimento al bone da animare
    bone_name = "Gear_gripper_2" 
    pose_bone = armature.pose.bones[bone_name]
    pose_bone.rotation_mode = 'XYZ'

    # Imposta rotazione al frame 300 
    pose_bone.rotation_euler = (gripeng, 0.0, 0.0)  # pinza in presa
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=300)

    # Imposta rotazione al frame 330 
    pose_bone.rotation_euler = (gripopen, 0.0, 0.0)  # pinza aperta
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=330)
    
    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')



    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC 
    # Creiamo i frames per il Cubo_Dati_Gear_Gripper_2

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Arm da animare
    object_name = "Cubo_Dati_Gear_Gripper_2"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'

    # Imposta rotazione al frame 300 
    obj.rotation_euler = (gripeng, 0.0, 0.0)  # pinza in presa
    obj.keyframe_insert(data_path="rotation_euler", frame=300)

    # Imposta rotazione al frame 330 
    obj.rotation_euler = (gripopen, 0.0, 0.0)  # pinza aperta
    obj.keyframe_insert(data_path="rotation_euler", frame=330)


    '''
    Terminine delle azioni per il trasporto dell'oggetto
    '''



def braccioaRiposo(theta1, theta2, theta3, theta4):


    '''
    Sequenza di azioni per riportare il braccio a riposo dopo il rilascio dell’oggetto: 
    Rotazione spalla Arm:  (zR : theta2 —> 135° , frames: 330 —> 360)
    Rotazione avambraccio Forearm: (zR : theta3 + 90° —> 0° , frames: 330 —> 360)
    Piegamento polso posizione riposo  Wrist_vertical: ( zR : theta4 + 90° → 0°, frames: 330 → 360)
    Pinza sempre aperta Gear_gripper_2:  ( xR = gripopen, frames: 330 → 360)
    Chiusura pinza Gear_gripper_2 in riposo:  ( xR : gripopen → gripclose, frames: 360 → 390)
    Rotazione della base Base a riposo: (yR = theta1 , frames: 330 —> 360), (yR : theta1 —> 0° , frames: 360 —> 390)

    '''


    # Seleziona l'oggetto armatura
    armature_name = "Armature"  # nome dell'oggetto armatura
    armature = bpy.data.objects[armature_name]
    bpy.context.view_layer.objects.active = armature

    # Assicurati di essere in modalità 'POSE'
    bpy.ops.object.mode_set(mode='POSE')


    # Rotazione spalla Arm in posizione di riposo: (zR : theta2 —> 135° , frames: 330 —> 360)

    # Riferimento al bone da animare
    bone_name = "Arm" 
    pose_bone = armature.pose.bones[bone_name]

    # Imposta rotazione al frame 360 
    pose_bone.rotation_mode = 'XYZ'  
    pose_bone.rotation_euler = (0.0, 0.0, 3*3.1415/4)  # 3/4 pigreco in radianti equivale a 135°
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=360)


    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC Creiamo i frames per il Cubo_Dati_Arm
       
    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Arm da animare
    object_name = "Cubo_Dati_Arm"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
    
    # Imposta la rotazione a su tutti gli assi
    obj.rotation_mode = 'XYZ'
    
    # Imposta rotazione al frame 360 
    obj.rotation_euler = (0.0, 0.0, 3*3.1415/4)  # 3/4 pigreco in radianti equivale a 135°
    obj.keyframe_insert(data_path="rotation_euler", frame=360)




    # Rotazione avambraccio Forearm in posizione riposo: (zR : theta3 —> 0° , frames: 330 —> 360)

    # Assicurati di essere in modalità 'POSE'
    bpy.ops.object.mode_set(mode='POSE')

    # Riferimento al bone da animare
    bone_name = "Forearm" 
    pose_bone = armature.pose.bones[bone_name]

    # Imposta rotazione al frame 360 
    pose_bone.rotation_mode = 'XYZ'  
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=360)


    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC creiamo i frames per il Cubo_Dati_ForeArm 

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Base da animare
    object_name = "Cubo_Dati_ForeArm"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
        
        
        
        
    # Imposta rotazione al frame 360 
    obj.rotation_mode = 'XYZ'  
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=360)




    # Piegamento polso posizione riposo  Wrist_vertical: (zR : theta4 + 90° → 0°, frames: 330 → 360)

    # Riferimento al bone da animare
    bone_name = "Wrist_vertical" 
    pose_bone = armature.pose.bones[bone_name]

    # Assicurati di essere in modalità 'POSE'
    bpy.ops.object.mode_set(mode='POSE')

    # Imposta rotazione al frame 360 
    pose_bone.rotation_mode = 'XYZ'  # puoi usare anche 'QUATERNION'
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=360)


    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC creiamo i frames per il Cubo_Dati_Wrist_Vertical 

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Wrist_Vertical da animare
    object_name = "Cubo_Dati_Wrist_Vertical"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
        
    # Imposta la modalità di rotazione 
    obj.rotation_mode = 'XYZ'  

    # Imposta rotazione al frame 360 
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=360)


    # Chiusura pinza Gear_gripper_2 in riposo: (xR = gripopen, frames: 330 → 360), ( xR : gripopen → gripclose, frames: 360 → 390)

    # Riferimento al bone da animare
    bone_name = "Gear_gripper_2" 
    pose_bone = armature.pose.bones[bone_name]

    # Assicurati di essere in modalità 'POSE'
    bpy.ops.object.mode_set(mode='POSE')

    # Imposta rotazione al frame 360 
    pose_bone.rotation_mode = 'XYZ'  
    pose_bone.rotation_euler = (gripopen, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=360)

    # Imposta rotazione al frame 390 
    pose_bone.rotation_mode = 'XYZ' 
    pose_bone.rotation_euler = (gripclose, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=390)




    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC creiamo i frames per il Cubo_Dati_Gear_Gripper_2 

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Gear_Gripper_2 da animare
    object_name = "Cubo_Dati_Gear_Gripper_2"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
        
    # Imposta la modalità di rotazione 
    obj.rotation_mode = 'XYZ'  

    # Imposta rotazione al frame 360 
    obj.rotation_euler = (gripopen, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=360)

    # Imposta rotazione al frame 390 
    obj.rotation_euler = (gripclose, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=390)



    # Rotazione del bone Base a riposo: (yR = theta1 , frames: 330 —> 360), (yR : theta1 —> 0° , frames: 360 —> 390)
    
        # Riferimento al bone da animare
    bone_name = "Base" 
    pose_bone = armature.pose.bones[bone_name]

    # Assicurati di essere in modalità 'POSE'
    bpy.ops.object.mode_set(mode='POSE')

    # Imposta rotazione al frame 360 
    pose_bone.rotation_mode = 'XYZ'  
    pose_bone.rotation_euler = (0.0, theta1, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=360)

    # Imposta rotazione al frame 390 
    pose_bone.rotation_mode = 'XYZ' 
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)  
    pose_bone.keyframe_insert(data_path="rotation_euler", frame=390)


    #Per comandare i servomotori l'interfaccia di blender con la porta seriale del PC creiamo i frames per il Cubo_Dati_Base

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')
  
    # Riferimento al Cubo_Dati_Base da animare
    object_name = "Cubo_Dati_Base"         
    
    # Recupera l'oggetto tramite il suo nome
    obj = bpy.data.objects.get(object_name)   
        
    # Imposta la modalità di rotazione 
    obj.rotation_mode = 'XYZ'  

    # Imposta rotazione al frame 360 
    obj.rotation_euler = (0.0, theta1, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=360)

    # Imposta rotazione al frame 390 
    obj.rotation_euler = (0.0, 0.0, 0.0)  
    obj.keyframe_insert(data_path="rotation_euler", frame=390)



    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')

    # Imposta il frame corrente a 1 e aggiorna la scena
    bpy.context.scene.frame_set(1)

    '''
    Terminine delle azioni per portare il braccio a riposo
    '''


def aggancioCube(x, y, z, theta1, theta2, theta3, theta4):
    # Creazione dei frames per l'oggetto Cube che deve muoversi quando preso dal braccio, seguendo il bone Wrist_rotation


    # Nomi della scena
    armature_name = "Armature"      # Nome dell'oggetto armatura
    bone_name = "Wrist_rotation"    # Nome del bone
    object_name = "Cube"            # Nome dell'oggetto da collegare

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')


    # Recupera i riferimenti
    armature_obj = bpy.data.objects.get(armature_name)
    child_obj = bpy.data.objects.get(object_name)
    bone_obj = bpy.data.objects.get(bone_name)

    # Validazione
    if armature_obj is None or armature_obj.type != 'ARMATURE':
        raise ValueError(f"L'oggetto '{armature_name}' non è un'armatura valida.")
    if child_obj is None:
        raise ValueError(f"L'oggetto '{object_name}' non esiste.")
    if bone_name not in armature_obj.data.bones:
        raise ValueError(f"Il bone '{bone_name}' non esiste nell'armatura '{armature_name}'.")

    # Imposta il vincolo "Child Of" dell'oggetto object_name a bone_name
    child_of = child_obj.constraints.new(type='CHILD_OF')
    child_of.name = "Child Of"
    child_of.target = armature_obj
    child_of.subtarget = bone_name


    # Imposta l'influence iniziale
    child_of.influence = 0.0  # 0% di influence

    # Inserisce i frames per l'oggetto Cube per variare l'influence in base ai movimenti del braccio
    # Imposta l'influence 0 dal frame 1 al frame 150
    frame_num = 1
    child_of.keyframe_insert(data_path="influence", frame=frame_num)

    frame_num = 210
    child_of.keyframe_insert(data_path="influence", frame=frame_num)

    # === APPLICA "SET INVERSE" ===
    bpy.ops.object.mode_set(mode='OBJECT')  # Assicura di essere in Object Mode
    bpy.context.view_layer.objects.active = child_obj
    bpy.ops.constraint.childof_set_inverse(constraint=child_of.name, owner='OBJECT')

    # Imposta l'influence per il trasporto
    child_of.influence = 1.0  # 100% di influence

    frame_num = 211
    child_of.keyframe_insert(data_path="influence", frame=frame_num)

    frame_num = 330
    child_of.keyframe_insert(data_path="influence", frame=frame_num)

    # Imposta l'influence 0% dal  rilascio del cube
    child_of.influence = 0.0  # 0% di influence

    frame_num = 331
    child_of.keyframe_insert(data_path="influence", frame=frame_num)

    frame_num = 410
    child_of.keyframe_insert(data_path="influence", frame=frame_num)



    # Imposta la Location del Cube dal frame 1 al frame 330
    frame_start = 1   # Frame da cui iniziare la nuova posizione
    frame_end = 330     # Frame in cui termina l'animazione
    start_location = (x, y, z)  # Posizione iniziale (x, y, z)
    
    # determinazione dell'angolo z_R dell'oggetto Cube nella posizione iniziale
    # Arcotangente con gestione quadranti
    #z_R = math.atan2(y, x)  # in radianti
    #start_rotation = (0.0, 0.0, z_R)  # Posizione angolare iniziale (x_R, y_R, z_R)
    
    for f in range(frame_start +1, frame_end + 1 ):
        bpy.context.scene.frame_set(f)
        child_obj.location = start_location
        child_obj.keyframe_insert(data_path="location", frame=f)
        #child_obj.rotation_euler = start_rotation
        child_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    '''
    Terminine delle azioni per l'aggancio  dell'oggetto Cube al bone Wrist_rotation
    '''

def sgancioCube():
        # Imposta la Location e la Rotation del Cube ormai non più "Child of" con influece a 0.0 dal frame 331 al frame 410 
    
    
    # Nomi della scena
    armature_name = "Armature"      # Nome dell'oggetto armatura
    bone_name = "Wrist_rotation"    # Nome del bone
    object_name = "Cube"            # Nome dell'oggetto da collegare

    # Torna in modalità oggetto
    bpy.ops.object.mode_set(mode='OBJECT')


    # Recupera i riferimenti
    armature_obj = bpy.data.objects.get(armature_name)
    child_obj = bpy.data.objects.get(object_name)
    bone_obj = bpy.data.objects.get(bone_name)

     # Imposta la Location dell'oggetto Cube ormai non più "Child of" con influece a 0.0 dal frame 331 al frame 410 
    frame_start = 330   # Frame da cui iniziare la nuova posizione
    frame_end = 410     # Frame in cui termina l'animazione
    # Posizione globale (coordinate mondo)
    world_pos = child_obj.matrix_world.translation.copy()
    new_location = (world_pos.x,  world_pos.y , world_pos.z )  # Nuova posizione (x, y, z)
    # Rotazione globale (coordinate mondo)
    world_rot = child_obj.matrix_world.to_euler()
    new_rotation = (world_rot[0],  world_rot[1] , world_rot[2] )  # Nuova rotazione (x, y, z)

        
    for f in range(frame_start + 1, frame_end + 1):
        bpy.context.scene.frame_set(f)
        child_obj.location = new_location
        child_obj.keyframe_insert(data_path="location", frame=f)
        child_obj.rotation_euler = new_rotation
        child_obj.keyframe_insert(data_path="rotation_euler", frame=f)
    
    '''
    Terminine delle azioni per  lo sgancio dell'oggetto Cube dal bone Wrist_rotation
    '''


def ruotaCube(x, y, z):
    # dispone l'oggetto Cube da prendere, allineandolo con il centro della base del braccio in modo che possa essere preso con le pinze. Gli argomenti x, y, z sono le coordinate del centro dell'oggetto Cube da prendere
    
    # viene calcolato l'angolo di rotazione dell'oggetto Cube rispetto all'asse Z
    # math.atan2() è la funzione arcotangente con gestione quadranti
    rotZ = math.atan2(y, x)  # angolo di rotazione rispetto all'asse Z in radianti
    
    # viene ruotato l'oggetto Cube
    object_name = "Cube"
    # Verifica che l'oggetto esista nella scena prima di effettuare la rotazione
    if object_name in bpy.data.objects:
        obj = bpy.data.objects[object_name]
        #Imposta la rotazione in radianti rotZ sull'asse Z
        obj.rotation_euler[0] = 0.   # Asse X
        obj.rotation_euler[1] = 0.   # Asse Y
        obj.rotation_euler[2] = rotZ # Asse Z
        
    # fine di ruotaCube(x, y, z)


def posizioneCube():
    # rileva la posizione iniziale dell'oggetto Cube
    # Nome dell'oggetto da leggere
    object_name = "Cube"  

    # Verifica che l'oggetto esista nella scena
    if object_name in bpy.data.objects:
        obj = bpy.data.objects[object_name]
    
        # Lettura posizione (coordinate globali)
        location = obj.location  # Vector (x, y, z)
            
    # restituisce i valori della posizione location
    return location
  
  
def posizioneTarghet():
    # rileva la posizione  dell'oggetto Circle dove depositare l'oggetto Cube
    # Nome dell'oggetto da leggere
    object_name = "Targhet"  

    # Verifica che l'oggetto esista nella scena
    if object_name in bpy.data.objects:
        obj = bpy.data.objects[object_name]
    
        # Lettura posizione (coordinate globali)
        location = obj.location  # Vector (x, y, z)    
    # restituisce i valori della posizione location
    return location

    
def rimuoviAnimazioni():
    # rimozione delle animazioni create in precedenza
    
    # Nomi della scena
    armature_name = "Armature"      # Nome dell'oggetto armatura
    object_name = "Cube"            # Nome dell'oggetto  
    
    # Recupera i riferimenti
    armature_obj = bpy.data.objects.get(armature_name)
    cube_obj = bpy.data.objects.get(object_name)
    
    # Se gli oggetti Armature e Cube hanno dati di animazione, li rimuoviamo
    if armature_obj.animation_data:
        armature_obj.animation_data_clear()
    if cube_obj.animation_data:
        cube_obj.animation_data_clear()
    
    # Rimuove  i vincolo 'Child Of' dall'oggetto Cube
    for c in list(cube_obj.constraints):
        if c.type == "CHILD_OF":
            cube_obj.constraints.remove(c)
   
    # rimozione delle animazioni di Cubo_Dati_Base
    object_name = "Cubo_Dati_Base" 
    cube_obj = bpy.data.objects.get(object_name)
    if cube_obj.animation_data:
        cube_obj.animation_data_clear()   
   
    # rimozione delle animazioni di Cubo_Dati_Arm
    object_name = "Cubo_Dati_Arm" 
    cube_obj = bpy.data.objects.get(object_name)
    if cube_obj.animation_data:
        cube_obj.animation_data_clear()   

    # rimozione delle animazioni di Cubo_Dati_ForeArm
    object_name = "Cubo_Dati_ForeArm" 
    cube_obj = bpy.data.objects.get(object_name)
    if cube_obj.animation_data:
        cube_obj.animation_data_clear()   

    # rimozione delle animazioni di Cubo_Wrist_Vertical
    object_name = "Cubo_Dati_Wrist_Vertical" 
    cube_obj = bpy.data.objects.get(object_name)
    if cube_obj.animation_data:
        cube_obj.animation_data_clear()   

    # rimozione delle animazioni di Cubo_Dati_Wrist_rotation
    object_name = "Cubo_Dati_Wrist_rotation" 
    cube_obj = bpy.data.objects.get(object_name)
    if cube_obj.animation_data:
        cube_obj.animation_data_clear()   

    # rimozione delle animazioni di Cubo_Dati_Gear_Gripper_2
    object_name = "Cubo_Dati_Gear_Gripper_2" 
    cube_obj = bpy.data.objects.get(object_name)
    if cube_obj.animation_data:
        cube_obj.animation_data_clear()   






def rilevaMattoncino():
    # rileva dalla fotografia nel file Prova02.jpeg la posizione reale del mattoncino che deve prendere il braccio
    
    # 1. Si carica l'immagine e poi da essa viene creato un array NumPy contenente i pixel
    # con tre byte per ciascuno per esprimere il colore. Con RGB si esprimono le componenti
    # dei colori Red, Green, Blue i cui livelli variano ciascuno da 0 a 255.
    # Essi sono immessi in un array di dimensione 3: [R, G, B] per ciascun pixel
    # Le dimensioni dell'immagine in pixel è  width x height

    img = Image.open('/Users/enrico/Documents/blentinkerkit/prova5.jpg')
    pixels = img.load()
    width, height = img.size
    r_width = 800  # larghezza reale dell'immagine in mm
    r_height = 500   # altezza reale dell'immagine in mm
    img_array = np.array(img)
    print("Le dimensioni dell'immagine sono: ", width, height, "pixel")


    # 2. Definisci il range minimo e massimo per ogni canale (R, G, B)
    lower_bound = np.array([50, 60, 65])   # [R_min, G_min, B_min]
    upper_bound = np.array([60, 70, 75])  # [R_max, G_max, B_max]

    # 3. Trova i pixel che rientrano nel range per tutti e tre i canali
    maschera = np.all((img_array >= lower_bound) & (img_array <= upper_bound), axis=-1)


    # 4. Ottieni le coordinate (indici y, x) dei pixel individuati e il loro baricentro
    coordinata_y, coordinata_x = np.where(maschera)



    if (len(coordinata_x)!=0  and len(coordinata_y) != 0) :
        print(f"Trovati {len(coordinata_x)} pixel del colore nel range dei colori specificato.")
        x_p = sum(coordinata_x)// len(coordinata_x)
        y_p = sum(coordinata_y)// len(coordinata_y)
        x_b = x_p*(r_width/width)-r_width/2         # ascissa in mm del baricentro dell'oggetto Cube rispetto al centro dell'immagine
        y_b = r_height - 100 - y_p*(r_height/height)      # ordinata in mm del baricentro dell'oggetto Cube rispetto al bordo inferiore dell'immagine
        #print("Il baricentro dei pixel del colore specificato è nel pixel: ", x_p, y_p)
        #print("Il baricentro dei pixel del colore specificato ha coordinate: ", np.int64(x_b), "mm",np.int64(y_b),"mm")  
        
        # posiziona l'oggetto Cube nella posizione del mattoncino reale rilevata nella fotografia
        object_name = "Cube"
        # Verifica che l'oggetto esista nella scena prima di effettuare il posizionamento
        if object_name in bpy.data.objects:
            obj = bpy.data.objects[object_name]
            #Imposta la location del Cube
            obj.location.x = x_b/1000           # posizione x in metri del centro dell'oggetto Cube
            obj.location.y = y_b/1000           # posizione y in metri del centro dell'oggetto Cube
            obj.location.z = dz/2               # posizione z del centro dell'oggetto Cube
    else:
        print("Non esiste alcun pixel nel range dei colori specificato! ")

# fine di rilevaMattoncino()

    
    
    
    
    

def main():
    # main definisce l'ordine di esecuzione delle funzioni
    
    rimuoviAnimazioni()             # rimuove le precedenti animazioni
    
    rilevaMattoncino()              # rileva la posizione del mattoncino nella fotografia
    
    (x, y, z) = posizioneCube()     # determina la posizione dell'oggetto Cube da prendere
    
    ruotaCube(x, y, z)              # ruota l'oggetto Cube da prendere allineandolo con il braccio
    
    (theta1, theta2, theta3, theta4) = angoliPresaRilascioCube(x, y, z)       
    presaCube(theta1, theta2, theta3, theta4)
    
    aggancioCube(x, y, z, theta1, theta2, theta3, theta4)
    
    (tx, ty, tz) = posizioneTarghet()
    (theta1, theta2, theta3, theta4) = angoliPresaRilascioCube(tx, ty, tz)
    trasportoCube(theta1, theta2, theta3, theta4)
    sgancioCube()
   
    braccioaRiposo(theta1, theta2, theta3, theta4)
    

# programmi ausiliari



# programma principale
main()