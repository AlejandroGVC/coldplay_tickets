import pandas as pd
import requests
import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date

#parametros
grupo = 'coldplay'
ciudad = 'paris'
dia = 17
sitios = 'pista'

def get_html(url):
	'''
	Devuelve el contenido del html en un objeto beaufitul soup
	'''
	page = requests.get(url)
	return BeautifulSoup(page.content, 'html.parser')

def milanuncios(grupo, ciudad, dia, sitios):
    '''
    Extrae de la pagina de mil anuncios informacion
    de un concierto en una ciudad y dia concretos y 
    devuelve un csv
    '''
    url = 'https://www.milanuncios.com/entradas-de-concierto/?s='+ str(grupo) + '%20' + str(ciudad) + '%20' + str(dia) + '%20' + str(sitios)
    anuncios = get_html(url).find_all('div', {'class':'ma-AdCard-detail'})
    ls_titulos, ls_precios, ls_descrip  = [], [], []
    for anuncio in anuncios:
        ls_titulos.append(anuncio.find('h2').text)
        ls_precios.append(anuncio.find('div', {'class':'ma-AdMultiplePrice'}).text)
        ls_descrip.append(anuncio.find('p', {'class':'ma-AdCardDescription-text'}).text)
    dictionary = {'titulo':ls_titulos, 
                  'descripcion':ls_descrip, 
                  'precio':ls_precios,
                  'dia':date.today()} 
    data = pd.DataFrame.from_dict(dictionary)
    n = len(data.loc[:,'titulo']) 
    for i in range(0, n):
        if 'coldplay' not in data.loc[i,'titulo'].lower():
            data.drop(i, inplace = True)
    return data.to_csv(index = False, path_or_buf = 'data/milanuncios.csv', mode = 'a', header = False) 

def viagogo(grupo, ciudad, dia):
    '''
    Extrae de la pagina de viagogo informacion
    de un concierto en una ciudad y dia concretos y 
    devuelve un csv
    '''
    #selenium
    driver = webdriver.Safari()
    driver.get('https://www.viagogo.es')
    search = driver.find_element_by_xpath('//*[@id="search"]')
    separator = ' '
    info = [str(grupo), str(ciudad), str(dia)]
    search.send_keys(separator.join(info))
    # espera a cargar y escoge el elemento que sale
    # aqui podria equivocarse y coger otro concierto ? 
    event = WebDriverWait(driver, 4)\
        .until(EC.element_to_be_clickable((By.XPATH, '//*[@id="searchResults"]/div[3]/div/a')))
    event.click()
    slct_qnty = WebDriverWait(driver, 20)\
        .until(EC.element_to_be_clickable((By.XPATH, '//*[@id="qtySelectionModalContent"]/div/div[1]/div[2]/div[1]')))
    slct_qnty.click()
    options = driver.find_elements_by_class_name('dropdown__row')
    for option in options:
        if '2 entradas' in option.text:
            if '12' not in option.text: # si hay 22, 32, 42... no funciona 
                option.click()

    continue_ = driver.find_element_by_xpath('//*[@id="qtySelectionModalContent"]/div/button')
    continue_.click()
    pista = WebDriverWait(driver, 50)\
        .until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Pista"]')))
    pista.click()
    entrada = WebDriverWait(driver, 20)\
        .until(EC.element_to_be_clickable((By.XPATH, '//*[@id="clientgridtable"]/div[2]/div/div[1]/div[3]/div[1]/div[2]/a')))
    html = driver.page_source  
    driver.close()
    # BS 
    tablon = BeautifulSoup(html, 'html.parser').find('div', {'class':'f-list'}).find_all('div', {'class':'p0'})
    ls_precio = []
    ls_dia = []
    ls_seccion = []
    for anuncio in tablon:
        ls_seccion.append(anuncio.find('span', {'class':'v-title-sml'}).text.strip())
        ls_precio.append(anuncio.find('span', {'class':'t-b'}).text.strip())
        ls_dia.append(date.today())
    dictionary = {'precio':ls_precio, 
                  'seccion':ls_seccion,
                  'dia':ls_dia} 
    data = pd.DataFrame.from_dict(dictionary)
    return data.to_csv(index = False, path_or_buf = 'data/viagogo.csv', mode = 'a', header = False) 

if __name__=='__main__':
    viagogo(grupo=grupo, ciudad=ciudad, dia=dia)
    milanuncios(grupo=grupo, ciudad=ciudad, dia=dia, sitios=sitios)
  

