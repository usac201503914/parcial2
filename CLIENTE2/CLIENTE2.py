import paho.mqtt.client as paho
import logging
import time
import random
import socket
import threading #Concurrencia con hilos
import binascii
import os
from datetime import datetime
from brokerData_01 import * #Informacion de la conexion

#USER_ID = "201503914"
#TOPIC_USER_ID="comandos/25/201503914"

'''
--------------------------PJAM INICIO Configuración_01 Logging-------------------------------------------------------------------
'''

#PJAM Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    )

'''
--------------------------PJAM FINAL Configuración_01 Logging-------------------------------------------------------------------
'''

class InicioMQTT(object):

    def  __init__(self):
        logging.debug("init")
        self.bandera_recepcion_trama = 0
        self.trama_entrante = b''
        self.tamaño_trama = 0
        self.STOP = 1
        #self.TOPIC_USER_ID=TOPIC_USER_ID

        host=MQTT_HOST
        puerto=MQTT_PORT
        #topic=self.TOPIC_USER_ID

        #PJAM Inicia la configuración del cliente MQTT
        self.__setupMQTTClient(host,puerto)

        #PJAM Suscripción a topic
        self.Configuracion()

        self.FUNCION()

    
    '''
    -------------------PJAM LECTURA TEXTO PLANO------------------------------------------------------------------
    '''
    def Configuracion(self):
        salas_file = [] #PJAM lista que guardará el usuario y las salas
        path_to_script = os.path.dirname(os.path.abspath(__file__)) #PJAM instrucción que devuelve la dirección de este archivo
        usuario_conf = os.path.join(path_to_script, "usuario.txt")  #PJAM isntrucción que une la dirección con el nombre del documento .txt
        f= open(usuario_conf, "r")
        for line in f:
            salas_file.append(line)
        f.close()

        salas_conf = os.path.join(path_to_script, "salas.txt")
        f= open(salas_conf, "r")
        for line in f:
            salas_file.append(line)
        f.close()
        for i in range(len(salas_file)):
            salas_file[i] = salas_file[i].replace('\n', '') #PJAM remplaza los saltos de linea con espacio vacío
            if salas_file[i]=="":
                del salas_file[i]
        logging.debug(salas_file)                                                                                                                                                                                                                        
        self.__mqttSubscribe(salas_file)

    '''
    -------------------PJAM INICIO Configuración del cliente MQTT------------------------------------------------------------------
    '''

    def __setupMQTTClient(self,MQTT_HOST,MQTT_PORT):

        self.client = paho.Client(clean_session=True) #PJAM Nueva instancia de cliente
        self.client.on_connect = self.on_connect #PJAM Se configura la funcion "Handler" cuando suceda la conexion
        self.client.on_publish = self.on_publish #PJAM Se configura la funcion "Handler" que se activa al publicar algo
        self.client.on_message = self.on_message
        self.client.username_pw_set(MQTT_USER, MQTT_PASS) #PJAM Credenciales requeridas por el broker
        self.client.connect(host=MQTT_HOST, port = MQTT_PORT) #PJAM Conectar al servidor remoto

    '''
    -------------------PJAM INICIO Configuración Subscripcion MQTT-----------------------------------------------------------------
    '''
    #Función para subscribirse a cada uno de los grupos sacados del archivo salas, subscribirse a los audios y al propio tema
    def __mqttSubscribe(self, salas_file, qos=2):
        self.salas_file = salas_file #globalizamos lista para utilizarla en el resto de la clase
        TOPIC="usuarios/25"+salas_file[0]
        self.client.subscribe((TOPIC, qos))
        for i in range(len(salas_file)):
            if i ==0:
                TOPIC="usuarios/25/"+salas_file[0]
            else:
                TOPIC="salas/25/"+salas_file[i]
            self.client.subscribe((TOPIC, qos))
            logging.debug(TOPIC)    
        for i in range(len(salas_file)):
            if i ==0:
                TOPIC="audio/25/"+salas_file[0]
            else:
                TOPIC="audio/25/"+salas_file[i]
            self.client.subscribe((TOPIC, qos))
            logging.debug(TOPIC)        


    '''
    -------------------PJAM Función publicación MQTT-----------------------------------------------------------------
    '''

    #PJAM Invoke one-shot publish to MQTT default broker
    def __mqttPublish(self,topic,data):
        self.client.publish(topic=topic,payload=data,qos=1)
    '''
    -------------------PJAM publicación MQTT----------------------------------------------------------------
    '''
    #PJAM Handler en caso se publique satisfactoriamente en el broker MQTT
    def on_publish(self,client, userdata, mid): 
        publishText = "Publicacion satisfactoria"
        logging.debug(publishText)

    '''
    -------------------PJAM Recepción mensajes MQTT----------------------------------------------------------------
    '''

    #PJAM Callback que se ejecuta cuando llega un mensaje al topic suscrito
    def on_message(self,client, userdata, msg):
        end="end"
        cod=end.encode()
        #Se muestra en pantalla informacion que ha llegado
        #logging.debug("Ha llegado el mensaje al topic: " + str(msg.topic))
        #logging.debug("El contenido del mensaje es: " + str(msg.payload))

        #Recepción_Audio(msg.topic,msg.payload,self.salas_file)
        if self.bandera_recepcion_trama == 0: 
            for i in range(len(self.salas_file)):
                if i ==0:
                    TOPIC="audio/25/"+self.salas_file[0]
                    TOPIC_1="usuarios/25/"+self.salas_file[0]
                    if (str(msg.topic))== TOPIC:
                        logging.info("PREPARANDO PARA RECIBIR AUDIO DE USUARIO PERSONAL")
                        self.tamaño_trama=int(msg.payload)
                        self.bandera_recepcion_trama = 1
                        logging.debug(self.tamaño_trama)
                        break
                    elif (str(msg.topic))== TOPIC_1:
                        logging.info("MENSAJE ENTRANTE DE USUARIO PERSONAL")
                        logging.info(str(msg.payload))
                        break
                else:
                    TOPIC="audio/25/"+self.salas_file[i]
                    TOPIC_1="salas/25/"+self.salas_file[i]
                    if (str(msg.topic))== TOPIC:
                        logging.info("PREPARANDO PARA RECIBIR AUDIO DE SALA")
                        self.tamaño_trama=int(msg.payload)
                        self.bandera_recepcion_trama = 1
                        break
                    elif (str(msg.topic))== TOPIC_1:
                        logging.info("MENSAJE ENTRANTE DE SALA")
                        logging.info(str(msg.payload))
                        break
                        
            
        elif self.bandera_recepcion_trama == 1:
            if str(msg.payload) == str(cod):
                logging.debug(len(self.trama_entrante))
                logging.debug(self.tamaño_trama)
                if len(self.trama_entrante) == self.tamaño_trama:
                    logging.info("MENSAJE DE AUDIO RECIBIDO EXITOSAMENTE")
                else:
                    logging.warning("MENSAJE DE AUDIO NO RECIBIDO")
                    logging.warning("INTENTE DE NUEVO")

                self.Reconstruccion_audio(self.trama_entrante)

                self.bandera_recepcion_trama = 0
                self.trama_entrante = b''
                self.tamaño_trama = 0    
            else:
                self.trama_entrante+=msg.payload
                logging.debug(len(self.trama_entrante))
            

    '''
    -------------------PJAM conexión broker MQTT----------------------------------------------------------------
    '''

    #PJAM Handler en caso suceda la conexion con el broker MQTT
    def on_connect(self,client, userdata, flags, rc): 
        connectionText = "CONNACK recibido del broker con codigo: " + str(rc)
        logging.info(connectionText)

    '''
    -------------------PJAM loop MQTT----------------------------------------------------------------
    '''
    #Función que mantendrá conectado al cliente al broker
    def FUNCION(self):
        try:
            logging.info("Cliente MQTT con paho-mqtt") #Mensaje en consola
            self.client.loop_start()
            while self.STOP==1:
                self.menu()
        except KeyboardInterrupt:
            logging.warning("Desconectando del broker MQTT...")
        finally:
            self.client.loop_stop() 
            self.client.disconnect()
            logging.info("Se ha desconectado del broker. Saliendo...")

    '''
    -------------------RMJD Función CLEAR-----------------------------------------------------------------
    '''

    def clear(self):
        os.system('clear')

    #RMJD Creando las funciones integrantes del menu

    '''
    -------------------RMJD Función DESTINO-----------------------------------------------------------------
    '''

    def destino(self): #RMJD Imprime las opciones de destino
        logging.info("\nEscoja destino:\n")
        logging.info("a. Enviar a usuario ")
        logging.info("b. Enviar a sala")
        logging.info("c. Regresar a menu\n")

    '''
    -------------------RMJD Función MENSAJE-----------------------------------------------------------------
    '''

    def mensaje(self): #RMJD lugar donde se ingresa el mensaje a enviar
        logging.info("Escriba el mensaje que desea enviar")
        self.msj = input()
        logging.info("El mensaje enviado es: \n" + self.msj)

    '''
    -------------------RMJD Función VOZ-----------------------------------------------------------------
    '''

    def voz(self,duracion,userID): #RMJD lugar donde se graba el mensaje de voz a enviar
        path_to_script = os.path.dirname(os.path.abspath(__file__)) #PJAM instrucción que devuelve la dirección de este archivo
        self.usuario_conf = os.path.join(path_to_script, "prueba_02_examen02.wav")  #PJAM isntrucción que une la dirección con el nombre del documento .txt

        logging.info('Comenzando grabacion')
        os.system('arecord -d' + str(duracion) + ' -f U8 -r 8000 '+ self.usuario_conf)
        self.Envio_Voz(userID)

    '''
    -------------------RMJD Función ENVIO DE VOZ-----------------------------------------------------------------
    '''

    def Envio_Voz(self,userID): #RMJD lugar donde se graba el mensaje de voz a enviar
        binario1=b''
        a=1

        f= open(self.usuario_conf, "rb")    #PJAM se abre el archivo de audio en modo lectura de bits

        tamaño_trama=f.read()               #PJAM se avisa el tamaño de la trama que será enviada
        data=str(len(tamaño_trama))
        self.__mqttPublish(userID,data)

        f.close()                           #se cierra y se vuelve a abrir el docuemnto ya que solo puede ser leido una vez por apertura

        f= open(self.usuario_conf, "rb")

        while a==1:
            binario=f.read(200)
            if binario:
                binario1+=binario
                self.__mqttPublish(userID,binario)
                #logging.debug(len(binario1))
            else:
                a=2

        data="end"
        self.__mqttPublish(userID,data)

        f.close()
    '''
    -------------------RMJD Función RECONSTRUCCIÓN AUDIO-----------------------------------------------------------------
    '''
    def Reconstruccion_audio(self,audio_bits):
        logging.debug(len(audio_bits))

        now = datetime.now()
        timestamp = datetime.timestamp(now)

        nombre_archivo= str(timestamp)+".wav"

        path_to_script = os.path.dirname(os.path.abspath(__file__)) #PJAM instrucción que devuelve la dirección de este archivo
        direccion_audio_recibido = os.path.join(path_to_script, nombre_archivo) 

        q= open(direccion_audio_recibido,'wb')
        q.write(audio_bits)
        logging.debug(type(q))
        q.close()

        Reproduccion_hilos(direccion_audio_recibido,timestamp)

        '''
        logging.info('GRABACIÓN FINALIZADA, INCIA REPRODUCCION')
        os.system('aplay '+ direccion_audio_recibido)
        '''
    
    '''
    -------------------RMJD Función creación hilos-----------------------------------------------------------------
    '''

    '''
    -------------------RMJD Función ERROR-----------------------------------------------------------------
    '''

    def errorOpcion(self): #RMJD error que aparece solo si no se ingresa un valor valido
        self.clear()
        logging.info("No ha ingresado una opcion valida.  Intente de nuevo")

    '''
    -------------------RMJD Función OPCION FINAL-----------------------------------------------------------------
    '''

    def finalOpcion(self): #RMJD metodo donde el usuario escoge si regresa o no al menu
        logging.info("Ingrese:\n 1. Salir a menu \n 2. Cerrar chat")
        p = input()

        if p == "1":
            self.menu()

        elif p == "2":
            self.exit()

        else:
            self.errorOpcion()
            self.finalOpcion()

    '''
    -------------------RMJD Función ENVIAR TEXTO-----------------------------------------------------------------
    '''

    def enviarTexto(self): # RMJD funcion correspondiente a enviar un texto
        self.clear()
        logging.info ("\nEnviar mensaje de Texto")
        self.destino()
        choice2 = input()

        if choice2 == "a":
            logging.info("\nEnviar mensaje privado a: ")
            userID = input() #Variable donde se ingresa el ID del usuario
            self.mensaje()
            topic="usuarios/25/"+str(userID)
            self.__mqttPublish(topic,self.msj)
            logging.info("\nMensaje enviado a " + userID)
            self.finalOpcion()
    
        elif choice2 == "b":
            logging.info("\nEnviar mensaje a la sala: ")
            salaID = input() #Variable que guarda el ID de la sala destino
            self.mensaje()
            topic="salas/25/"+str(salaID)
            self.__mqttPublish(topic,self.msj)
            logging.info("\nMensaje enviado a " + salaID)
            self.finalOpcion()

    
        elif choice2 == "c":
            self.menu()

        else:
            self.errorOpcion()
            self.enviarTexto()

    '''
    -------------------RMJD Función ENVIAR VOZ-----------------------------------------------------------------
    '''

    def enviarVoz(self): # RMJD funcion correspondiente a enviar mensaje de voz
        self.clear()
        logging.info ("\nEnviar mensaje de Voz")
        self.destino()
        choice2 = input()

        if choice2 == "a":
            logging.info("\nEnviar mensaje privado a: ")
            userID = input() #Variable donde se ingresa el ID del usuario
            topic="audio/25/"+str(userID)
            logging.info("\nIngrese duracion en segundos")
            duracion = input()# Variable que guarda la duracion del mensaje de voz
            self.voz(duracion,topic)
            logging.info("\nMensaje enviado a " + userID)
            self.finalOpcion()

        elif choice2 == "b":
            logging.info("\nEnviar mensaje a la sala: ")
            salaID = input() #Variable que guarda el ID de la sala destino
            topic="audio/25/"+str(salaID)
            logging.info("\nIngrese duracion en segundos")
            duracion = input()# Variable que guarda la duracion del mensaje de voz
            self.voz(duracion,topic)
            logging.info("\nMensaje enviado a " + salaID)
            self.finalOpcion()

        elif choice2 == "c":
            self.menu()
        else:
            self.errorOpcion()
            self.enviarVoz()

    '''
    -------------------RMJD Función EXIT-----------------------------------------------------------------
    '''
     
    def exit(self): #RMJD funcion que sale de la interfaz de usuario
        self.clear()
        input("\nCerrando la sesion, presione Enter para finalizar")
        logging.warning("Desconectando del broker MQTT...")
        self.client.loop_stop() 
        self.client.disconnect()
        logging.info("Se ha desconectado del broker. Saliendo...")
        self.STOP = 0

    '''
    -------------------RMJD Función MENU-----------------------------------------------------------------
    '''

    def menu(self): #RMJD 
        self.clear()
        logging.info("1. Enviar Texto")
        logging.info("2. Enviar mensaje de voz")
        logging.info("3. Exit")
        choice = input("\nIngrese la opcion: ")

        if choice == "1":
            self.enviarTexto()
        elif choice == "2":
            self.enviarVoz()
        elif choice == "3":
            self.exit()

        else:
            self.clear()
            self.errorOpcion()
            self.menu()

class Reproduccion_hilos(object):
    def  __init__(self,direccion_audio,nombre_audio):
        self.direccion_audio = direccion_audio
        self.nombre_audio = nombre_audio
        self.Creacion_hilos()
        

    def Creacion_hilos(self):
        
        t1 = threading.Thread(name = 'Reproducción Audio' +str(self.nombre_audio),
                            target = self.Reproduccion_audio_reconstruido,
                            args = (()),
                            daemon = True
                            )
        t1.start()

    def Reproduccion_audio_reconstruido(self):
        logging.info('GRABACIÓN FINALIZADA, INCIA REPRODUCCION')
        os.system('aplay '+ self.direccion_audio)



#USER_ID = "201503914"
#TOPIC_USER_ID="comandos/25/"+str(USER_ID)


#try:
InicioMQTT() # IRM Debugging disabled
#except KeyboardInterrupt:
	#logging.info("Killing Meteo!") 
	#del myMeteo
