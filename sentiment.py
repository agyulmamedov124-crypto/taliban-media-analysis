# -*- coding: utf-8 -*-
"""
sentiment.py

Тональный анализ корпуса публикаций о движении «Талибан».
Использует трансформерную модель rubert-base-cased-sentiment,
обученную на русскоязычных текстах.
Результат сохраняется в corpus_sentiment.csv.

Зависимости:
    pip install transformers torch pandas tqdm
"""

import subprocess
subprocess.run(["pip", "install", "transformers", "torch", "-q"])

from transformers import pipeline
from tqdm import tqdm
import pandas as pd
from google.colab import files


# Загрузка модели
sentiment_model = pipeline(
    "text-classification",
    model="blanchefort/rubert-base-cased-sentiment",
    device=-1  # CPU; для GPU замените на device=0
)
print("Модель загружена")


def get_sentiment(text):
    if not isinstance(text, str) or len(text.strip()) < 10:
        return "нейтральная"
    try:
        result = sentiment_model(
            str(text)[:512],
            truncation=True,
            max_length=512
        )[0]
        label = result["label"]
        if label == "POSITIVE":
            return "позитивная"
        elif label == "NEGATIVE":
            return "негативная"
        else:
            return "нейтральная"
    except Exception:
        return "нейтральная"


# Загрузка корпуса
uploaded = files.upload()
df = pd.read_csv("corpus.csv")
print(f"Статей: {len(df)}")

# Тональный анализ
tqdm.pandas()
df["sentiment"] = df["text"].progress_apply(get_sentiment)

print("\nРаспределение тональности:")
print(df["sentiment"].value_counts())
print("\nПо изданиям:")
print(df.groupby("source")["sentiment"].value_counts())

# Сохранение файла
df.to_csv("corpus_sentiment.csv", index=False, encoding="utf-8-sig")
files.download("corpus_sentiment.csv")
print("Сохранено")
