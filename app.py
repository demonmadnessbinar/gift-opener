import streamlit as st
import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(layout="wide")
st.title("🎁 Открой свой подарок!")

# Загружаем основное изображение
main_image_url = "https://quickimagetools.com/uploads/image_68a1212295ed12.74319359.jpg"
response = requests.get(main_image_url)
img = Image.open(BytesIO(response.content))
img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

# Ищем жёлтые подарки
hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([35, 255, 255])
mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Загружаем изображения вещей
gift_images = [
    "https://quickimagetools.com/uploads/image_68a0f2056d96d0.56792069.jpg",
    "https://quickimagetools.com/uploads/image_68a0f21b7a7f12.50304972.jpg",
    "https://quickimagetools.com/uploads/image_68a0f272462c37.02957994.jpg",
    "https://quickimagetools.com/uploads/image_68a0f28a1a4fa6.73539447.jpg"
]
gift_items = [Image.open(BytesIO(requests.get(url).content)) for url in gift_images]

# Сохраняем координаты подарков
gifts = []
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if w > 50 and h > 50:
        gifts.append((x, y, w, h))
        cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Состояние открытых подарков
if "opened" not in st.session_state:
    st.session_state.opened = [False] * len(gifts)

# Кнопки для открытия
for i, (x, y, w, h) in enumerate(gifts):
    col = st.columns(len(gifts))[i]
    with col:
        if not st.session_state.opened[i]:
            if st.button(f"Открыть 🎁 #{i+1}"):
                st.session_state.opened[i] = True
                item_resized = gift_items[i].resize((w, h))
                item_cv = cv2.cvtColor(np.array(item_resized), cv2.COLOR_RGB2BGR)
                img_cv[y:y+h, x:x+w] = item_cv
                cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 0, 255), 2)

# Показываем изображение
st.image(img_cv, channels="BGR", caption="Ваши подарки")
