import streamlit as st
import json
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
import io


st.set_page_config(page_title="Kur'an-ı Kerim Dijital Rehber", page_icon="📖", layout="centered")


st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextbox, .stMarkdown { font-family: 'serif'; }
    .ayet-box {
        background-color: #262730;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)



@st.cache_data
def veriyi_yukle():
    try:
        with open('Diyanet Vakfı.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Hata: 'Diyanet Vakfı.json' dosyası bulunamadı!")
        return None


data = veriyi_yukle()


st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2904/2904843.png", width=100)
st.sidebar.title("Dijital Rehber v1.0")
menu = st.sidebar.radio("Gitmek İstediğiniz Bölüm:",
                        ["🏠 Ana Sayfa", "🔍 Detaylı Arama", "🎭 Ruh Halim", "📚 Sure Kütüphanesi"])



def ayet_gorseli_olustur(ayet_metni, kaynak):
    width, height = 1080, 1080
    img = Image.new('RGB', (width, height), color='#121212')
    draw = ImageDraw.Draw(img)

    # Not: Web sunucularında font yolu değişebilir, standart fonta düşme koruması ekliyoruz
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerif.ttf", 45)
    except:
        font = ImageFont.load_default()

    full_text = f"\"{ayet_metni}\"\n\n— {kaynak}"
    wrapped_text = textwrap.fill(full_text, width=40)

    draw.multiline_text((540, 540), wrapped_text, font=font, fill="#E0E0E0", anchor="mm", align="center")
    img = ImageOps.expand(img, border=20, fill='#4CAF50')

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()



if data:
    if menu == "🏠 Ana Sayfa":
        st.title("📖 Kur'an-ı Kerim Rehberi")
        st.write("Tematik konulara göre ayetleri keşfedin.")

        kategoriler = {
            "İman & Tevhid": ["iman", "allah", "tek", "tevhid", "mümin"],
            "Güzel Ahlak": ["ahlak", "iyilik", "anne", "baba", "akraba", "emanet"],
            "Sabır ve Metanet": ["sabır", "zorluk", "kolaylık", "imtihan"],
            "İbadet ve Dua": ["namaz", "dua", "hac", "oruç", "zikir"],
            "Sosyal Hayat": ["adalet", "ölçü", "tartı", "alışveriş", "barış"]
        }

        secim = st.selectbox("Bir konu seçin:", list(kategoriler.keys()))

        if st.button("Bir Ayet Getir"):
            anahtar = kategoriler[secim]
            havuz = [(s['name'], a[0], a[1]) for s in data['sures'] for a in s['ayetler'] if
                     any(k in a[1].lower() for k in anahtar)]

            if havuz:
                sure, no, metin = random.choice(havuz)
                st.markdown(
                    f"""<div class='ayet-box'><h4>{secim}</h4><p>"{metin}"</p><p style='text-align:right;'><b>{sure} Suresi, {no}. Ayet</b></p></div>""",
                    unsafe_allow_html=True)

                # Görsel İndirme
                img_data = ayet_gorseli_olustur(metin, f"{sure} {no}")
                st.download_button(label="🖼️ Görsel Olarak İndir", data=img_data, file_name="ayet_kartpostal.png",
                                   mime="image/png")

    elif menu == "🎭 Ruh Halim":
        st.title("🎭 Ruh Halinize Göre Rehber")
        ruh_halleri = {
            "Hüzünlü / Üzgün": ["üzülme", "gevşeme", "ferah", "göğüs", "sabret", "müjde"],
            "Kararsız / Şaşkın": ["hidayet", "yol", "doğru", "açık", "aydınlık", "rehber"],
            "Yalnız / Çaresiz": ["yakın", "şah damarı", "beraber", "dost", "vekil", "yardım"],
            "Şükür Dolu": ["nimet", "bolluk", "müjde", "sevinç", "hamd", "şükür"],
            "Öfkeli / Gergin": ["öfke", "affet", "yumuşak", "sabır", "huzur", "sükun"]
        }

        mod = st.select_slider("Şu an nasıl hissediyorsunuz?", options=list(ruh_halleri.keys()))

        if st.button("Bana Bir Ayet Oku"):
            anahtar = ruh_halleri[mod]
            havuz = [(s['name'], a[0], a[1]) for s in data['sures'] for a in s['ayetler'] if
                     any(k in a[1].lower() for k in anahtar)]

            if havuz:
                sure, no, metin = random.choice(havuz)
                st.markdown(
                    f"""<div class='ayet-box' style='border-left-color: #FF4B4B;'><h4>Şu anki haliniz için:</h4><p>"{metin}"</p><p style='text-align:right;'><b>{sure} Suresi, {no}. Ayet</b></p></div>""",
                    unsafe_allow_html=True)

        elif menu == "🔍 Detaylı Arama":
    
            st.title("🔍 Kelime İle Ayet Ara")
            kelime = st.text_input("Aramak istediğiniz kavram (Örn: Adalet, Namaz, Allah):")
        
        if kelime:
            # Tüm sonuçları bul
            sonuclar = [(s['name'], a[0], a[1]) for s in data['sures'] for a in s['ayetler'] if kelime.lower() in a[1].lower()]
            toplam_sonuc = len(sonuclar)
            
            if toplam_sonuc > 0:
                st.write(f"**{toplam_sonuc}** adet sonuç bulundu.")
                
                # --- SAYFALAMA MANTIĞI ---
                sonuc_sayisi_per_page = 15
                toplam_sayfa = (toplam_sonuc // sonuc_sayisi_per_page) + (1 if toplam_sonuc % sonuc_sayisi_per_page > 0 else 0)
                
                # Sayfa seçici (Slider veya Sayı Girişi)
                if toplam_sayfa > 1:
                    current_page = st.number_input(f"Sayfa seç (Toplam {toplam_sayfa})", min_value=1, max_value=toplam_sayfa, step=1)
                else:
                    current_page = 1
                
                # Gösterilecek aralığı belirle
                start_idx = (current_page - 1) * sonuc_sayisi_per_page
                end_idx = start_idx + sonuc_sayisi_per_page
                
                # Sadece o sayfanın sonuçlarını ekrana bas
                for s, n, m in sonuclar[start_idx:end_idx]:
                    with st.expander(f"📖 {s} Suresi, {n}. Ayet"):
                        st.write(m)
                        # Görsel İndirme Butonu (Opsiyonel: Arama sonuçlarına da ekleyebilirsin)
                        # img_data = ayet_gorseli_olustur(m, f"{s} {n}")
                        # st.download_button(label="🖼️ İndir", data=img_data, file_name=f"{s}_{n}.png", key=f"btn_{s}_{n}")
            else:
                st.warning("Eşleşen bir sonuç bulunamadı.")


    elif menu == "📚 Sure Kütüphanesi":
        st.title("📚 Sure Kütüphanesi")
        sure_isimleri = [s['name'].strip() for s in data['sures']]
        secilen_sure_adi = st.selectbox("Okumak istediğiniz sureyi seçin:", sure_isimleri)

        for s in data['sures']:
            if s['name'].strip() == secilen_sure_adi:
                st.subheader(f"{s['name']} Suresi")
                st.info(f"Toplam {len(s['ayetler'])} ayet içerir.")
                for a in s['ayetler']:
                    st.write(f"**[{a[0]}]** {a[1]}")

