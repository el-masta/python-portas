#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  autoportas.py
#  
#  Mario Rodríguez
#  
#  Llenado automático de portas, usando la base de datos.
#  
#  Pantalla inicia en X 0
#  Pantalla termina en X 470


#********VARIABLES DE OPERACIÓN******** IMPROTANTE VERIFICAR ANTES DE PORTAR**********
agencia='SAMAT'
operador='ATT'
intentos=60

#**** El promotor sin comentar será el que se use

promotor='Sin promotor'
#  NO   promotor='QUIROZ CHAVEZ ARACELI LIZET'
#-promotor='ORTIZ RODRIGUEZ VIVIAN FERNANDA'
#  NO   promotor='NAVARRO MENDOZA JONATHAN JOEL'
#promotor='ROSAS ALVARADO JOSE LUIS'
#  NO   promotor='DAVILA VERGEL ANDRES'
#promotor='MARTINEZ HERNANDEZ LIZET'
#promotor='HURTADO OSORNIO JOSE IVAN'
#  Tal vez   promotor='HERNANDEZ ORTIZ PERLA RAQUEL'


import mysql.connector as mariadb
from random import randrange
from datetime import date
import sys
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller
mouse = Controller()
from pynput.keyboard import Key, Controller as Ctrlr2
keybrd = Ctrlr2()
from PIL import Image
import pytesseract
import pyautogui
import cv2
import numpy as np
from time import time as tiempo
import time
import os
import requests, json

# Region de trabajo en pantalla (x,y,w,h)
window=(112,163,414,756)

# Configura MariaDB
config_maria = {'user': 'root','password': '*******','host': 'localhost','database': 'cisat','port':'3306'}
screendir='/home/mario/screenportas/'
# Inicia variables
curp,nombre,apep,apem=' ',' ',' ',' '
nl,tel,nip=' ',' ',' '
iccid,imei,idcop=' ',' ',' '
total=0
operadortemp=''


#imagenes para identificacion
imgdir='/home/mario/Telefonos/imgs/'
dashboard=imgdir+'dashboard.png'
img1=imgdir+'1.png'
img2=imgdir+'2.png'
yasolicitud=imgdir+'ya_solicitud.png'
imgconfirmar=imgdir+'confirmar.png'
imgexito=imgdir+'exito.png'
curpnoexiste=imgdir+'curpnoexiste.png'
valideiccid=imgdir+'valideiccid.png'
validenip=imgdir+'validenip.png'
curpincorrecto=imgdir+'curpincorrecto.png'
nopuedeser=imgdir+'nopuedeser.png'
curpnovalido=imgdir+'curpnovalido.png'
modifnombres=imgdir+'modifnombres.png'
yaestelcel=imgdir+'yaestelcel.png'
yatieneidcop=imgdir+'idcop.png'
f1=imgdir+'f1.png'
numincorrecto=imgdir+'numincorrecto.png'
valideimei=imgdir+'valideimei.png'
formatonodisponible=imgdir+'formatonodisponible.png'
usado=imgdir+'usado.png'
baja=imgdir+'baja.png'
java=imgdir+'java.png'
prepago=imgdir+'prepago.png'
nipdiferentes=imgdir+'nipsnoiguales.png'
parse=imgdir+'parse.png'
telnovalido=imgdir+'telnovalido.png'

# Identificar pantalla
def encontrar(img, y, h):
   ubicacion=pyautogui.locateOnScreen(img,region=(0, y, 470, h), grayscale=True, confidence=0.80)
   if ubicacion is not None:
      return True
   else:
      return False

