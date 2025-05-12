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

# Prueba de XSS (Cross-Site Scripting)
def test_xss():
    test_name = "Prueba de XSS"
    start_time = time.time()

    try:
        driver.get("http://localhost:5000/login")  # URL donde se envían comentarios o entradas de usuario

        comment_field = driver.find_element(By.ID, "email")
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")

        # Inyección XSS (por ejemplo, un script de alerta)
        comment_field.send_keys('<script>alert("XSS")</script>')  # Inyección XSS
        submit_button.click()

        # Verificar si la alerta de JavaScript se ejecuta
        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())  # Espera que aparezca la alerta
            execution_time = time.time() - start_time
            save_metrics(test_name, "Fallo", execution_time, "La aplicación es vulnerable a XSS.")
            print(f"{test_name} - Fallo: La aplicación es vulnerable a XSS.")
        except:
            execution_time = time.time() - start_time
            save_metrics(test_name, "Éxito", execution_time, "La aplicación no es vulnerable a XSS.")
            print(f"{test_name} - Éxito: {execution_time:.2f} segundos")

    except Exception as e:
        execution_time = time.time() - start_time
        save_metrics(test_name, "Fallo", execution_time, str(e))
        print(f"{test_name} - Fallo: {str(e)}")

    driver.quit()  # Cerrar el navegador

# Ejecutar la prueba de XSS
test_xss()

# Guardar los resultados en un archivo CSV
save_results_to_csv()
