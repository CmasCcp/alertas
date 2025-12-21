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
RAM_THRESHOLD = 50  # Porcentaje de RAM que dispara la alerta
RAM_CHECK_INTERVAL = 70  # Segundos entre verificaciones de RAM (1 minuto)
last_ram_alert_time = 0  # Para evitar spam de alertas de RAM

# Configuración para monitoreo de CPU
CPU_THRESHOLD = 80  # Porcentaje de CPU que dispara la alerta
CPU_CHECK_INTERVAL = 60  # Segundos entre verificaciones de CPU
last_cpu_alert_time = 0  # Para evitar spam de alertas de CPU

# Configuración para monitoreo de almacenamiento
STORAGE_THRESHOLD = 80  # GB mínimos de almacenamiento disponible
STORAGE_CHECK_INTERVAL = 120  # Segundos entre verificaciones de almacenamiento
last_storage_alert_time = 0  # Para evitar spam de alertas de almacenamiento

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

def check_cpu_usage():
    """
    Verifica el uso de CPU y envía alerta si excede el umbral configurado.
    """
    global last_cpu_alert_time
    
    try:
        # Obtener uso de CPU (promedio durante 1 segundo)
        cpu_percent = psutil.cpu_percent(interval=1)
        
        print(f"{datetime.now()}: Uso de CPU: {cpu_percent:.1f}%")
        
        # Verificar si excede el umbral
        if cpu_percent > CPU_THRESHOLD:
            current_time = time.time()
            # Evitar spam de alertas (enviar solo una vez cada 30 minutos)
            if current_time - last_cpu_alert_time > 1800:  # 30 minutos = 1800 segundos
                send_cpu_alert(cpu_percent)
                last_cpu_alert_time = current_time
        
    except Exception as e:
        print(f"{datetime.now()}: ERROR al verificar CPU ❌ - {e}")

def send_cpu_alert(cpu_percent):
    """
    Envía alerta por correo cuando el uso de CPU excede el umbral.
    """
    sender = "servidorcmas@gmail.com"
    receiver = "dkressing@udd.cl"
    subject = f"🚨 ALERTA: Uso elevado de CPU - {cpu_percent:.1f}%"
    
    # Obtener información adicional de CPU
    cpu_count = psutil.cpu_count(logical=False)  # Núcleos físicos
    cpu_count_logical = psutil.cpu_count(logical=True)  # Núcleos lógicos
    cpu_freq = psutil.cpu_freq()
    
    body = f"""
🚨 ALERTA DE USO DE CPU 🚨

El uso de CPU ha excedido el umbral configurado.

📊 Detalles de CPU:
• Uso actual: {cpu_percent:.1f}%
• Umbral configurado: {CPU_THRESHOLD}%
• Núcleos físicos: {cpu_count}
• Núcleos lógicos: {cpu_count_logical}
• Frecuencia actual: {cpu_freq.current:.0f} MHz (si disponible)

⏰ Fecha y hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Por favor, revisa los procesos en ejecución y optimiza el uso de CPU si es necesario.
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
        print(f"{datetime.now()}: 🚨 Alerta de CPU enviada - Uso: {cpu_percent:.1f}%")
    except Exception as e:
        print(f"{datetime.now()}: ERROR al enviar alerta de CPU ❌ - {e}")

def cpu_monitor_thread():
    """
    Función que se ejecuta en un hilo separado para monitorear la CPU continuamente.
    """
    print(f"{datetime.now()}: 🔍 Iniciando monitoreo de CPU (umbral: {CPU_THRESHOLD}%)")
    while True:
        check_cpu_usage()
        time.sleep(CPU_CHECK_INTERVAL)

def check_storage_usage():
    """
    Verifica el almacenamiento disponible y envía alerta si está por debajo del umbral.
    """
    global last_storage_alert_time
    
    try:
        # Obtener información del disco principal (C: en Windows, / en Linux)
        disk_usage = psutil.disk_usage('/')
        
        # Convertir bytes a GB
        total_gb = disk_usage.total / (1024**3)
        used_gb = disk_usage.used / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        used_percent = (disk_usage.used / disk_usage.total) * 100
        
        print(f"{datetime.now()}: Almacenamiento libre: {free_gb:.2f} GB ({100-used_percent:.1f}% libre)")
        
        # Verificar si el espacio libre está por debajo del umbral
        if free_gb < STORAGE_THRESHOLD:
            current_time = time.time()
            # Evitar spam de alertas (enviar solo una vez cada 30 minutos)
            if current_time - last_storage_alert_time > 1800:  # 30 minutos = 1800 segundos
                send_storage_alert(free_gb, total_gb, used_gb, used_percent)
                last_storage_alert_time = current_time
        
    except Exception as e:
        print(f"{datetime.now()}: ERROR al verificar almacenamiento ❌ - {e}")

def send_storage_alert(free_gb, total_gb, used_gb, used_percent):
    """
    Envía alerta por correo cuando el almacenamiento disponible está bajo.
    """
    sender = "servidorcmas@gmail.com"
    receiver = "dkressing@udd.cl"
    subject = f"🚨 ALERTA: Almacenamiento bajo - {free_gb:.2f} GB libres"
    
    body = f"""
🚨 ALERTA DE ALMACENAMIENTO 🚨

El espacio libre en disco está por debajo del umbral configurado.

💾 Detalles de almacenamiento:
• Espacio libre: {free_gb:.2f} GB
• Umbral mínimo: {STORAGE_THRESHOLD} GB
• Espacio total: {total_gb:.2f} GB
• Espacio utilizado: {used_gb:.2f} GB ({used_percent:.1f}%)
• Espacio libre: {100-used_percent:.1f}%

⏰ Fecha y hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Por favor, libera espacio en disco eliminando archivos innecesarios o transfiriéndolos a otra ubicación.
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
        print(f"{datetime.now()}: 🚨 Alerta de almacenamiento enviada - Libre: {free_gb:.2f} GB")
    except Exception as e:
        print(f"{datetime.now()}: ERROR al enviar alerta de almacenamiento ❌ - {e}")

def storage_monitor_thread():
    """
    Función que se ejecuta en un hilo separado para monitorear el almacenamiento continuamente.
    """
    print(f"{datetime.now()}: 🔍 Iniciando monitoreo de almacenamiento (mínimo: {STORAGE_THRESHOLD} GB)")
    while True:
        check_storage_usage()
        time.sleep(STORAGE_CHECK_INTERVAL)

# -------------------
# BUCLE PRINCIPAL
# -------------------
if __name__ == "__main__":
    # Iniciar los hilos de monitoreo
    print(f"{datetime.now()}: 🚀 Iniciando sistema de monitoreo completo...")
    
    # Hilo de monitoreo de RAM
    ram_thread = threading.Thread(target=ram_monitor_thread, daemon=True)
    ram_thread.start()
    
    # Hilo de monitoreo de CPU
    cpu_thread = threading.Thread(target=cpu_monitor_thread, daemon=True)
    cpu_thread.start()
    
    # Hilo de monitoreo de almacenamiento
    storage_thread = threading.Thread(target=storage_monitor_thread, daemon=True)
    storage_thread.start()
    
    print(f"{datetime.now()}: ✅ Todos los monitores iniciados correctamente")
    
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
