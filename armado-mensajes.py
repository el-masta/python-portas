#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Envía mensajes de portas'''
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "sirmcoil73@gmail.com"
__author__      = "Mario Rodríguez"

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import time
import pyperclip as clipboard
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller
mouse = Controller()
from pynput.keyboard import Key, Controller as Ctrlr2
keybrd = Ctrlr2()
import mysql.connector as mariadb



def on_press(key):
   try:
      print(key.char)

   except AttributeError:
      #print('special key {0} pressed'.format(key) )
      if (key==Key.cmd):
         pegarmsg()
         
def pegarmsg():
   total=0
   conn = mariadb.connect(host='localhost', port='3306', user='*****', password='*****', database='portas')
   cursor = conn.cursor()
   cursor2 = conn.cursor(prepared=True)
   try:
      cursor.execute("SELECT ID, TELEFONO, NOMBRE, APEP, APEM, IDCOP, ICCID FROM `t_portas` WHERE MENSAJE=0 ORDER BY ID LIMIT 10")
      records=cursor.fetchall()
      for ID, TELEFONO, NOMBRE, APEP, APEM, IDCOP, ICCID in records:
         total+=1
         msgid=str(ID)
         msg='NOMBRE DEL PROMOTOR: HERNANDEZ CUEVAS VERONICA ALEJANDRA\n'
         msg+='SUPERVISOR: VACANTE\n'
         msg+='NUMERO A PORTAR: '+ str(TELEFONO)+'\n'
         msg+='CLIENTE: '+str(NOMBRE)+' '+str(APEP)+' '+str(APEM)+'\n'
         msg+='NUMERO SECUENCIAL: '+ str(IDCOP)+'\n'
         msg+='SIM: '+ str(ICCID)+'\n'
         msg+='COMPAÑÍA: MOVISTAR\n'
         msg+='PROMOCIÓN: 50\n'
         msg+='EQUIPO: NAUCALPAN\n'
         msg+='COLOR: VERDE';
         clipboard.copy(msg)
         time.sleep(0.3)
         with keybrd.pressed(Key.ctrl):
            keybrd.press('v')
            keybrd.release('v')
         time.sleep(0.3)
         keybrd.press(Key.enter)
         keybrd.release(Key.enter)
         try:
            cursor2.execute("UPDATE `t_portas` SET MENSAJE=1 WHERE ID='"+msgid+"'")
            conn.commit()
            #print(str(ID)+"- ",cursor2.rowcount, "fila afectada")
         except mariadb.Error as error:
            print(str(ID)+"-Error1: {}".format(error))
         print(total)

         
   except mariadb.Error as error:
      print("Error2: {}".format(error))

   finally:
      if(conn.is_connected() ):
         conn.close()
      print('TERMINADO')
   

# Collect events until released
with keyboard.Listener(on_press=on_press) as listener:
   listener.join()
