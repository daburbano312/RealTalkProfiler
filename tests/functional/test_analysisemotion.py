from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
import time

# Usar Service y ChromeDriverManager para manejar el driver
service = Service(ChromeDriverManager().install())

# Configurar el WebDriver
driver = webdriver.Chrome(service=service)

# Acceder a la página
driver.get("http://localhost:5000")  # Asegúrate de que la aplicación esté corriendo

# Iniciar sesión si es necesario
email_field = driver.find_element(By.ID, "email")
password_field = driver.find_element(By.ID, "password")
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

email_field.send_keys("admin@example.com")
password_field.send_keys("password123")
login_button.click()

# Esperar que la página cargue completamente antes de interactuar con elementos
wait = WebDriverWait(driver, 10)  # Espera hasta 10 segundos para encontrar el elemento

# Esperar el botón de grabación y hacer clic
start_button = wait.until(EC.element_to_be_clickable((By.ID, "btnStart")))
start_button.click()

# Esperar que el prompt de cédula aparezca y manejarlo
try:
    # Espera hasta que el prompt esté presente
    alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
    
    # Enviar la cédula al prompt y aceptar
    alert.send_keys("1234567890")  # Aquí ingresamos la cédula que deseas utilizar
    alert.accept()  # Aceptar el prompt
    print("Cédula ingresada y prompt aceptado.")
except Exception as e:
    print(f"No se pudo manejar el prompt: {e}")

# Esperar a que el análisis de emociones se complete
try:
    # Esperar hasta que el análisis de emociones haya terminado y el texto sea diferente de "..."
    emotion_output = wait.until(EC.text_to_be_present_in_element((By.ID, "emotionOutput"), "..."))
    assert emotion_output.text != "..."  # Verificar que el resultado no es "..."
    print("Análisis de emociones completado.")
except Exception as e:
    print(f"No se pudo realizar el análisis de emociones correctamente: {e}")

# Detener grabación
stop_button = wait.until(EC.element_to_be_clickable((By.ID, "btnStop")))
assert stop_button.is_enabled()
stop_button.click()

time.sleep(2)  # Espera para detener la grabación

# Verificar que la grabación se ha detenido
assert start_button.is_enabled()

# Cerrar el navegador
driver.quit()
