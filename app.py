import streamlit as st
import numpy as np
import requests
from io import BytesIO
from PIL import Image, ImageDraw
from scipy.ndimage import label, find_objects
from streamlit_image_coordinates import image_coordinates

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

# Ищем жёлтые области
hsv = np.array(main_img.convert("HSV"))
mask = (
    (hsv[:, :, 0] >= 20) & (hsv[:, :, 0] <= 35) &
    (hsv[:, :, 1] >= 100) & (hsv[:, :, 2] >= 100)
)

# Находим bounding boxes
def find_boxes(mask):
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
gift_items = []
for url in gift_images:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            gift_items.append(img)
        else:
            gift_items.append(None)
    except Exception:
        gift_items.append(None)

# Состояние
if "opened" not in st.session_state:
    st.session_state.opened = [False] * len(gifts)

# Копия изображения для рисования
canvas = main_img.copy()
draw = ImageDraw.Draw(canvas)

# Вставка подарков
for i, (x, y, w, h) in enumerate(gifts):
    if st.session_state.opened[i] and gift_items[i] is not None:
        item = gift_items[i].resize((w, h))
        canvas.paste(item, (x, y), item)
        draw.rectangle([x, y, x+w, y+h], outline="red", width=3)
    elif st.session_state.opened[i]:
        draw.rectangle([x, y, x+w, y+h], outline="gray", width=3)
        draw.text((x+5, y+5), "❌ Нет подарка", fill="black")
    else:
        draw.rectangle([x, y, x+w, y+h], outline="green", width=3)

# Показываем изображение и отслеживаем клик
coords = image_coordinates(canvas, key="giftmap")
if coords is not None:
    click_x, click_y = coords["x"], coords["y"]
    for i, (x, y, w, h) in enumerate(gifts):
        if x <= click_x <= x + w and y <= click_y <= y + h:
            st.session_state.opened[i] = True
            st.experimental_rerun()
