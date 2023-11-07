import streamlit as st
import tempfile
import os
import fitz  # PyMuPDF
import requests

url = "https://microsoft-translator-text.p.rapidapi.com/translate"

headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "5701363bbcmshb239dc6ed0c116bp18dc4djsn46cd100f0ad9",
	"X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com"
}

# Define a dictionary to map Braille to English characters
braille_to_english_dict = {
    '⠁': ['a', '1'],
    '⠃': ['b', '2'],
    '⠉': ['c', '3'],
    '⠙': ['d', '4'],
    '⠑': ['e', '5'],
    '⠋': ['f', '6'],
    '⠛': ['g', '7'],
    '⠓': ['h', '8'],
    '⠊': ['i', '9'],
    '⠚': ['j', '0'],
    '⠅': ['k'],
    '⠇': ['l'],
    '⠍': ['m'],
    '⠝': ['n'],
    '⠕': ['o'],
    '⠏': ['p'],
    '⠟': ['q'],
    '⠗': ['r'],
    '⠎': ['s'],
    '⠞': ['t'],
    '⠥': ['u'],
    '⠧': ['v'],
    '⠺': ['w'],
    '⠭': ['x'],
    '⠽': ['y'],
    '⠵': ['z'],
    '⠀': [' '],  # Braille space
    '⠒': [':'],
    '⠐': ['('],
    '⠤': ['-'],
    '⠈': ['@'],
    '⠴': ['%'],
    '⠼': ['#'],  # Consider '#' as a distinction
    '⠜': ['>'],
    '⠘': [')'],
    '⠾': [']'],
    '⠸': ['/'],
    '⠬': ['+'],
    '⠷': ['['],
    '⠳': ['{']
    # Define your Braille to English mappings here
}

braille_dict = {
    'a': '⠁',
    'b': '⠃',
    'c': '⠉',
    'd': '⠙',
    'e': '⠑',
    'f': '⠋',
    'g': '⠛',
    'h': '⠓',
    'i': '⠊',
    'j': '⠚',
    'k': '⠅',
    'l': '⠇',
    'm': '⠍',
    'n': '⠝',
    'o': '⠕',
    'p': '⠏',
    'q': '⠟',
    'r': '⠗',
    's': '⠎',
    't': '⠞',
    'u': '⠥',
    'v': '⠧',
    'w': '⠺',
    'x': '⠭',
    'y': '⠽',
    'z': '⠵',
    ',': ':',
    '0': '⠼⠚',
    '1': '⠼⠁',
    '2': '⠼⠃',
    '3': '⠼⠉',
    '4': '⠼⠙',
    '5': '⠼⠑',
    '6': '⠼⠋',
    '7': '⠼⠛',
    '8': '⠼⠓',
    '9': '⠼⠊',
    ' ': '⠀',
    ';': ':',
    'A': '⠁',
    'B': '⠃',
    'C': '⠉',
    'D': '⠙',
    'E': '⠑',
    'F': '⠋',
    'G': '⠛',
    'H': '⠓',
    'I': '⠊',
    'J': '⠚',
    'K': '⠅',
    'L': '⠇',
    'M': '⠍',
    'N': '⠝',
    'O': '⠕',
    'P': '⠏',
    'Q': '⠟',
    'R': '⠗',
    'S': '⠎',
    'T': '⠞',
    'U': '⠥',
    'V': '⠧',
    'W': '⠺',
    'X': '⠭',
    'Y': '⠽',
    'Z': '⠵',
    ':': '⠒',
    '(': '⠐',
    ')': '⠘',
    '-': '⠤',
    '/': '⠸',
    '@': '⠈',
    '+': '⠬',
    '&': '⠧',
    '%': '⠴',
    '*': '⠭',
    '#': '⠼',
    '>': '⠜',
    '[': '⠷',
    ']': '⠾',
    '{': '⠳',
    '$': '⠢',
    '=': '⠐⠶',
    '<': '⠐⠣',
    '}': '⠷⠾',
    '': ' '  # Braille space
}

lang2code = {
    'Arabic': 'ar',
    'Chinese Simplified': 'zh-Hans',
    'Chinese Traditional': 'zh-Hant',
    'English': 'en',
    'French': 'fr',
    'German': 'de',
    'Spanish': 'es',
    'Italian': 'it',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Dutch': 'nl',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Turkish': 'tr',
    'Vietnamese': 'vi',
    'Hindi': 'hi',
    'Bengali': 'bn',
    'Urdu': 'ur',
    'Punjabi': 'pa',
    'Tamil': 'ta'
}
code2lang = {
    'ar': 'Arabic',
    'zh-Hans': 'Chinese Simplified',
    'zh-Hant': 'Chinese Traditional',
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'nl': 'Dutch',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'pa': 'Punjabi',
    'ta': 'Tamil'
}