# Obtiene datos de teléfono
def gettel():
   global operador, operadortemp
   if agencia=='CIRCULO' or agencia=="DREAM":
      datatel = requests.get('http://cisat.ap/api/numeros/dame0/'+operador).json()
   else :
      datatel = requests.get('http://cisat.ap/api/numeros/dame0/'+operador).json()
   if datatel:
      if operador.find('ATT')>=0:
         operadortemp='ATT'
      elif operador.find('MOVI')>=0:
         operadortemp='MOVISTAR'
      else:
         operadortemp=operador
      print('\t\tNúmero '+operador+' cargado:\t'+str(datatel[0]['nl'])+' - '+str(datatel[0]['numero'])+' '+str(datatel[0]['nip']) )
      return str(datatel[0]['nl']),str(datatel[0]['numero']),str(datatel[0]['nip'])
   else:
      print('Telefonos agotados')
      finalizar('Ya no hay TELEFONOS para portar')
         
# Actualiza telefono
def updatetel(razon):
   uptel = requests.put('http://cisat.ap/api/numeros/actualiza/'+tel+'/'+razon)
   time.sleep(0.1)
   return

# Obtiene datos del cliente
def getcurp():
   if agencia=='CLAPA':
      datacurp = requests.get('http://cisat.ap/api/curps/dameclapa').json()
   else:
      datacurp = requests.get('http://cisat.ap/api/curps/dame1').json()
   if datacurp:
      print('\t\tCURP cargado:\t\t'+datacurp[0]['curp']+' - '+datacurp[0]['nombre']+' '+datacurp[0]['apep']+' '+datacurp[0]['apem'])
      return datacurp[0]['curp'],datacurp[0]['nombre'],datacurp[0]['apep'],datacurp[0]['apem']
   else:
      print('CURPs agotados')
      finalizar('Ya no hay CURPS para portar')
         
# Borra datos del cliente
def deletecurp(curp):
   delcurp = requests.delete('http://cisat.ap/api/curps/borra/'+curp)
   time.sleep(0.3)
   return

# Marca CURP como procesado
def updatecurp():
   if agencia=='CLAPA':
      delcurp = requests.put('http://cisat.ap/api/curps/actualizaclapa/'+curp)
   else:
      delcurp = requests.put('http://cisat.ap/api/curps/actualiza/'+curp)
   time.sleep(0.1)
   return

#obtiene ICCID
def getchip():
   global intentos, total
   total+=1
   if total%20==0:
      reiniciar()
      print('REINICIANDO APP')
   print('Total: ' + str(total))
   
   dataiccid = requests.get('http://cisat.ap/api/iccids/dame1/'+agencia).json()
   if dataiccid:
      
      print('\n\nRestan '+str(intentos)+' ICCIDs por portar')
      if intentos==0 :
         finalizar('Se completaron todos los intentos')
      intentos-=1
      
      print('\t\tICCID de '+agencia+' cargado:\t'+dataiccid[0]['iccid'])
      return str(dataiccid[0]['iccid']), str(randrange(100000000000000, 999999999999999))
   else:
      print('ICCIDS AGOTADOS')
      finalizar('Ya no hay ICCID para portar')

# Actualiza ICCID
def updateiccid(razon):
   updiccid = requests.put('http://cisat.ap/api/iccids/actualiza/'+iccid+'/'+razon)
   time.sleep(0.1)
   return

# Carga datos desde BD
def getall():
   global nl,tel,nip,curp,nombre,apep,apem,iccid,imei
   nl,tel,nip=gettel()
   curp,nombre,apep,apem=getcurp()
   iccid,imei=getchip()

# Inicia la captura de datos
def llenar1():
   print('\t\tInicia rellenado de formulario 1')
   pyautogui.click(275,380) #Nombre
   time.sleep(0.2)
   pyautogui.click(80,270) #Combo tipo de plan
   time.sleep(0.6)
   pyautogui.click(60,300) #Plan Normal
   time.sleep(0.6)
   pyautogui.click(60,380) #Campo teléfono
   pyautogui.typewrite(tel)
   pyautogui.press('tab')
   time.sleep(0.2)
   pyautogui.typewrite(nombre)
   pyautogui.press('tab')
   time.sleep(0.2)
   pyautogui.typewrite(apep)
   pyautogui.press('tab')
   time.sleep(0.2)
   pyautogui.typewrite(apem)
   pyautogui.press('tab')
   time.sleep(0.2)
   pyautogui.typewrite(curp)
   time.sleep(0.3)
   pyautogui.click(235,870) #Siguiente
   return

