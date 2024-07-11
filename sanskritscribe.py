import streamlit as st
import sqlite3
import easyocr
from googletrans import Translator
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import tempfile 
import os
from PIL import Image
import textwrap
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

st.set_page_config(layout="wide")

def set_jpg_as_page_bg(jpg_file):
    bin_str = get_base64_of_bin_file(jpg_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/jpeg;base64,%s");
        background-size:100%% 100%%;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Calling  the function with JPEG file path( background)
set_jpg_as_page_bg(r"C:\Users\Dell\Desktop\bg1.jpg")

# CSS styling for highlighting text
highlight_css = """
<style>
.big-text {
    font-size: 24px;
    padding: 16px;
    margin-bottom: 10px;
}

.highlight {
    background-color: #58210F;
    color: white;
}
</style>
"""

# Inject CSS into Streamlit
st.markdown(highlight_css, unsafe_allow_html=True)

# Constants
LANGUAGES = {
    "English": "en",
    "Chinese (Simplified)": "zh-cn",
    "Chinese (Traditional)": "zh-tw",
    "Spanish": "es",
    "French": "fr",
    "Arabic": "ar",
    "Russian": "ru",
    "Hindi": "hi",
    "Bengali": "bn",
    "Portuguese": "pt",
    "Urdu": "ur",
    "Indonesian": "id",
    "German": "de",
    "Japanese": "ja",
    "Swahili": "sw",
    "Telugu": "te",
    "Marathi": "mr",
    "Turkish": "tr",
    "Tamil": "ta",
    "Vietnamese": "vi",
    "Korean": "ko",
    "Italian": "it",
    "Yoruba": "yo",
    "Thai": "th",
    "Gujarati": "gu",
    "Filipino": "fil",
    "Punjabi": "pa",
    "Ukrainian": "uk",
    "Burmese": "my",
    "Malayalam": "ml",
    "Kannada": "kn",
    "Odia": "or",
    "Sindhi": "sd",
    "Amharic": "am",
    "Nepali": "ne",
    "Dutch": "nl",
    "Hausa": "ha",
    "Kurdish": "ku",
    "Sinhala": "si",
    "Finnish": "fi",
    "Romanian": "ro",
    "Bulgarian": "bg",
    "Czech": "cs",
    "Hungarian": "hu",
    "Swedish": "sv",
    "Greek": "el",
    "Danish": "da",
    "Norwegian": "no",
    "Hebrew": "he",
    "Polish": "pl",
    "Persian": "fa",
    "Serbian": "sr",
    "Malay": "ms",
    "Croatian": "hr",
    "Lithuanian": "lt",
    "Latvian": "lv",
    "Estonian": "et",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Albanian": "sq",
    "Macedonian": "mk",
    "Belarusian": "be",
    "Uzbek": "uz",
    "Azerbaijani": "az",
    "Kazakh": "kk",
    "Georgian": "ka",
    "Kyrgyz": "ky",
    "Tajik": "tg",
    "Tatar": "tt",
    "Armenian": "hy",
    "Bosnian": "bs",
    "Montenegrin": "srp",
    "Catalan": "ca",
    "Luxembourgish": "lb",
    "Khmer": "km",
    "Lao": "lo",
    "Dari": "prs",
    "Pashto": "ps",
    "Somali": "so",
    "Chichewa": "ny",
    "Zulu": "zu",
    "Xhosa": "xh",
    "Afrikaans": "af",
    "Setswana": "tn",
    "Yiddish": "yi",
    "Fijian": "fj",
    "Tongan": "to",
    "Samoan": "sm",
    "Hawaiian": "haw",
    "Kinyarwanda": "rw",
    "Kirundi": "rn",
    "Shona": "sn",
    "Tigrinya": "ti",
    "Krio": "kri",
    "Pidgin English": "pcm",
    "Hmong": "hmn",
    "Malagasy": "mg",
    "Ewe": "ee",
    "Akan": "ak",
    "Wolof": "wo",
}



FONT_PATH = r"C:\Users\Dell\Desktop\himanshi\project\font\TiroDevanagariSanskrit-Regular.ttf"

# Function to perform OCR on the uploaded image
def ocr_image(image_path):
    reader = easyocr.Reader(['en', 'hi'])
    output = reader.readtext(image_path, paragraph=True, batch_size=3)
    sanskrit_text = ""
    for item in output:
        sanskrit_text += item[1] + "\n"
    return sanskrit_text

def insert_translation_into_db(sanskrit_text, translated_text, target_lang):
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS translations (id INTEGER PRIMARY KEY, original_text TEXT,translated_text TEXT, language TEXT)")
    c.execute("SELECT * FROM translations WHERE original_text = ? AND translated_text = ?", (sanskrit_text, translated_text))
    if not c.fetchall():
        c.execute("INSERT INTO translations (original_text, translated_text, language) VALUES (?, ?, ?)", (sanskrit_text, translated_text, target_lang))
        conn.commit()
    conn.close()

# Function to translate Sanskrit text to the selected language
def translate_sanskrit_text(sanskrit_text, target_lang):
    translator = Translator()
    translated_text = translator.translate(sanskrit_text, dest=target_lang).text
    return translated_text



from reportlab.lib import colors

def generate_pdf(original_text, translated_text, logo_image_path, pdf_path):
    pdfmetrics.registerFont(TTFont("CustomFont", FONT_PATH))

    # Create a canvas object with wider pages
    pdf = canvas.Canvas(pdf_path, pagesize=(750, 1200))  # Adjusted page width

    # Draw logo image at the top center of the first page
    logo_width = 400  # Adjusted logo width
    logo_height = 70  # Adjusted logo height
    logo_x = (750 - logo_width) / 2  # Centered horizontally
    logo_y = 1100  # Adjusted to position the logo at the top of the page
    pdf.drawImage(logo_image_path, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')

    # Set font for the entire document
    pdf.setFont("CustomFont", 15)

    # Draw original text heading on the first page
    pdf.drawString(50, 1050, "Original Text (Sanskrit):")  # Adjusted y-coordinate for spacing
    y_offset = 1020  # Adjusted y-coordinate for spacing

    # Wrap and draw original text on the first page
    lines = textwrap.wrap(original_text, width=80)
    for line in lines:
        if y_offset < 50:
            pdf.showPage()  # Create new page if text overflows
            pdf.setFont("CustomFont", 15)  # Reset font at the beginning of each page
            y_offset = 1150  # Reset y-coordinate for new page
        pdf.drawString(50, y_offset, line)
        y_offset -= 20

    # Add space between original and translated text headings
    y_offset -= 50

    # Draw translated text heading on the first page
    pdf.drawString(50, y_offset, "Translated Text:")  # Adjusted y-coordinate for spacing
    y_offset -= 30  # Adjusted y-coordinate for spacing

    # Wrap and draw translated text on the first page
    lines = textwrap.wrap(translated_text, width=80)
    for line in lines:
        if y_offset < 50:
            pdf.showPage()  # Create new page if text overflows
            pdf.setFont("CustomFont", 15)  # Reset font at the beginning of each page
            y_offset = 1150  # Reset y-coordinate for new page
        pdf.drawString(50, y_offset, line)
        y_offset -= 20

    pdf.save()






def main():
    img = Image.open(r'C:\Users\Dell\Desktop\himanshi\project\font\logo6.jpeg')
    desired_width = 2000
    desired_height = 380
    img_resized = img.resize((desired_width, desired_height))
    st.image(img_resized, use_column_width=True)

    st.title("Sanskrit Translator")

    uploaded_file = st.file_uploader("Choose an image or PDF...", type=["jpg","pdf"])
    if uploaded_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg" if uploaded_file.type == 'image/jpeg' else ".pdf")
        temp_file.write(uploaded_file.read())
        temp_file.close()

        if uploaded_file.type == 'image/jpeg':
            sanskrit_text = ocr_image(temp_file.name)
        elif uploaded_file.type == 'application/pdf':
            pdf_reader = PdfReader(temp_file.name)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            sanskrit_text = text

        target_lang = st.selectbox("Select Target Language:", list(LANGUAGES.keys()))

        if target_lang in LANGUAGES:
            translated_text = translate_sanskrit_text(sanskrit_text, LANGUAGES[target_lang])

            # Display original text with custom styling
            st.markdown(
                f"<h2 class='big-text highlight'>Original Text:</h2>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='big-text highlight'>{sanskrit_text}</div>", unsafe_allow_html=True)

            # Display translated text with custom styling
            st.markdown(
                "<h2 class='big-text highlight'>Translated Text:</h2>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='big-text highlight'>{translated_text}</div>", unsafe_allow_html=True)

            insert_translation_into_db(
                sanskrit_text, translated_text, target_lang)

            if st.button("Download PDF"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                    pdf_path = tmpfile.name
                    generate_pdf(sanskrit_text, translated_text, r'C:\Users\Dell\Desktop\himanshi\project\font\logo6.jpeg', pdf_path)
                    st.download_button(label="Click Here", data=open(
                        pdf_path, "rb").read(), file_name="translation.pdf")


        os.unlink(temp_file.name)

if __name__ == "__main__":
    main()
