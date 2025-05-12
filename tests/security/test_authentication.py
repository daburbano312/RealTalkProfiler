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

# Prueba de autenticación
def test_authentication():
    test_name = "Prueba de Autenticación"
    start_time = time.time()  # Inicio del cronómetro

    try:
        driver.get("http://localhost:5000/login")
        login_page = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "remember"))  # Asegúrate de que este selector sea correcto
        )

        execution_time = time.time() - start_time  # Tiempo de ejecución
        save_metrics(test_name, "Éxito", execution_time, "Redirigido a la página de inicio de sesión.")
        print(f"{test_name} - Éxito: {execution_time:.2f} segundos")

    except Exception as e:
        execution_time = time.time() - start_time
        save_metrics(test_name, "Fallo", execution_time, str(e))
        print(f"{test_name} - Fallo: {str(e)}")

    driver.quit()  # Cerrar el navegador

# Ejecutar la prueba de autenticación
test_authentication()

# Guardar los resultados en un archivo CSV
save_results_to_csv()