# Continua Captura de 2a pantalla
def llenar2():
   print('\t\tInicia rellenado de formulario 2')
   pyautogui.click(55,450) #campo nip
   time.sleep(0.15)
   pyautogui.click(135,365) #seleccionar promocion
   time.sleep(0.5)
   if agencia=='CONECT' or agencia=='CIRCULO':
      pyautogui.click(135,440) #campo normal
   else:
      pyautogui.click(135,397) #campo normal
   time.sleep(0.5)
   pyautogui.click(55,450) #campo nip
   pyautogui.typewrite(nip)
   pyautogui.press('tab')
   pyautogui.typewrite(nip)
   pyautogui.press('tab')
   pyautogui.typewrite(iccid)
   pyautogui.press('tab')
   time.sleep(0.1)
   pyautogui.press('tab')
   time.sleep(0.1)
   pyautogui.typewrite(imei)
   time.sleep(0.1)
   pyautogui.click(350,870) #boton siguiente
   return

def llenar2ICCID():
   print('\t\tEscribe nuevo ICCID')
   pyautogui.click(135,612) #campo IMEI
   time.sleep(0.3)
   pyautogui.click(135,530) #campo ICCID
   time.sleep(0.2)
   pyautogui.typewrite(iccid)
   pyautogui.press('tab')
   pyautogui.press('tab')
   pyautogui.click(350,870) #boton siguiente
   return

#obtiene IDCOP desde pantalla
def getidcop():
   global idcop
   im= pyautogui.screenshot(region=(267,155,160,30))
   idcop=pytesseract.image_to_string(im)
   idcop=idcop.replace('/','7')
   print('Se encontro IDCOP:\t'+idcop)

#registra porta en BD

def regporta():
   global tel,operador,curp,iccid,agencia,idcop,promotor
   conn = mariadb.connect(**config_maria)
   cursor = conn.cursor(prepared=True)
   try:
      cursor.execute("INSERT INTO `portas` (fecha, telefono, operador, curp, iccid, agencia, idcop, mensaje, status, promotor) values (now(), '"+tel+"', '"+operadortemp+"', '"+curp+"', '"+iccid+"', '"+agencia+"', '"+idcop+"', 0, 'DESCONOCIDO', '"+promotor+"');" )
      conn.commit()
      cursor = conn.cursor(prepared=True)
      cursor.execute("UPDATE `candidatos` SET status='portado' WHERE numero='"+tel+"';" )
      conn.commit()
   except mariadb.Error as error:
      print("Error2: {}".format(error))
   finally:
      if(conn.is_connected() ):
         conn.close()
   time.sleep(1)
   print('\n\t*******************************')
   print('\t*                             *')
   print('\t*  REGISTRO de PORTA EXITOSO  *')
   print('\t*                             *')
   print('\t*******************************\n')
   updatecurp()
   updatetel(iccid)
   updateiccid(tel)
   getall()
   return

def screenshot(img):
   # ~ time.sleep(0.1)
   # ~ im = pyautogui.screenshot(region=(2,30, 470, 915))
   # ~ im.save(screendir+img+'.png', 'PNG', optimize=True)
   # ~ print("Imagen de pantalla guardada")
   # ~ time.sleep(0.1)
   pass
   
def reiniciar():
   time.sleep(1)
   pyautogui.click(342,942) #minimiza aplicación
   time.sleep(1)
   pyautogui.click(236,857) #cierra todas las ventanas
   time.sleep(1)
   pyautogui.click(64,265) #Abre app
   time.sleep(1)
   pyautogui.click(100,204) #Iniciar semáforo
   time.sleep(1)
   pass
   
def finalizar(razon):
   print('FINALIZADO - '+razon)
   sys.exit(main(sys.argv))
      
