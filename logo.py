from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pdf2image import convert_from_path
import os

def add_text_to_certificate_template(input_pdf, user_text):
    # Giriş PDF'sini kontrol et
    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"Giriş PDF bulunamadı: {input_pdf}")

    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()

    # İlk sayfayı al
    page = pdf_reader.pages[0]

    # Sayfa boyutlarını al (yatay ortalamak için)
    page_width = float(page.mediabox.width)
    x_center = page_width / 2  # Yatay orta nokta

    # Katman için BytesIO tamponu oluştur
    packet = BytesIO()
    canvas_obj = canvas.Canvas(packet)

    # Font dosyasını kontrol et
    custom_font_path = "Museo900.ttf"  # Doğru .ttf dosyasını kullan
    if not os.path.exists(custom_font_path):
        raise FileNotFoundError(f"Font dosyası bulunamadı: {custom_font_path}")

    # Museo900 fontunu kaydet
    try:
        pdfmetrics.registerFont(TTFont('Museo900', custom_font_path))
    except Exception as e:
        print(f"Font kaydedilirken hata: {e}")
        raise

    # Font ve boyut ayarla
    font_name = "Museo900"
    font_size = 41
    canvas_obj.setFont(font_name, font_size)

    # Metin rengini HEX #00B6C5 olarak ayarla
    canvas_obj.setFillColor(HexColor('#00B6C5'))

    # Metni yatayda ortala ve logonun altına yerleştir (y koordinatını ayarlayın)
    y_position = 500  # Logonun altına yerleştirmek için, gerektiğinde ayarlayın
    canvas_obj.drawCentredString(x_center, y_position, user_text)

    # Arka planın şeffaf olduğundan emin ol (varsayılan olarak şeffaf)
    canvas_obj.save()
    packet.seek(0)

    # Katmanı sertifikayla birleştir
    overlay_reader = PdfReader(packet)
    overlay_page = overlay_reader.pages[0]
    page.merge_page(overlay_page)
    pdf_writer.add_page(page)

    # Değiştirilmemiş diğer sayfaları ekle
    for page in pdf_reader.pages[1:]:
        pdf_writer.add_page(page)

    # Çıktı dosya adını oluştur
    output_pdf = f"logo_{user_text}.pdf"

    # Son çıktıyı PDF olarak kaydet
    with open(output_pdf, 'wb') as output_file:
        pdf_writer.write(output_file)

    print(f"PDF '{output_pdf}' olarak kaydedildi!")

    # PDF'yi PNG'ye dönüştür
    try:
        # Poppler yolunu belirtin (kendi poppler\bin yolunuzu güncelleyin)
        poppler_path = r"C:\Program Files (x86)\poppler-25.07.0\Library\bin"  # Örnek yol, kendi yolunuzu güncelleyin
        images = convert_from_path(output_pdf, poppler_path=poppler_path, fmt="png", transparent=True)

        # PNG dosyasını kaydet
        output_png = f"logo_{user_text}.png"
        images[0].save(output_png, "PNG")
        print(f"PNG '{output_png}' olarak kaydedildi!")
    except Exception as e:
        print(f"PNG dönüştürme hatası: {e}")

if __name__ == "__main__":
    try:
        # Kullanıcıdan metin girişi al
        user_input = input("Lütfen sertifikaya eklenecek metni girin: ").strip()
        if not user_input:
            raise ValueError("Metin girişi boş olamaz!")
        # Dosya adına uygun hale getirmek için özel karakterleri temizle
        user_input_clean = "".join(c for c in user_input if c.isalnum() or c in (' ', '_')).strip()
        if not user_input_clean:
            raise ValueError("Geçerli bir dosya adı oluşturulamadı!")
        # Girilen metni kullanarak PDF ve PNG oluştur
        add_text_to_certificate_template("logo.pdf", user_input_clean)
    except Exception as e:
        print(f"Hata: {e}")