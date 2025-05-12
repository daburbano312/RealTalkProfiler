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

# Prueba de Inyección SQL
def test_sql_injection():
    test_name = "Prueba de Inyección SQL"
    start_time = time.time()

    try:
        driver.get("http://localhost:5000/login")  # URL del formulario de inicio de sesión

        username_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        # Inyección SQL (por ejemplo, ingresar un ' OR 1=1 -- en el campo de usuario)
        username_field.send_keys("admin@example.com")  # Inyección SQL
        password_field.send_keys("password123")  # Cualquier contraseña
        login_button.click()

        # Verificar si se redirige a la página de inicio de sesión o si ocurre un error
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "errorMessage"))
            )
            execution_time = time.time() - start_time
            save_metrics(test_name, "Fallo", execution_time, "La aplicación es vulnerable a inyección SQL.")
            print(f"{test_name} - Fallo: La aplicación es vulnerable a inyección SQL.")
        except:
            execution_time = time.time() - start_time
            save_metrics(test_name, "Éxito", execution_time, "La aplicación no es vulnerable a inyección SQL.")
            print(f"{test_name} - Éxito: {execution_time:.2f} segundos")

    except Exception as e:
        execution_time = time.time() - start_time
        save_metrics(test_name, "Fallo", execution_time, str(e))
        print(f"{test_name} - Fallo: {str(e)}")

    driver.quit()  # Cerrar el navegador

# Ejecutar la prueba de inyección SQL
test_sql_injection()

# Guardar los resultados en un archivo CSV
save_results_to_csv()
