# -*- coding: utf-8 -*-
"""
parser.py

Парсер HTM-файлов выгрузок из базы данных Integrum.
Извлекает из каждой статьи: источник, дату, заголовок, текст.
Результат сохраняется в corpus.csv.

Зависимости:
    pip install beautifulsoup4 pandas lxml
"""

from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import re
from google.colab import files


def parse_integrum_htm(content):
    soup = BeautifulSoup(content, "html.parser")
    articles = []
    date_pattern = re.compile(r'\d{2}\.\d{2}\.\d{4}')
    anchors = soup.find_all("a", attrs={"name": re.compile(r'^\d+$')})

    for i, anchor in enumerate(anchors):
        try:
            end = anchors[i+1] if i+1 < len(anchors) else None
            siblings = []
            node = anchor.next_sibling
            while node and node != end:
                siblings.append(node)
                node = getattr(node, 'next_sibling', None)
            block = BeautifulSoup(
                "".join(str(s) for s in siblings), "html.parser"
            )

            # Данные
            date = ""
            for td in block.find_all("td", attrs={"bgcolor": "#e4e1d9"}):
                m = date_pattern.search(td.get_text())
                if m:
                    date = m.group()
                    break

            # Источник
            source = ""
            for td in block.find_all("td", attrs={"bgcolor": "#e4e1d9"}):
                td_text = td.get_text(" ").strip()
                if date and date in td_text:
                    raw = td_text.split(";")[0]
                    source = " ".join(raw.split()).strip()
                    break

            # Заголовок
            title = ""
            h3 = block.find("h3")
            if h3:
                title = h3.get_text(separator=" ", strip=True)
                title = " ".join(dict.fromkeys(title.split())).strip()
            else:
                first_td = block.find("td", attrs={"bgcolor": "#e4e1d9"})
                if first_td:
                    candidate = first_td.get_text(strip=True)
                    if not date_pattern.search(candidate) and \
                       ";" not in candidate:
                        title = candidate

            # Текст
            text = ""
            pre = block.find("pre")
            if pre:
                text = pre.get_text(strip=True)
            else:
                paras = block.find_all("p")
                text = " ".join(
                    p.get_text(separator=" ", strip=True)
                    for p in paras
                    if len(p.get_text(strip=True)) > 20
                )

            if not title and not text:
                continue

            articles.append({
                "source": source,
                "date":   date,
                "title":  title,
                "text":   text
            })

        except Exception:
            continue

    return articles


# -Загрузка и обработка файлов
uploaded = files.upload() 

all_articles = []

for filename, content in uploaded.items():
    print(f"Обрабатываю: {filename}...", end=" ")
    try:
        text = content.decode("windows-1251")
    except Exception:
        text = content.decode("utf-8", errors="ignore")

    articles = parse_integrum_htm(text)
    all_articles.extend(articles)
    print(f"{len(articles)} статей")

df = pd.DataFrame(all_articles)
print(f"\nВсего статей: {len(df)}")
print(df.head())

df.to_csv("corpus.csv", index=False, encoding="utf-8-sig")
files.download("corpus.csv")
print("Готово — corpus.csv скачан")
