import requests
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# -------------------
# CONFIGURACIÓN
# -------------------
API_URL = "http://127.0.0.1:8084/listarDatosEstructurados"
FECHA = datetime.now().strftime("%Y-%m-%d")  # Obtiene la fecha actual del sistema en formato YYYY-MM-DD
INTERVALO_HORAS = 28  # cada cuántas horas se ejecuta

# -------------------
# FUNCIONES
# -------------------
def check_api(API_URL,PROYECTO_ID,CODIGO_INTERNO,FECHA):
    """
    Consulta la API y verifica si hay al menos un dato para el proyecto,
    dispositivo y fecha especificados.
    """
    try:

        url = API_URL + "?tabla=datos&disp.id_proyecto=" + PROYECTO_ID + "&limite=1&disp.codigo_interno=" + CODIGO_INTERNO + "&fecha_inicio=" + FECHA
        response = requests.get(url)


        datos = response.json()
        print(datos)
        if datos["status"] == "fail":
            alerta(API_URL,PROYECTO_ID,CODIGO_INTERNO,FECHA)
        else:
            print(f"{datetime.now()}: Datos encontrados ✅. Total: {len(datos['data']['tableData'])}")
    except Exception as e:
        print(f"{datetime.now()}: ERROR al consultar la API ❌ - {e}")

def alerta(API_URL,PROYECTO_ID,CODIGO_INTERNO,FECHA):
    """
    Acción de alerta si no hay datos.
    """
    print(f"{datetime.now()}: ALERTA! No hay datos para proyecto {PROYECTO_ID}, dispositivo {CODIGO_INTERNO} en fecha {FECHA}")

    send_email_alert(API_URL,PROYECTO_ID,CODIGO_INTERNO,FECHA)

def send_email_alert(API_URL,PROYECTO_ID,CODIGO_INTERNO,FECHA):
       # Servidor Cmas
    # servidorcmas@gmail.com
    
    sender = "servidorcmas@gmail.com"
    receiver = "dkressing@udd.cl"
    subject = f"Alerta: Faltan datos en dispositivo {CODIGO_INTERNO}."
    body = f"No hay datos para proyecto {PROYECTO_ID}, dispositivo {CODIGO_INTERNO} en fecha {FECHA}"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            # server.login(sender, "Investigacion2023")
            server.login(sender, "yniu gfrb bsls digo")
            server.sendmail(sender, receiver, msg.as_string())
        print(f"{datetime.now()}: Correo de alerta enviado a {receiver}")
    except Exception as e:
        print(f"{datetime.now()}: ERROR al enviar correo de alerta ❌ - {e}")

# -------------------
# BUCLE PRINCIPAL
# -------------------
if __name__ == "__main__":
    while True:
        # DICTUC
        check_api(API_URL,"6","SOIL-01",FECHA)
        check_api(API_URL,"6","SOIL-02",FECHA)
        check_api(API_URL,"6","SOIL-03",FECHA)
        check_api(API_URL,"6","SOIL-04",FECHA)
        check_api(API_URL,"6","SOIL-05",FECHA)
        check_api(API_URL,"6","SOIL-06",FECHA)
        check_api(API_URL,"6","SOIL-07",FECHA)
        check_api(API_URL,"6","SOIL-08",FECHA)

        
        print(f"{datetime.now()}: Esperando {INTERVALO_HORAS} horas para la siguiente ejecución...\n")
        #time.sleep(60)  # convertir horas a segundos
        time.sleep(INTERVALO_HORAS * 3600)  # convertir horas a segundos
