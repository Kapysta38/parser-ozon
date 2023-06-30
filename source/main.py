import json
import logging
import traceback

from client import Client


file_log = logging.FileHandler('log_client.log', encoding='utf-8')
logging.basicConfig(handlers=(file_log,),
                    format='[%(asctime)s | %(levelname)s | %(name)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

log = logging.getLogger("parser")

api_url = "https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2?url={}/?layout_container=pdpPage2column&layout_page_index=2"


def parse_elem(data, photo, price):
    characteristics = {'price': price, 'photo': photo}
    name = data['productTitle'].replace('Характеристики:', '').strip()
    data = data['characteristics']
    for characteristic in data:
        for elem in characteristic['short']:
            if 'OZON' not in elem['name']:
                characteristics[elem['name']] = elem['values'][0]['text']
    return name, characteristics


def parse_json(data, price):
    data = json.loads(data)
    photo = list(filter(lambda x: '.jpg' in x['content'], data['seo']['meta']))[0]['content']
    data = data['widgetStates']
    for widget_name, widget_value in data.items():
        if 'webCharacteristics' in widget_name:
            elem = json.loads(widget_value)
            return parse_elem(elem, photo, price)


def parse_urls(urls, client):
    result = {}
    for data, name in urls:
        result_category = {}
        print(f"Парсинг категории '{name}'")
        category_urls, category_price = data
        for i, url in enumerate(category_urls):
            print(f'Парсинг товара {i + 1}/{len(category_urls)}')
            url = url.split("/?")[0].replace("https://www.ozon.ru", '')
            data = client.get_data(api_url.format(url))
            product_name, characteristics = parse_json(data, category_price[i])
            result_category[product_name] = characteristics

        result[name] = result_category
    return result


def save_result(result):
    with open('data.json', 'w', encoding='utf-8') as fp:
        json.dump(result, fp, ensure_ascii=False)


def main():
    try:
        print('Начало работы парсера')
        client = Client()

        urls = client.get_urls()

        result = parse_urls(urls, client)

        client.quit()

        save_result(result)
        print('Парсер успешно завершил работу')
    except Exception as ex:
        print('Произошла ошибка, необходимо посмотреть файл log_client.log')
        log.error({'error': ex, 'traceback': traceback.format_exc()})


if __name__ == '__main__':
    main()
    input('\n\nДля выхода нажмите любую клавишу: ')
