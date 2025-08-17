import streamlit as st
import numpy as np
import requests
from io import BytesIO
from PIL import Image, ImageDraw

st.set_page_config(layout="wide")
st.title("🎁 Открой свой подарок!")

# Ссылки на изображения
main_image_url = "https://quickimagetools.com/uploads/image_68a1212295ed12.74319359.jpg"
gift_images = [
    "https://quickimagetools.com/uploads/image_68a0f2056d96d0.56792069.jpg",
    "https://quickimagetools.com/uploads/image_68a0f21b7a7f12.50304972.jpg",
    "https://quickimagetools.com/uploads/image_68a0f272462c37.02957994.jpg",
    "https://quickimagetools.com/uploads/image_68a0f28a1a4fa6.73539447.jpg"
]

# Загружаем основное изображение
response = requests.get(main_image_url)
main_img = Image.open(BytesIO(response.content)).convert("RGB")
main_np = np.array(main_img)

# Ищем жёлтые области
hsv = np.array(main_img.convert("HSV"))
mask = (
    (hsv[:, :, 0] >= 20) & (hsv[:, :, 0] <= 35) &
    (hsv[:, :, 1] >= 100) & (hsv[:, :, 2] >= 100)
)

# Находим bounding boxes вручную
def find_boxes(mask):
    from scipy.ndimage import label, find_objects
    labeled, _ = label(mask)
    slices = find_objects(labeled)
    boxes = []
    for s in slices:
        y1, y2 = s[0].start, s[0].stop
        x1, x2 = s[1].start, s[1].stop
        w, h = x2 - x1, y2 - y1
        if w > 50 and h > 50:
            boxes.append((x1, y1, w, h))
    return boxes

gifts = find_boxes(mask)

# Загружаем изображения подарков
gift_items = [Image.open(BytesIO(requests.get(url).content)) for url in gift_images]

# Состояние
if "opened" not in st.session_state:
    st.session_state.opened = [False] * len(gifts)

# Копия изображения для рисования
canvas = main_img.copy()
draw = ImageDraw.Draw(canvas)

# Обработка открытия
for i, (x, y, w, h) in enumerate(gifts):
    if st.session_state.opened[i]:
        item = gift_items[i].resize((w, h))
        canvas.paste(item, (x, y))
        draw.rectangle([x, y, x+w, y+h], outline="red", width=3)
    else:
        draw.rectangle([x, y, x+w, y+h], outline="green", width=3)

# Кнопки
cols = st.columns(len(gifts))
for i, col in enumerate(cols):
    with col:
        if not st.session_state.opened[i]:
            if st.button(f"Открыть 🎁 #{i+1}"):
                st.session_state.opened[i] = True
                st.experimental_rerun()

# Показываем результат
st.image(canvas, caption="Ваши подарки")
