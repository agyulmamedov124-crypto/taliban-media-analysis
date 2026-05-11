# -*- coding: utf-8 -*-
"""
frames.py
---------
Автоматическая классификация публикаций корпуса по пяти фреймам
репрезентации движения «Талибан». Публикации с неоднозначной
классификацией помечаются для последующей ручной верификации.
Результат сохраняется в corpus_frames.csv.

Система фреймов (по Энтману, 1993):
    1. Угроза безопасности
    2. Политический актор
    3. Гуманитарный кризис
    4. Региональный стабилизатор
    5. Исторический контекст

Использование (Google Colab):
    Запустите скрипт и загрузите corpus_full.csv через диалоговое окно.

Зависимости:
    pip install pandas
"""

import pandas as pd
import re
from google.colab import files


# --- ЗАГРУЗКА КОРПУСА ---
uploaded = files.upload()
df = pd.read_csv("corpus_full.csv")
df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
df['period'] = df['date'].apply(
    lambda d: 'до авг.2021'
    if pd.notna(d) and d < pd.Timestamp('2021-08-15')
    else 'после авг.2021'
)


# --- СЛОВАРИ КЛЮЧЕВЫХ СЛОВ ПО ФРЕЙМАМ ---
FRAMES = {
    "угроза безопасности": [
        "террор", "угроз", "атак", "боевик", "взрыв", "жертв",
        "захват", "нестабильност", "радикал", "экстремизм",
        "ИГИЛ", "ИГ ", "насилие", "убийств", "смерт"
    ],
    "политический актор": [
        "переговор", "встреч", "соглашени", "признани", "дипломат",
        "МИД", "посольств", "делегаци", "официальн", "правительств",
        "министр", "договор", "заявил министр", "афганские власти",
        "талибан заявил", "талибы заявил"
    ],
    "гуманитарный кризис": [
        "беженц", "гуманитарн", "голод", "женщин", "школ", "детей",
        "помощь", "ООН", "ЮНИСЕФ", "права человека", "эвакуаци",
        "вынужденн", "кризис", "нищет"
    ],
    "региональный стабилизатор": [
        "стабильност", "Центральная Азия", "ИГ Хорасан",
        "ИГИЛ-Хорасан", "Хорасан", "противодейств террор",
        "региональн", "партнер", "сотрудничеств", "безопасност региона"
    ],
    "исторический контекст": [
        "вывод войск", "США вывел", "оккупаци", "советск",
        "провал", "поражени", "двадцать лет", "20 лет",
        "западн", "американск", "операци США", "2001"
    ]
}


def detect_frame(text, title=""):
    if not isinstance(text, str):
        text = ""
    full = (str(title) + " " + text).lower()
    scores = {
        frame: sum(1 for kw in keywords if kw.lower() in full)
        for frame, keywords in FRAMES.items()
    }
    best = max(scores, key=scores.get)
    best_score = scores[best]
    if best_score == 0:
        return "угроза безопасности"  # дефолт при отсутствии маркеров
    top_scores = sorted(scores.values(), reverse=True)
    if top_scores[0] == top_scores[1]:
        return "смешанный / требует проверки"
    return best


# --- КЛАССИФИКАЦИЯ ---
df["frame"] = df.apply(
    lambda row: detect_frame(row.get("text", ""), row.get("title", "")),
    axis=1
)

print("=== Распределение фреймов ===")
print(df["frame"].value_counts())
print()
print("=== По периодам ===")
print(df.groupby("period")["frame"].value_counts())
print()
print("=== По изданиям ===")
print(df.groupby("source")["frame"].value_counts())

# --- СОХРАНЕНИЕ ---
df.to_csv("corpus_frames.csv", index=False, encoding="utf-8-sig")
files.download("corpus_frames.csv")
print("Сохранено")
