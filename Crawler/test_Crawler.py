from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import json



def main():

    driver = webdriver.Firefox()

    driver.get("https://www.potterpedia.it/?speciale=elenco&categoria=Pozioni")
    WebDriverWait(driver, timeout=1)


    div = driver.find_element(By.ID, "mainContainer")
    potions = [d.get_attribute("href") for d in div.find_elements(By.TAG_NAME, "a")]
    potions = potions[:-4]


    potions_info = list()
    
    for e in potions:
        driver.get(e)
        potion = list()
        WebDriverWait(driver, timeout=1)
        div_table = driver.find_element(By.ID, "mainContainer")
        potion.append(div_table.find_element(By.TAG_NAME, "h3").text)
        rows = div_table.find_elements(By.XPATH, "//table//tr")
        for row in rows[2:]:
            try:
                potion.append(row.find_element(By.XPATH, ".//td[2]").text)
            except Exception as ex:
                print(ex)
                potion.append('')
        potions_info.append(potion)
    
    
    driver.quit()

    df = pd.DataFrame(potions_info)
    df.to_string()
    df = df.to_json(r'../Data/Potions.json')
    
if __name__ == "__main__":
    main()