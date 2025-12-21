import requests
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import psutil
import threading

# -------------------
# CONFIGURACIÓN
# -------------------
API_URL = "http://127.0.0.1:8084/listarDatosEstructurados"
FECHA = datetime.now().strftime("%Y-%m-%d")  # Obtiene la fecha actual del sistema en formato YYYY-MM-DD
INTERVALO_HORAS = 28  # cada cuántas horas se ejecuta

# Configuración para monitoreo de RAM
RAM_THRESHOLD = 70  # Porcentaje de RAM que dispara la alerta
RAM_CHECK_INTERVAL = 70  # Segundos entre verificaciones de RAM (1 minuto)
last_ram_alert_time = 0  # Para evitar spam de alertas de RAM

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

def check_ram_usage():
    """
    Verifica el uso de RAM y envía alerta si excede el umbral configurado.
    """
    global last_ram_alert_time
    
    try:
        # Obtener información de memoria
        memory = psutil.virtual_memory()
        ram_percent = memory.percent
        
        print(f"{datetime.now()}: Uso de RAM: {ram_percent:.1f}%")
        
        # Verificar si excede el umbral
        if ram_percent > RAM_THRESHOLD:
            current_time = time.time()
            # Evitar spam de alertas (enviar solo una vez cada 30 minutos)
            if current_time - last_ram_alert_time > 1800:  # 30 minutos = 1800 segundos
                send_ram_alert(ram_percent, memory)
                last_ram_alert_time = current_time
        
    except Exception as e:
        print(f"{datetime.now()}: ERROR al verificar RAM ❌ - {e}")

def send_ram_alert(ram_percent, memory):
    """
    Envía alerta por correo cuando el uso de RAM excede el umbral.
    """
    sender = "servidorcmas@gmail.com"
    receiver = "dkressing@udd.cl"
    subject = f"🚨 ALERTA: Uso elevado de RAM - {ram_percent:.1f}%"
    
    # Convertir bytes a GB para mayor legibilidad
    total_gb = memory.total / (1024**3)
    used_gb = memory.used / (1024**3)
    available_gb = memory.available / (1024**3)
    
    body = f"""
🚨 ALERTA DE MEMORIA RAM 🚨

El uso de memoria RAM ha excedido el umbral configurado.

📊 Detalles de memoria:
• Uso actual: {ram_percent:.1f}%
• Umbral configurado: {RAM_THRESHOLD}%
• Memoria total: {total_gb:.2f} GB
• Memoria utilizada: {used_gb:.2f} GB
• Memoria disponible: {available_gb:.2f} GB

⏰ Fecha y hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Por favor, revisa los procesos en ejecución y libera memoria si es necesario.
    """
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, "yniu gfrb bsls digo")
            server.sendmail(sender, receiver, msg.as_string())
        print(f"{datetime.now()}: 🚨 Alerta de RAM enviada - Uso: {ram_percent:.1f}%")
    except Exception as e:
        print(f"{datetime.now()}: ERROR al enviar alerta de RAM ❌ - {e}")

def ram_monitor_thread():
    """
    Función que se ejecuta en un hilo separado para monitorear la RAM continuamente.
    """
    print(f"{datetime.now()}: 🔍 Iniciando monitoreo de RAM (umbral: {RAM_THRESHOLD}%)")
    while True:
        check_ram_usage()
        time.sleep(RAM_CHECK_INTERVAL)

# -------------------
# BUCLE PRINCIPAL
# -------------------
if __name__ == "__main__":
    # Iniciar el hilo de monitoreo de RAM
    ram_thread = threading.Thread(target=ram_monitor_thread, daemon=True)
    ram_thread.start()
    
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
