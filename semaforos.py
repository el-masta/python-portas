#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  autoportas.py
#  
#  Copyright 2019 Mario Rodríguez <mario@intelipages.com>
#  
#  Semaforo para numeros candidatos a portacion.
#  
#  Pantalla inicia en 3,45
#  Pantalla termina en 303,595

import mysql.connector as mariadb
import cv2
import random
import pyautogui
import numpy as np
from time import time as tiempo
import time
import os

# Region de trabajo en pantalla (x,y,w,h)
window=(3,45,300,550)

# Configura MariaDB
config_maria = {'user': 'Mario','password': '*****','host': 'cisat.ap','database': 'cisat','port':'3306'}

# Inicia variables
tel, ope, sem, nombre, apep, apem=' ',' ',' ',' ',' ',' '
operador='MOVIST'
total=0
haytel=False


#imagenes para identificacion
directorio='/home/mario/Escritorio/share/PythonScripts/imgsemaforo/'
imgdash=directorio+'dash.png'
img1=directorio+'1.png'
img2=directorio+'2.png'
yasolicitud=directorio+'ya_solicitud.png'
yaestelcel=directorio+'yaestelcel.png'
numincorrecto=directorio+'numincorrecto.png'
nopuede=directorio+'no_puede_ser_procesado.png'
yaidcop=directorio+'yatieneidcop.png'
java=directorio+'java.png'
rojo=directorio+'rojo.png'
verde=directorio+'verde.png'

# Funcion para identificar pantalla -------------
def encontrar(img, y, h):
   ubicacion=pyautogui.locateOnScreen(img,region=(3, y, 300, h), grayscale=False, confidence=0.87)
   if ubicacion is not None:
      return True
   else:
      return False

# Funcion que obtiene el siguiente telefono a semaforear -----------
def gettel():
   global total
   global haytel
   conn = mariadb.connect(**config_maria)
   cursor = conn.cursor()
   try:
      cursor.execute("SELECT numero, operador, nombre, apep, apem FROM `candidatos` WHERE STATUS='verde' AND operador ='"+operador+"' ORDER BY RAND() LIMIT 1")
      records=cursor.fetchall()
      if len(records)!=0:
         for NUM, OPE, NOM, APEP, APEM in records:
			total+=1
			print(str(total)+' - TELEFONO: '+str(NUM)+'\tOPERADOR: '+str(OPE)+'\t'+NOM+' '+APEP+' '+APEM )
			haytel=True
			return str(NUM), str(OPE), NOM, APEP, APEM
      else:
		 haytel=False
		 print('-*-*-NO HAY TELEFONOS PARA HACER SEMAFORO-*-*-')
		 return 'VACIO', 'VACIO'
   except mariadb.Error as error:
      print("Error2: {}".format(error))
   finally:
      if(conn.is_connected() ):
         conn.close()

#Funcion que borra telefono de BD
def deltel():
   global tel, ope, nombre, apep, apem
   conn = mariadb.connect(**config_maria)
   cursor = conn.cursor(prepared=True)
   try:
      cursor.execute("DELETE FROM `candidatos`  WHERE numero ='"+tel+"' ")
      conn.commit()
   except mariadb.Error as error:
      print("Error2: {}".format(error))
   finally:
      if(conn.is_connected() ):
         conn.close()
   time.sleep(0.5)
   print('Número eliminado de BD: '+tel)
   tel,ope,nombre,apep,apem=gettel()
   return

#Funcion que marca telefono como verde
def updatetel():
   global tel, ope, nombre, apep, apem
   conn = mariadb.connect(**config_maria)
   cursor = conn.cursor(prepared=True)
   try:
      cursor.execute("UPDATE `candidatos` SET status = 'verde2' WHERE numero ='"+tel+"' ")
      conn.commit()
   except mariadb.Error as error:
      print("Error2: {}".format(error))
   finally:
      if(conn.is_connected() ):
         conn.close()
   time.sleep(0.5)
   tel,ope,nombre,apep,apem=gettel()
   return

          
# Avanzar a partir del dash
def iniciarsemaforo():
   time.sleep(0.2)
   pyautogui.click(150,210) #Click icono Iniciar Portabilidad
   time.sleep(0.5)
   p1=False
   while p1==False:
      print('Buscando pantalla 1...')
      if encontrar(img1,75,100) is True:
         p1=True
         print('ENCONTRADO')
         pyautogui.click(150,175) #Combo tipo de plan
         time.sleep(0.2)
         pyautogui.click(46,231) #Elige promo 50

