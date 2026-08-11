from fastapi import FastAPI, UploadFile, File, Form
import fitz
import pytesseract
from PIL import Image
import re
from deep_translator import GoogleTranslator


# =========================
#
# =========================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================
# FASTAPI APP
# =========================

app = FastAPI(
    title="Kingdom of SP",
    description="JEE PDF Summary, OCR and Translation",
    version="1.0"
)


# =========================
# HOME
# =========================

from fastapi.responses import FileResponse

@app.get("/")
def home():
    return FileResponse("index.html")

# =========================
# QUESTION + OPTIONS DETECT
# =========================

def detect_question_and_options(text):

    lines = text.splitlines()

    question_lines = []

    options = {
        "A": "",
        "B": "",
        "C": "",
        "D": ""
    }

    current_option = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # A / B / C / D detect
        match = re.match(
            r"^\(?([A-Da-d])\)?[\.\:\-\s]+(.+)",
            line
        )

        if match:

            current_option = match.group(1).upper()

            options[current_option] = (
                match.group(2).strip()
            )

        elif current_option:

            options[current_option] += (
                " " + line
            )

        else:

            question_lines.append(line)

    return {
        "question": " ".join(question_lines),
        "options": options
    }


# =========================
# TRANSLATION
# =========================

def translate_to_bengali(text):

    if not text.strip():
        return ""

    try:

        translator = GoogleTranslator(
            source="auto",
            target="bn"
        )

        # Google translator-এর text limit এড়ানোর জন্য
        # ছোট ছোট অংশে translate করা হচ্ছে

        chunks = []

        words = text.split()

        current_chunk = ""

        for word in words:

            if len(current_chunk) + len(word) < 4000:

                current_chunk += " " + word


                chunks.append(current_chunk.strip())

                current_chunk = word

        if current_chunk:
            chunks.append(current_chunk.strip())

        translated_chunks = []

        for chunk in chunks:

            translated = translator.translate(chunk)

            translated_chunks.append(translated)

        return " ".join(translated_chunks)

    except Exception as e:

        return "Translation Error: " + str(e)


# =========================
# UPLOAD
# =========================

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    action: str = Form("extract")
):

    contents = await file.read()


    # ==================================================
    # IMAGE UPLOAD
    # ==================================================

    if (
        file.content_type
        and file.content_type.startswith("image")
    ):

        with open("temp_image.png", "wb") as f:

            f.write(contents)


        img = Image.open("temp_image.png")


        # OCR
        text = pytesseract.image_to_string(
            img,
            lang="eng+ben"
        )


        # Question + Options
        detected = detect_question_and_options(text)


        # =========================
        # TRANSLATE TO BANGLA
        # =========================

        if action == "translate":

            translated_text = translate_to_bengali(
                text
            )

            translated_question = translate_to_bengali(
                detected["question"]
            )

            translated_options = {}

            for key, value in detected["options"].items():

                translated_options[key] = (
                    translate_to_bengali(value)
                    if value
                    else ""
                )


            return {
                "filename": file.filename,
                "action": "translate",
                "extracted_text": text,
                "translated_text": translated_text,
                "question": translated_question,
                "options": translated_options
            }


        # =========================
        # NORMAL EXTRACT
        # =========================

        return {
            "filename": file.filename,
            "action": "extract",
            "extracted_text": text,
            "question": detected["question"],
            "options": detected["options"]
        }


    # ==================================================
    # PDF UPLOAD
    # ==================================================

    with open("temp.pdf", "wb") as f:

        f.write(contents)


    doc = fitz.open("temp.pdf")

    all_text = []

    highlights = []


    for page_num, page in enumerate(doc):

        # PDF text
        page_text = page.get_text()


        if page_text:

            all_text.append(page_text)


        # Highlight / Underline
        annotations = page.annots()


        if annotations:

            for annot in annotations:

                if annot.type[1] in [
                    "Highlight",
                    "Underline"
                ]:

                    highlights.append({
                        "page": page_num + 1,
                        "type": annot.type[1]
                    })


    combined_text = "\n".join(all_text)


    detected = detect_question_and_options(
        combined_text
    )


    # =========================
    # PDF TRANSLATION
    # =========================

    if action == "translate":

        translated_text = translate_to_bengali(
            combined_text
        )

        translated_question = translate_to_bengali(
            detected["question"]
        )

        translated_options = {}

        for key, value in detected["options"].items():

            translated_options[key] = (
                translate_to_bengali(value)
                if value
                else ""
            )


        return {
            "filename": file.filename,
            "action": "translate",
            "extracted_text": combined_text,
            "translated_text": translated_text,
            "question": translated_question,
            "options": translated_options,
            "highlights_found": highlights
        }


    # =========================
    # NORMAL PDF RESULT
    # =========================

    return {
        "filename": file.filename,
        "action": "extract",
        "extracted_text": combined_text,
        "question": detected["question"],
        "options": detected["options"],
        "highlights_found": highlights
    }