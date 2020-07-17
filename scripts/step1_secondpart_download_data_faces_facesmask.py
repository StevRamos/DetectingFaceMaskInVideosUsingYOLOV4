# FUENTE: https://stackoverflow.com/questions/61190450/unable-to-scrape-google-images-selenium

# Con este script se descargan imagenes y se guardan en un directorio creado
# Por este mismo script. El nombre de las imagenes seran enumeradas desde 1 
# hasta el maximo de imagenes que se desea.
# Luego de que este script cree una carpeta con imagenes segun los parametros 
# de busqueda, este folder se guardara en un drive compartido para el 
# entrenar el modelo a desarrollar con YOLOv4

#Se importan las librerias que se usaran en este script
import base64
import os
import requests
import time

from io import BytesIO
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

#Con la ayuda de este DRIVER descargaremos imagenes de google imagenes
CHROME_DRIVER_LOCATION = r'C:/Users/monte/Downloads/chromedriver.exe'
SEARCH_TERMS = ['people','wears','masks','ukraine','png']   #Termino de busqueda

#Las imagenes se descargan en este directorio
TARGET_SAVE_LOCATION = os.path.join(r'C:/Users/monte/.spyder-py3/images/', '_'.join([x.capitalize() for x in SEARCH_TERMS]),  r'{}.{}')
if not os.path.isdir(os.path.dirname(TARGET_SAVE_LOCATION)):
    os.makedirs(os.path.dirname(TARGET_SAVE_LOCATION))

#
def check_if_result_b64(source):
    possible_header = source.split(',')[0]
    if possible_header.startswith('data') and ';base64' in possible_header:
        image_type = possible_header.replace('data:image/', '').replace(';base64', '')
        return image_type
    return False


#Funcion diseñada para usar el DRIVER de manera adecuada,
#es decir, se adecua el driver para la version de google actual
#o cambios en el html la pagina web google imagenes
def get_driver():

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/80.0.3987.132 Safari/537.36'
    options = Options()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--allow-cross-origin-auth-prompt")

    new_driver = webdriver.Chrome(executable_path=CHROME_DRIVER_LOCATION, options=options)
    new_driver.get(f"https://www.google.com/search?q={'+'.join(SEARCH_TERMS)}&source=lnms&tbm=isch&sa=X")
    return new_driver



driver = get_driver()

#Debido a que deseamos descargar la maxima cantidad de imagenes
#Con los terminos de busqueda propuesto, hacemos un scrolling
#Para cargar una pagina con mayor cantidad de imagenes
print("start scrolling to generate more images on the page...")
# Se hace un scroll automatico 500 veces o hasta que la pag web
# alcance el limite de imagenes
for _ in range(500):
    driver.execute_script("window.scrollBy(0,10000)")

first_search_result = driver.find_elements_by_xpath('//a/div/img')[0]
first_search_result.click()

right_panel_base = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'''//*[@data-query="{' '.join(SEARCH_TERMS)}"]''')))
first_image = right_panel_base.find_elements_by_xpath('//*[@data-noaft="1"]')[0]
magic_class = first_image.get_attribute('class')
image_finder_xp = f'//*[@class="{magic_class}"]'


# Tiempo de esperar para que la primera imagen cargue
time.sleep(3)

# Se obtienen las caracteristicas del html que tengan 'src',
# Pues este es el link donde se encuentra almacenada la imagen
thumbnail_src = driver.find_elements_by_xpath(image_finder_xp)[-1].get_attribute("src")


# Se define el rango de imagenes que se descargaran
for i in range(700):

    # Todos los imagenes comparte el mismo tag 'img'.
    # [-2] es el elemento que se visualiza actualmente
    print("image number xyz")
    target = driver.find_elements_by_xpath(image_finder_xp)[-2]

    # Se crea un tiempo de espera hasta que cargue la imagen
    wait_time_start = time.time()
    while (target.get_attribute("src") == thumbnail_src) and time.time() < wait_time_start + 5:
        time.sleep(0.2)
    thumbnail_src = driver.find_elements_by_xpath(image_finder_xp)[-1].get_attribute("src")
    attribute_value = target.get_attribute("src")
    print(attribute_value)

    # Si la imagen es base64, la informacion que se encuentren en los
    # tag sobre 'src' no seran urls,
    is_b64 = check_if_result_b64(attribute_value)
    if is_b64:
        image_format = is_b64
        content = base64.b64decode(attribute_value.split(';base64')[1])
    else:
        print("you are inside else")
        resp = requests.get(attribute_value, stream=True)
        temp_for_image_extension = BytesIO(resp.content)
        print(temp_for_image_extension.getvalue())
        image = Image.open(temp_for_image_extension)
        image_format = image.format
        content = resp.content
    # Al guardar el archivo se abre el directorio de descargas,
    # enonces con esta funcion cerramos el directorio
    with open(TARGET_SAVE_LOCATION.format(i, image_format), 'wb') as f:
        f.write(content)
    # Cambiamos el path de los html, pues esto se actualizan de tiempo
    # en tiempo en las paginas web de google
    svg_arrows_xpath = '//div[@jscontroller]//a[contains(@jsaction, "click:trigger")]//*[@viewBox="0 0 24 24"]'
    next_arrow = driver.find_elements_by_xpath(svg_arrows_xpath)[-3]
    next_arrow.click()