# Inicia la captura de datos
def llenar1():
   pyautogui.click(170,240) #campo Nombre
   time.sleep(0.1)
   pyautogui.click(60,240) #Campo Telefono
   pyautogui.press('backspace')
   time.sleep(0.1)
   pyautogui.typewrite(tel)
   pyautogui.press('tab')
   pyautogui.typewrite(nombre)
   pyautogui.press('tab')
   pyautogui.typewrite(apep)
   pyautogui.press('tab')
   pyautogui.typewrite(apem)
   time.sleep(0.5)
   pyautogui.click(150,560) #Siguiente
   return

def reiniciar():
   time.sleep(1)
   pyautogui.click(222,609) #minimiza aplicacion
   time.sleep(1)
   pyautogui.click(153,558) #cierra todas las aplicaciones
   time.sleep(5)
   pyautogui.click(41,178) #Abre app
   time.sleep(4)

def main(args):
   return 0

if __name__ == '__main__':
   #Inicia semáforo --------------
   tel, ope, nombre, apep, apem=gettel()
   aceptados=0.0
   actual=1

   # ~ for i in range(300):
   while (haytel==True):
      if total%30==0:
         reiniciar()
      if encontrar(imgdash,160,100) is True:
         iniciarsemaforo()
         time.sleep(0.5)
      if encontrar(img1,75,100) is True:
         llenar1()
         ok=False
         while ok is False:
            print('Buscando pantalla 2')
            time.sleep(0.5)
            if encontrar(img2,130,130) is True:
               print('CORRECTO')
               ok=True
            else:
               #print('Buscando errores')
               if encontrar(numincorrecto,290,120) is True:
                  pyautogui.click(150,345) #Boton aceptar
                  time.sleep(0.2)
                  print('Numero mal escrito') 
                  llenar1()
               elif encontrar(yasolicitud,290,60) is True:
                  print('Numero ya tiene solicitud')
                  deltel()
                  actual+=1
                  print('Telefono '+str(actual)+' cargado.')
                  pyautogui.click(155,365) # Boton aceptar
                  time.sleep(0.2)
                  llenar1()
               elif encontrar(nopuede,260,90) is True:
                  print('No puede ser procesado')
                  deltel()
                  actual+=1
                  print('Telefono '+str(actual)+' cargado.')
                  pyautogui.click(155,365) # Boton aceptar
                  time.sleep(0.2)
                  llenar1()
               elif encontrar(yaestelcel,260,90) is True:
                  print('Numero ya es Telcel')
                  deltel()
                  actual+=1
                  print('Telefono '+str(actual)+' cargado.')
                  pyautogui.click(155,355) #bOTON ACEPTAR
                  time.sleep(0.2)
                  llenar1()
               elif encontrar(yaidcop,250,100) is True:
                  deltel()
                  actual+=1
                  print('Ya tiene IdCop')
                  print('Telefono '+str(actual)+' cargado.')
                  pyautogui.click(150,365)
                  time.sleep(0.2)
                  llenar1()
               elif encontrar(java,240,120) is True:
                  print('Reintendando...')
                  pyautogui.click(150,375)
                  time.sleep(2)
                  pyautogui.click(150,560)
                               
         #Leer segunda pantalla
         print('Buscando semáforo...')
         ok2=False
         intentos=0
         #Verifica semáforo
         while ok2 is False:
			if intentos>8:
			   print('Reintentando')
			   pyautogui.click(90,560) #Boton regresar
			   time.sleep(2)
			   pyautogui.click(150,560) #Siguiente
			   time.sleep(4)
			   intentos=0
			print('escaneando...')
			if encontrar(img2,150,100) is True:
			   print('-REGISTRADO-')
			   pyautogui.click(90,560) #Boton regresar
			   # # Obtiene telefono siguiente
			   aceptados+=1
			   print('Van %.0f'%aceptados+' aceptados, {:.1%} de los revisados'.format(aceptados/actual) )
			   updatetel()
			   actual+=1
			   ok2=True
			intentos+=1

   #Ya no hay datos para procesar
   print(str(aceptados)+' nuevos números con semaforo.')
   exit()
