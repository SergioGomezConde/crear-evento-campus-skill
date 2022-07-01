import json
import time
from datetime import date
from datetime import datetime

from mycroft import MycroftSkill, intent_file_handler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# Fichero JSON donde almacenar la informacion
ficheroJSON = '/home/serggom/scraping/datos.json'
contenidoJSON = {'asignaturas': [], 'usuario': [], 'eventos': [], 'siguiente_evento': [], 'eventos_hoy': [],
                 'numero_mensajes': []}


def inicio_sesion(self):
    # Datos de acceso fijos
    usuario = 'e71180769r'
    contrasena = 'p5irZ9Jm4@9C#6WUaE!z9%@V'

    # Modo headless
    options = Options()
    options.headless = True
    options.add_argument("--windows-size=1920,1200")

    # Acceso a pagina
    driver = webdriver.Chrome(options=options)
    driver.get('https://campusvirtual.uva.es/login/index.php')

    # Inicio de sesion
    driver.find_element(by=By.NAME, value='adAS_username').send_keys(usuario)
    driver.find_element(
        by=By.NAME, value='adAS_password').send_keys(contrasena)
    driver.find_element(by=By.NAME, value='adAS_submit').click()

    # Aceptar cookies
    driver.implicitly_wait(10)
    driver.find_element(
        by=By.XPATH, value='/html/body/div[1]/div/a[1]').click()

    return driver


def mes_a_numero(x):  # Funcion que devuelve el numero de mes introducido de manera escrita
    return {
        'enero': "01",
        'febrero': "02",
        'marzo': "03",
        'abril': "04",
        'mayo': "05",
        'junio': "06",
        'julio': "07",
        'agosto': "08",
        'septiembre': "09",
        'octubre': "10",
        'noviembre': "11",
        'diciembre': "12",
    }[x]


# Funcion que devuelve una lista con dia, mes y anio
def formatear_fecha_introducida(dia_a_formatear):
    dia_en_numero = str(dia_a_formatear).split(" ")[1]
    mes_en_numero = mes_a_numero(str(dia_a_formatear).split(" ")[3])

    dia_separado = [dia_en_numero, mes_en_numero, str(date.today().year)]

    return dia_separado


class CrearEventoCampus(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('campus.evento.crear.intent')
    def handle_campus_evento_crear(self, message):

        # Solicitud y obtencion del nombre del evento a crear
        texto_response = self.get_response('solicitarnombre')
        self.log.info(texto_response)

        # Solicitud y obtencion del dia del evento a crear
        dia_response = self.get_response('solicitardia')
        self.log.info(dia_response)

        # Obtencion de los numeros de dia, mes y anio
        dia_separado = formatear_fecha_introducida(dia_response)
        numero_dia = int(dia_separado[0])
        numero_mes = int(dia_separado[1])
        numero_anio = int(dia_separado[2])

        # Por defecto se toma el anio actual
        fecha = str(numero_dia) + "/" + str(numero_mes) + "/" + str(numero_anio)

        # Comprobacion de que la fecha aun no ha pasado
        if (numero_mes < date.today().month) or (
                (numero_mes == date.today().month) and (numero_dia < date.today().day)):
            self.speak("La fecha introducida ya ha pasado")

        else:
            # Solicitud y obtencion de la hora del evento a crear
            hora_response = self.get_response('solicitarhora')
            hora_minuto = str(hora_response).split(" ")[2].split(":")

            # Obtencion de los numeros de hora y minuto
            hora = int(hora_minuto[0])
            if len(hora_minuto) == 1:
                minuto = 0
                minuto_a_mostrar = "00"
            else:
                minuto = int(hora_minuto[1])
                minuto_a_mostrar = str(hora_minuto[1])

            contenidoJSON['eventos'].append({
                'nombre': texto_response,
                'fecha': fecha,
                'hora': str(hora) + ":" + minuto_a_mostrar
            })

            with open(ficheroJSON, 'a') as ficheroDatosJSON:
                json.dump(contenidoJSON, ficheroDatosJSON, indent=4)

            ficheroDatosJSON.close()

            # Obtencion de la fecha en segundos desde epoch
            segundos = (datetime(numero_anio, numero_mes, numero_dia,
                                 0, 0) - datetime(1970, 1, 1)).total_seconds()

            driver = inicio_sesion(self)

            # Acceso al dia en el que crear el evento
            driver.get(
                'https://campusvirtual.uva.es/calendar/view.php?view=day&time=' + str(segundos))

            # Click sobre el boton de crear evento
            driver.implicitly_wait(10)
            driver.find_element(
                by=By.XPATH,
                value="/html/body/div[4]/div[2]/div/div/section/div/div/div/div/div[1]/div/div[1]/button").click()

            time.sleep(5)

            # Escribir el nombre del evento
            driver.implicitly_wait(20)
            driver.find_element(
                by=By.NAME, value='name').send_keys(texto_response)

            # Seleccion de la hora a la que crear el evento
            selector_hora = driver.find_element(
                by=By.XPATH,
                value='/html/body/div[7]/div[2]/div/div/div[2]/form/fieldset/div/div[2]/div[2]/fieldset/div/div[4]/span/select')
            drop = Select(selector_hora)
            drop.select_by_index(hora)

            # Seleccion del minuto a la que crear el evento
            selector_minuto = driver.find_element(
                by=By.XPATH,
                value='/html/body/div[7]/div[2]/div/div/div[2]/form/fieldset/div/div[2]/div[2]/fieldset/div/div[5]/span/select')
            drop = Select(selector_minuto)
            drop.select_by_index(minuto)

            time.sleep(5)

            # Click sobre el boton de guardar el evento
            driver.find_element(
                by=By.XPATH, value="/html/body/div[7]/div[2]/div/div/div[3]/button").click()

            time.sleep(5)

            # Confirmacion de la creacion del evento con su nombre, fecha y hora
            self.speak("Evento " + texto_response + " creado " +
                       fecha + " a las " + str(hora) + ":" + minuto_a_mostrar)


def create_skill():
    return CrearEventoCampus()
