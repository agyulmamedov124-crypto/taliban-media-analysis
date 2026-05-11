# -*- coding: utf-8 -*-
"""
nominations.py
--------------
Частотный анализ номинаций движения «Талибан» в корпусе публикаций.
Подсчитывает частоту ключевых лексем в доталибанский и постталибанский
периоды (до и после 15 августа 2021 года).
Результат сохраняется в corpus_full.csv.

Использование (Google Colab):
    Запустите скрипт и загрузите corpus_sentiment.csv через диалоговое окно.

Зависимости:
    pip install pandas
"""

import pandas as pd
import re
from collections import Counter
from google.colab import files


# --- ЗАГРУЗКА КОРПУСА ---
uploaded = files.upload()
df = pd.read_csv("corpus_sentiment.csv")
df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
df['period'] = df['date'].apply(
    lambda d: 'до авг.2021'
    if pd.notna(d) and d < pd.Timestamp('2021-08-15')
    else 'после авг.2021'
)
print(f"Загружено: {len(df)} статей")


# --- СЛОВАРЬ НОМИНАЦИЙ ---
NOMINATIONS = {
    "Талибан":                  r'\bТалибан\b',
    "талибы/талиб":             r'\bталиб[аыуов]*\b',
    "боевики":                  r'\bбоевик[аиов]*\b',
    "террористы":               r'\bтеррорист[аыов]*\b',
    "афганские власти":         r'афганск\w* власт\w+',
    "новые афганские власти":   r'нов\w* афганск\w* власт\w+',
    "движение Талибан":         r'движени\w+ .{0,10}[Тт]алибан',
    "де-факто правительство":   r'де.факто.{0,15}правительств\w*',
    "переходное правительство": r'переходн\w+ правительств\w*',
    "запрещённая организация":  r'запрещ\w+ \w*организаци\w*',
}


def count_nominations(text):
    if not isinstance(text, str):
        return {k: 0 for k in NOMINATIONS}
    return {
        k: len(re.findall(v, text, flags=re.IGNORECASE))
        for k, v in NOMINATIONS.items()
    }


# --- ПОДСЧЁТ ---
nom_df = df["text"].apply(count_nominations).apply(pd.Series)
df = pd.concat([df, nom_df], axis=1)

nom_cols = list(NOMINATIONS.keys())
pre  = df[df['period'] == 'до авг.2021']
post = df[df['period'] == 'после авг.2021']

print("=== Частота номинаций по всему корпусу ===")
print(df[nom_cols].sum().sort_values(ascending=False).to_string())

print("\n=== До августа 2021 ===")
print(pre[nom_cols].sum().sort_values(ascending=False).to_string())

print("\n=== После августа 2021 ===")
print(post[nom_cols].sum().sort_values(ascending=False).to_string())

pre_count  = len(pre)
post_count = len(post)
print(f"\nСтатей до авг.2021: {pre_count}")
print(f"Статей после авг.2021: {post_count}")

print("\n=== Номинации на 100 статей ===")
norm = pd.DataFrame({
    'до авг.2021':    (pre[nom_cols].sum() / pre_count * 100).round(1),
    'после авг.2021': (post[nom_cols].sum() / post_count * 100).round(1),
})
norm['изменение'] = (norm['после авг.2021'] - norm['до авг.2021']).round(1)
print(norm.sort_values('до авг.2021', ascending=False).to_string())

print("\n=== Номинации по изданиям ===")
print(df.groupby("source")[nom_cols].sum().to_string())

# --- СОХРАНЕНИЕ ---
df.to_csv("corpus_full.csv", index=False, encoding="utf-8-sig")
files.download("corpus_full.csv")