def main(args):
   return 0

if __name__ == '__main__':
   #Confirmación de datos
   print('\t**********************************')
   print('\tSe van a realizar '+str(intentos)+' portaciones para:')
   print('\tAgencia:\t'+agencia)
   print('\toperador:\t'+operador)
   print('\tPromotor:\t'+promotor)
   print('\t**********************************\n')
   confirmacion= raw_input('Enter para continuar, Ctrl-C para cancelar\n')
   pyautogui.hotkey('winleft','right') #Acomoda consola
   #Comieza ciclo
   bucle=True
   start_time = tiempo()
   getall()
   #Enfocando ScrCpy
   print('\n\tCambiando ventana de operación')
   time.sleep(0.1)
   while bucle==True:
    
      if tel!='VACIO' and iccid!='VACIO' :
         #Comienza porta
         print('\nIniciando porta...')
         if encontrar(dashboard,260,128) is True:
            elapsed_time = tiempo() - start_time
            print('\tDashboard encontrado')
            print("\t\tTiempo: %.2f segundos" % elapsed_time)
            start_time = tiempo()
            pyautogui.click(415,325) #Iniciar portabilidad
            time.sleep(1)
         if encontrar(prepago,260,128) is True:
            print('\t\tIcono prepago identificado')
            pyautogui.click(415,325) #Solicitudes prepago
            time.sleep(1)
                  
         #Llena primer pantalla
         if encontrar(img1,130,120) is True:
            print('\tIniciando captura 1')
            ok=False
            llenar1()
            #Verifica llenado correcto 
            while ok is False:
               print('\t\tVerificando captura 1')
               if encontrar(img2,230,160) is True:
                  print('\t\t\tCaptura 1 CORRECTA')
                  ok=True
               else:
                  print('\t\t\tBuscando errores')
                  if encontrar(curpnoexiste,400,60) is True:
                     print('***** CURP inexistente')
                     deletecurp(curp)
                     curp,nombre,apep,apem=getcurp()
                     screenshot('curp-no-existe')
                     pyautogui.click(370,570)
                     llenar1()
                  elif encontrar(curpincorrecto,420,70) is True:
                     print('***** Re-escribiendo CURP')
                     screenshot('curp-incorrecto')
                     pyautogui.click(380,525)
                     time.sleep(0.6)
                     pyautogui.press('del')
                     time.sleep(0.2)
                     llenar1()
                  elif encontrar(modifnombres,440,260) is True:
                     print('***** Reintentando')
                     screenshot('modificacion-de-nombre')
                     pyautogui.click(336,586)
                     llenar1()
                  elif encontrar(parse,400,55) is True:
                     print('***** Reintentando')
                     screenshot('parse-error')
                     pyautogui.click(365,565)
                     time.sleep(0.5)
                     pyautogui.click(250,870)
                  elif encontrar(numincorrecto,430,70) is True:
                     print('***** Re-escribiendo numero')
                     screenshot('numero-incorrecto')
                     pyautogui.click(360,250)
                     llenar1()
                  elif encontrar(yasolicitud,460,65) is True:
                     print('***** El numero ya tiene solicitud')
                     updatetel('Ya_tiene_solicitud_a_otro_nombre')
                     screenshot('ya-tiene-solicitud')
                     nl,tel,nip=gettel()
                     pyautogui.click(370,555)
                     llenar1()
                  elif encontrar(nopuedeser,420,100) is True:
                     print('***** El numero no puede ser procesado')
                     screenshot('no-puede-ser-procesado')
                     updatetel('No_puede_ser_procesado')
                     nl,tel,nip=gettel()
                     pyautogui.click(370,540)
                     llenar1()
                  elif encontrar(telnovalido,420,100) is True:
                     print('***** Numero no valido para proceso')
                     screenshot('numero-no-valido')
                     updatetel('No_puede_ser_procesado')
                     nl,tel,nip=gettel()
                     pyautogui.click(370,540)
                     llenar1()
                  elif encontrar(yaestelcel,430,70) is True:
                     print('***** El numero ya es TELCEL')
                     screenshot('ya-es-telcel')
                     updatetel('El_número_ya_es_TELCEL')
                     nl,tel,nip=gettel()
                     pyautogui.click(375,530)
                     llenar1()
                  elif encontrar(yatieneidcop,420,100) is True:
                     print('***** El numero ya tiene IdCop')
                     screenshot('ya-tiene-idcop')
                     updatetel('Ya cuenta con IdCop')
                     nl,tel,nip=gettel()
                     pyautogui.click(365,540)
                     llenar1()
                  elif encontrar(curpnovalido,400,70) is True:
                     print('***** CURP no valido')
                     screenshot('curp-no-valido')
                     deletecurp(curp)
                     curp,nombre,apep,apem=getcurp()
                     pyautogui.click(375,555)
                     llenar1()
               #pyautogui.click(440,789)
                
            #Llena segunda pantalla
            print('\tLlenando caputura 2...')
            ok=False
            foto=False
            getidcop()
            llenar2()
            #Verifica llenado correcto
            while ok is False:
               print('\t\t\tVerificando')
               if encontrar(imgconfirmar,165,60) is True:
                  print('\t\t\t\tCORRECTO')
                  if foto is False:
                     screenshot('confirmacion')
                     foto=True
                  pyautogui.click(240,880)
                  if encontrar(imgexito,405,110) is True:
                     pyautogui.click(380,545)
                     regporta()
                     ok=True
               elif encontrar(java,495,80) is True:
                  print('***** Intentando nuevamente')
                  screenshot('error-java')
                  pyautogui.click(316,602)
                  time.sleep(1)
                  pyautogui.click(426,871)
               elif encontrar(valideiccid,440,260) is True:
                  print('***** Error ICCID')
                  screenshot('error-iccid')
                  pyautogui.click(316,577)
                  time.sleep(0.1)
                  llenar2()
               elif encontrar(nipdiferentes,425,60) is True:
                  print('***** Error de captura en NIP')
                  screenshot('nip-diferente')
                  pyautogui.click(360,515)
                  time.sleep(0.25)
                  llenar2()
               elif encontrar(validenip,430,50) is True:
                  print('***** Error de captura en NIP')
                  screenshot('error-nip')
                  pyautogui.click(370,520)
                  time.sleep(0.25)
                  llenar2()
               elif encontrar(usado,460,60) is True:
                  print('***** ICCID - Usado')
                  screenshot('iccid-usado')
                  updateiccid('USADO')
                  iccid,imei=getchip()
                  pyautogui.click(360,550)
                  time.sleep(0.1)
                  llenar2ICCID()
               elif encontrar(baja,485,40) is True:
                  print('***** ICCID - BAJA')
                  screenshot('iccd-baja')
                  updateiccid('BAJA')
                  iccid,imei=getchip()
                  pyautogui.click(365,555)
                  time.sleep(0.1)
                  llenar2ICCID()
               elif encontrar(f1,475,30) is True:
                  print('***** El numero ya tiene trámite F1')
                  screenshot('ya-hay-tramite-f1')
                  updatetel('Ya tiene tramite de F1')
                  pyautogui.click(365,566)
                  print('Reiniciar proceso')
                  terminar()
               elif encontrar(formatonodisponible,440,60) is True:
                  print('***** Intentando nuevamente')
                  screenshot('formato-no-disponible')
                  pyautogui.click(370,555)
                  time.sleep(1)
                  pyautogui.click(350,870)
               elif encontrar(valideimei,440,260) is True:
                  print('***** Error IMEI')
                  screenshot('error-imei')
                  pyautogui.click(316,577)
                  time.sleep(0.1)
                  llenar2()
               #pyautogui.click(440,800)
                  

      else:
         #Ya no hay datos para procesar
         bucle=False
         finalizar('Ya no hay elementos para portar')
         
   sys.exit(main(sys.argv))
