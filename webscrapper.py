from bs4 import BeautifulSoup
import re
import requests
import io

#Esta es la pagina inicial. De aqui se van a sacar los links de los autos a analizar.
url = "https://www.encuentra24.com/costa-rica-es/autos-usados?q=number.50"
page = requests.get(url)
#Esto parsea los contenidos con HTML Parsing.
soup = BeautifulSoup(page.content, "html.parser")

#Obtengo una lista de todos las etiquetas <a> del soup.
etiquetasUrls = soup.find_all("a")

#Preparo el match de los URLs que son de vehiculos.
match = "/costa-rica-es/autos-usados/"
foundVehicleLinks = list()
for i in etiquetasUrls:
    #Se extrae el href de los <a>.
    url = i.get("href")
    try:
        #Si tiene el match, es un link a un vehiculo.
        if re.search(match, url):
            foundVehicleLinks.append(url)
    except:
        continue

#Primer elemento es irrelevante
foundVehicleLinks.pop(0)

#Cada link sale 3 veces por alguna razon. Borrar los repetidos.
del foundVehicleLinks[3-1::3]
del foundVehicleLinks[2-1::2]

#Ahora toca sacar la info importante de cada uno de esos links.
for i in foundVehicleLinks:
    url = "https://www.encuentra24.com" + i
    newPage = requests.get(url)
    newSoup = BeautifulSoup(newPage.content, "html.parser")

    relevantInfoTags = newSoup.find_all("span", class_="info-name")
    relevantInfoData = newSoup.find_all("span", class_="info-value")
    productFeatures = newSoup.find_all("ul", class_="product-features")

    print("Infos para " + i)
    #print(relevantInfoTags)
    #print(relevantInfoData)
    #print(productFeatures)

    #Depurar "info-name" - InfoTags
    #Hay que quitar los tags, los : y los ' ' de la info
    cleanTag1 = '<span class="info-name">'
    cleanTag2 = '</span>'
    infoTags = list()
    for i in relevantInfoTags:
        try:
            string = str(i)
            newOne = string.replace(cleanTag1, "")
            newTwo = newOne.replace(cleanTag2, "")

            newThree = newTwo
            if ":" in newTwo:
                newThree = newTwo.replace(":", "")
            if " " in newThree:
                newThree = newThree.replace(" ", "")
            infoTags.append(newThree)
        except:
            continue

    #Ahora hay que depurar "info-value" - InfoData
    #Igual, hay que quitar los tags
    cleanTag1 = '<span class="info-value">'
    cleanTag2 = '</span>'
    infoData = list()
    for i in relevantInfoData:
        try:
            string = str(i)
            newOne = string.replace(cleanTag1, "")
            newTwo = newOne.replace(cleanTag2, "")
            newThree = newTwo
            
            if '<div class="ann-price-reduced">' in newTwo:
                newThree = newTwo.split("<")
                newThree = newThree[0]
            
            infoData.append(newThree)
        except:
            continue

    #Ahora toca depurar el "product-features"
    #Viendo la estructura de productFeatures, el primer elemento siempre es lo que importa.
    #Sin embargo, si no hay product-features, la lista solo tiene un elemento con informacion de acomodar cosas.
    carFeatures = list()
    if len(productFeatures) == 1:
        carFeatures = []
    else:
        relevantString = str(productFeatures[0])
        cleanTag1 = '<ul class="product-features">'
        cleanTag2 = '</ul>'
        firstOne = relevantString.replace(cleanTag1, "")
        secondOne = firstOne.replace(cleanTag2, "")

        features = secondOne.split("</li>")
        features.remove("\n")
        for i in features:
            finalString = i
            if "\n<li> " in i:
                finalString = i.replace("\n<li> ", "")
            elif "\n<li>" in i:
                finalString = i.replace("\n<li>", "")
                
            carFeatures.append(finalString)

    #La informacion relevante esta lista. Ahora a guardarlo en un archivo de texto.
    file = io.open("dataSet.txt", "a+", encoding="utf-8")
    file.write("URL: " + url + "\n")
    for i in range(0, len(infoTags)):
        file.write(infoTags[i] + ": " + infoData[i] + "\n");
    file.write("Product Features: \n")
    for i in carFeatures:
        file.write(i + "\n")
    file.write("\n")
    file.write("\n")
    file.close()
