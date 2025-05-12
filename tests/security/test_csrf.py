import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Lista para almacenar las métricas
metrics = []

# Función para guardar las métricas en el archivo CSV
def save_metrics(test_name, status, execution_time, message=""):
    metrics.append([test_name, status, execution_time, message])

# Guardar los resultados al final de la ejecución
def save_results_to_csv():
    with open('security_tests_results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Test", "Estado", "Tiempo de Ejecución (segundos)", "Mensaje"])
        for metric in metrics:
            writer.writerow(metric)

# Configuración del WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Prueba de CSRF (Cross-Site Request Forgery)
def test_csrf():
    test_name = "Prueba de CSRF"
    start_time = time.time()

    try:
        driver.get("http://localhost:5000/login")  # URL de configuración de la cuenta

        # Iniciar sesión si es necesario
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        email_field.send_keys("admin@example.com")
        password_field.send_keys("password123")
        login_button.click()

        # Realizar una acción que cambie la configuración sin CSRF token
        driver.get("http://localhost:5000/settings/update?name=malicious")  # URL manipulada del atacante

        # Verificar si la acción fue permitida
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "errorMessage"))
            )
            execution_time = time.time() - start_time
            save_metrics(test_name, "Éxito", execution_time, "Protección CSRF activa.")
            print(f"{test_name} - Éxito: {execution_time:.2f} segundos")
        except:
            execution_time = time.time() - start_time
            save_metrics(test_name, "Fallo", execution_time, "La aplicación es vulnerable a CSRF.")
            print(f"{test_name} - Fallo: La aplicación es vulnerable a CSRF.")

    except Exception as e:
        execution_time = time.time() - start_time
        save_metrics(test_name, "Fallo", execution_time, str(e))
        print(f"{test_name} - Fallo: {str(e)}")

    driver.quit()  # Cerrar el navegador

# Ejecutar la prueba de CSRF
test_csrf()

# Guardar los resultados en un archivo CSV
save_results_to_csv()