# Function to convert Braille to English
def braille_to_english(braille_text):
    english_text = ""
    previous_translation_type = None  # To track the type of the previous translation

    for char in braille_text:
        if char in braille_to_english_dict:
            possible_translations = braille_to_english_dict[char]

            if '#' in possible_translations:
                previous_translation_type = 'digit'
                continue
            else:
                if previous_translation_type == 'digit':
                    flag=0
                    for t in possible_translations:

                        if(t.isnumeric()):
                            english_text+=t
                            flag=1
                            previous_translation_type=None
                    # if(flag==0):

                    # translation = [t for t in possible_translations if t.isnumeric()]
                    # if(translation):
                    #     previous_translation_type='digit'
                    
                    # previous_translation_type = 'digit' if translation else None
                else:
                    translation = possible_translations
                    english_text += translation[0]
                    previous_translation_type = None  # Reset the previous_translation_type if it was not 'digit'

            # if translation:
            #     english_text += translation[0]
            # else:
            #     english_text += char  # Use the character itself if no suitable translation found
        else:
            english_text += char  # If the character is not in the dictionary, leave it unchanged

    return english_text


# Function to convert English to Braille
def text_to_braille(text):
    braille_text = ""
    for char in text:
        if char in braille_dict:
            braille_text += braille_dict[char]
        else:
            braille_text += char  # If the character is not in the dictionary, leave it unchanged
    return braille_text

def translate_text(text, output_lang):
    querystring = {"to[0]": output_lang,
                   "api-version":"3.0",
                   "profanityAction":"NoAction",
                   "textType":"plain"
                    }
    
    payload = [{ "Text": text }]
    
    response = requests.post(url, json=payload, headers=headers, params=querystring)
    return response.json()[0]['translations'][0]['text']


# Define the Translator page
def translate_page():
    st.title("Multilingual/Braille Translator")

    # Language selection
    input_language = st.selectbox("Select Input Language", ["Braille","Arabic","Chinese Simplified","Chinese Traditional","English","French","German","Spanish","Italian","Japanese","Korean","Dutch","Portuguese","Russian","Turkish","Vietnamese","Hindi","Bengali","Urdu","Punjabi","Tamil"])
    output_language = st.selectbox("Select Output Language", ["Braille","Arabic","Chinese Simplified","Chinese Traditional","English","French","German","Spanish","Italian","Japanese","Korean","Dutch","Portuguese","Russian","Turkish","Vietnamese","Hindi","Bengali","Urdu","Punjabi","Tamil"])


    # Input and output text
    input_text = st.text_area("Input Text")
    output_text = ""

    if st.button("Translate"):
        if input_language == "Braille":
            english_text = braille_to_english(input_text)
            if output_language == "English":
                # Convert Braille to English
                output_text = english_text
            else:
                converted_text = translate_text(english_text, lang2code[output_language] )
                output_text = converted_text

        elif output_language == "Braille":
            # Convert English to Braille (implement this logic)
            if input_language == "English":
                final_input_text = input_text
            else:
                # converting the input language to english
                final_input_text = translate_text(input_text, "en")

            output_text = text_to_braille(final_input_text)

        else:
            output_text = translate_text(input_text, lang2code[output_language] )

    st.write("Translated Text:")
    st.text_area("Output Text", output_text)

# Function to extract text from a PDF and save it to a text file
def pdf_to_text_file(pdf_file, input_lang, output_lang):
    temp_pdf_filename = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()) + ".pdf")

    with open(temp_pdf_filename, "wb") as temp_pdf:
        temp_pdf.write(pdf_file.read())

    pdf_document = fitz.open(temp_pdf_filename)
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

    pdf_document.close()
    os.remove(temp_pdf_filename)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as text_file:
        text_file.write(text)
        text_file_path = text_file.name

    return text_file_path, text


# Define the PDF page
def pdf_page():
    st.title("PDF Translator")

    # Language selection
    input_language = st.selectbox("Select Input Language", ["Braille","Arabic","Chinese Simplified","Chinese Traditional","English","French","German","Spanish","Italian","Japanese","Korean","Dutch","Portuguese","Russian","Turkish","Vietnamese","Hindi","Bengali","Urdu","Punjabi","Tamil"])
    output_language = st.selectbox("Select Output Language", ["Braille","Arabic","Chinese Simplified","Chinese Traditional","English","French","German","Spanish","Italian","Japanese","Korean","Dutch","Portuguese","Russian","Turkish","Vietnamese","Hindi","Bengali","Urdu","Punjabi","Tamil"])

    # PDF file upload
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner("Translating..."):
            text_file_path, input_text = pdf_to_text_file(uploaded_file, input_language, output_language)

            if input_language == "Braille":
                english_text = braille_to_english(input_text)
                if output_language == "English":
                    # Convert Braille to English
                    output_text = english_text
                else:
                    converted_text = translate_text(english_text, lang2code[output_language] )
                    output_text = converted_text

            elif output_language == "Braille":
                # Convert English to Braille (implement this logic)
                if input_language == "English":
                    final_input_text = input_text
                else:
                    # converting the input language to english
                    final_input_text = translate_text(input_text, "en")

                output_text = text_to_braille(final_input_text)

            else:
                output_text = translate_text(input_text, lang2code[output_language] )

        st.write("Translated Text:")
        st.text_area("Output Text", output_text)


# Define the Streamlit app
def main():
    st.set_page_config(page_title="Braille Translator")

    # Create a navigation menu
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio("Go to", ("Translator", "PDF"))

    if selected_page == "Translator":
        translate_page()
    else:
        pdf_page()


if __name__ == "__main__":
    main()
