#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom  # <-- ДОБАВЛЕНО ДЛЯ ФОРМАТИРОВАНИЯ
from datetime import datetime
import requests
import os


class CountriesParser:
    """
    Класс для получения данных о странах из REST Countries API
    и сохранения в JSON и XML.
    """

    API_URL = "https://restcountries.com/v3.1/name/"

    COUNTRIES = [
        "russia", "usa", "germany", "france", "japan",
        "brazil", "india", "australia", "canada", "egypt"
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; CountriesParser/1.0)'
        })
        self.timeout = 10

    def fetch_country(self, country_name):
        """Получает данные о стране по названию"""
        try:
            url = self.API_URL + country_name
            print(f"[INFO] Запрос: {url}")

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            if not data:
                print(f"[WARN] Нет данных для {country_name}")
                return None

            country = data[0]

            name = country.get('name', {}).get('common', 'N/A')
            capital = country.get('capital', ['N/A'])[0]
            population = country.get('population', 0)
            area = country.get('area', 0)

            currencies = country.get('currencies', {})
            currency_info = list(currencies.values())[0] if currencies else {}
            currency = f"{currency_info.get('name', 'N/A')} ({currency_info.get('symbol', '')})"

            print(f"[SUCCESS] {name} — данные получены")

            return {
                "name": name,
                "capital": capital,
                "population": population,
                "area_km2": area,
                "currency": currency,
                "timestamp": datetime.now().isoformat()
            }

        except requests.exceptions.Timeout:
            print(f"[ERROR] Тайм-аут для {country_name}")
        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] HTTP ошибка для {country_name}: {e}")
        except Exception as e:
            print(f"[ERROR] Ошибка для {country_name}: {e}")

        return None

    def collect_all(self):
        """Собирает данные по всем странам"""
        result = []
        for country in self.COUNTRIES:
            data = self.fetch_country(country)
            if data:
                result.append(data)
            else:
                print(f"[WARN] Страна {country} пропущена")
        return result

    def save_to_json(self, data, filename="countries_data.json"):
        """Сохраняет данные в JSON"""
        output = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_countries": len(data),
                "source": "REST Countries API"
            },
            "countries": data
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        file_size = os.path.getsize(filename)
        print(f"[SUCCESS] JSON сохранён: {filename} ({file_size} байт)")

    def save_to_xml(self, data, filename="countries_data.xml"):
        """Сохраняет данные в XML с форматированием"""
        root = ET.Element("CountriesData")

        meta = ET.SubElement(root, "Metadata")
        ET.SubElement(meta, "GeneratedAt").text = datetime.now().isoformat()
        ET.SubElement(meta, "TotalCountries").text = str(len(data))
        ET.SubElement(meta, "Source").text = "REST Countries API"

        countries_elem = ET.SubElement(root, "Countries")

        for country in data:
            c = ET.SubElement(countries_elem, "Country")
            ET.SubElement(c, "name").text = country["name"]
            ET.SubElement(c, "capital").text = country["capital"]
            ET.SubElement(c, "population").text = str(country["population"])
            ET.SubElement(c, "area_km2").text = str(country["area_km2"])
            ET.SubElement(c, "currency").text = country["currency"]
            ET.SubElement(c, "timestamp").text = country["timestamp"]

        # Форматируем XML с отступами
        rough_string = ET.tostring(root, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

        file_size = os.path.getsize(filename)
        print(f"[SUCCESS] XML сохранён: {filename} ({file_size} байт)")


def main():
    print("=" * 70)
    print("НАЧАЛО СБОРА ДАННЫХ (вариант 3 — REST Countries API)")
    print("=" * 70)

    parser = CountriesParser()
    data = parser.collect_all()

    print("\n" + "=" * 70)
    print(f"СБОР ЗАВЕРШЁН: обработано {len(data)} из {len(parser.COUNTRIES)} стран")
    print("=" * 70)

    if data:
        parser.save_to_json(data)
        parser.save_to_xml(data)

        print("\n[Пример данных (первая страна)]:")
        for k, v in data[0].items():
            print(f"  {k}: {v}")
    else:
        print("[ERROR] Нет данных для сохранения")


if __name__ == "__main__":
    main()