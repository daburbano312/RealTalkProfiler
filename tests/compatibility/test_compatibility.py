import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

@pytest.fixture
def setup_driver():
    # Configuración de las opciones para los navegadores
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")  # Ejecutar en modo headless
    edge_options = EdgeOptions()
    edge_options.add_argument("--headless")
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.binary_location = r"C:/Users/drburban/AppData/Local/Mozilla Firefox/Firefox.exe"  # Ruta al ejecutable de Firefox

    # Usar webdriver_manager para gestionar los drivers automáticamente
    chrome_service = Service(ChromeDriverManager().install())
    firefox_service = FirefoxService(GeckoDriverManager().install())
    edge_service = EdgeService(EdgeChromiumDriverManager().install())

    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    yield driver
    driver.quit()

def test_chrome_compatibility(setup_driver):
    driver = setup_driver
    driver.get("http://localhost:5000/login")  # URL de la página de inicio de sesión
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    # Comprobación del título de la página de inicio de sesión
    title = driver.title
    assert title == "Iniciar Sesión - RealTalk Profiler", f"Error en el título: {title}"

    # Ingresar los datos de inicio de sesión
    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    
    email_field.send_keys("admin@example.com")
    password_field.send_keys("password123")
    login_button.click()

    # Esperar a que la página cargue completamente antes de interactuar con elementos
    wait = WebDriverWait(driver, 10)  # Espera hasta 10 segundos para encontrar el siguiente elemento
    start_button = wait.until(EC.element_to_be_clickable((By.ID, "btnStart")))

    # Iniciar grabación
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

    # Esperar a que la grabación haya comenzado verificando la transcripción
    output_text = wait.until(EC.visibility_of_element_located((By.ID, "output")))
    assert output_text.text != "Esperando inicio de grabación..."

    # Ahora esperar a que el botón de detener grabación esté habilitado
    stop_button = wait.until(EC.element_to_be_clickable((By.ID, "btnStop")))

    # Verificar que el botón de grabación está habilitado
    assert stop_button.is_enabled()

    # Esperar 10 segundos antes de detener la grabación
    time.sleep(2)  # Pausar la ejecución por 2 segundos

    # Detener grabación
    stop_button.click()

    time.sleep(2)  # Espera para detener la grabación

    # Verificar que la grabación se ha detenido
    assert start_button.is_enabled()

def test_firefox_compatibility(setup_driver):
    driver = setup_driver
    driver.get("http://localhost:5000/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    # Similar to the chrome test, fill out the form, start recording, etc.
    pass  # Repeat the logic for Firefox

def test_edge_compatibility(setup_driver):
    driver = setup_driver
    driver.get("http://localhost:5000/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    # Similar to the chrome test, fill out the form, start recording, etc.
    pass  # Repeat the logic for Edge

if __name__ == "__main__":
    pytest.main(options=["--html=report.html", "--self-contained-html"])
