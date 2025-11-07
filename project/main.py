import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scraping():
    # Посилання на веб-сторінки
    urls = [
        'https://detector.media/type/4/pagenum/1/',
        'https://detector.media/type/4/pagenum/2/',
        'https://detector.media/type/4/pagenum/3/',
        'https://detector.media/type/4/pagenum/4/',
        'https://detector.media/type/4/pagenum/5/',
    ]

    classes_to_search = ['cat_blkPostDate global_pdate',
                         'cat_blkPostCnt global_pcnt',
                         'cat_blkPostAuthor liman_1 global_authors lima_end',
                         'cat_blkPostTitle global_ptitle']
    column_names = ['Дата', 'Читачі', 'Автор', 'Назва']
    # Створюємо порожні  для зберігання даних кожного класу
    class_data = {class_name: [] for class_name in classes_to_search}

    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for class_name in classes_to_search:
                elements = soup.find_all(class_=class_name)
                class_data[class_name].extend([element.text for element in elements])
        else:
            print('Error:', response.status_code)
        time.sleep(1)  # Затримка 1 секунда між запитами

    # Створюємо DataFrame для кожного класу з відповідними назвами стовпців
    dfs = {class_name: pd.DataFrame({column_names: class_data[class_name]}) for class_name, column_names in
           zip(class_data, column_names)}

    # Об'єднуємо всі DataFrame в один за допомогою стовпців
    df = pd.concat(dfs, axis=1)

    # Зберігаємо DataFrame у файл Excel
    df.to_excel('data.xlsx')

scraping()

