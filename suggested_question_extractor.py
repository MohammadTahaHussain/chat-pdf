import openai
from PyPDF2 import PdfReader
import re

def get_pdf_text(pdf_docs):
    text = ""
    for pdf_doc in pdf_docs:
        pdf_reader = PdfReader(pdf_doc)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    # Define the desired chunk size
    chunk_size = 1500

    # Initialize variables to keep track of the current position and the list of chunks
    current_position = 0
    chunks = []

    # Loop through the text and split it into chunks
    while current_position < len(text):
        # Extract a chunk of the specified size
        chunk = text[current_position:current_position + chunk_size]

        # Append the chunk to the list of chunks
        chunks.append(chunk)

        # Update the current position
        current_position += chunk_size
    return chunks


def get_suggested_questions(pdf_doc, api_key):
    openai.api_key = api_key
    text = get_pdf_text(pdf_doc)
    # text = text[text.lower().index('introduction'):]
    chunks = get_text_chunks(text)
    # Print or process the list of chunks as needed
    suggested_questions = []
    for chunk in chunks:
        response = openai.Completion.create(
            engine="babbage-002",
            prompt=f"Generate questions from the following text: '{chunk}'\n\nQuestions:",
            max_tokens=100,  # Adjust as needed
            n = 100  # Number of questions to generate
        )
        # Extract the generated questions
        questions = response.choices[0].text.strip().split("\n")
        # Print the generated questionss
        for i, question in enumerate(questions):
            tokens = re.findall(r'\w+', question)

            if '?' in question and len(tokens) < 50 and len(tokens) > 5:
                question_pattern = r"[^.!?]*\?+"
                questions_ = re.findall(question_pattern, question)
                for i, q in enumerate(questions):
                    suggested_questions.append(q)
        if len(list(set(suggested_questions))) >=20:
            break
    # suggested_questions = [x for x in suggested_questions if len(re.findall(r'\w+', x)) >=6]
    questions = extract_questions(suggested_questions)
    return questions


# questions = [' 1.    Which of the following is an acceptable way of reversing a forklift? a. Keep left foot resting on foot plate below accelerator b. Move all weight onto right foot c. Put a hand on steering wheel under R hand side of dash d. Put hand onto steering wheel over R hand side of dash Answer: c ', ' 2.    Which of the following statements about avoiding falling loads is correct? a. Remain in the forklift until the', '10: The answers to the first question leads other to consider what types of transportation vehicles are used in the Haymarket District?', 'What type of WHS/OHS information does your business need to provide? What are your personal responsibilities as a licence holder? Previous Page Next Page', 'What do you do at your workplace when a new machine, equipment or parts arrive?  ', '   What do you need to ask your trainer before you use a new machine or equipment?   What are some workplace procedures at your workplace?  ', '  \t AWFTC TLILIC00 03 – Learner Guide                                Version 2.0                  21 April 2020                     Page 9 of 52 ', ' 2 Stream: Maintain vehicle and equipment systems  ', 'What do you do at your workplace when a new machine, equipment or parts arrive?  ', '   What do you need to ask your trainer before you use a new machine or equipment?   What are some workplace procedures at your workplace?  ', '  \t AWFTC TLILIC00 03 – Learner Guide                                Version 2.0                  21 April 2020                     Page 9 of 52 ', ' 2 Stream: Maintain vehicle and equipment systems  ']


def is_question(text):
    question_words = ["what", "where", "when", "who", "why", "how", "are", "am", "can", "could", "should",
                      "may", "might", "do", "does", "did", "will", "would", "shall", "should", "have", "has", "had",
                      "could", "can", "are"]

    text = text.lower()

    for word in question_words:
        if text.startswith(word):
            return True

    return False

def extract_questions(questions):
    # Define a regular expression pattern to match questions.
    question_pattern = r'\b(?:what|where|when|who|why|how|is|are|am|can|could|should|may|might|do|does|did|will|would|shall|should|have|has|had|could|can|are)\b.*?\?'

    # Find all matches in the text.
    # questions = re.findall(question_pattern, text, re.IGNORECASE)

    questions = [re.findall(question_pattern, x, re.IGNORECASE) for x in questions]
    from itertools import chain
    questions = list(chain(*questions))
    questions = list(filter(None, questions))
    # questions = [x for x in questions]/

    # Print the extracted questions.
    suggested_questions = []
    for question in questions:
        if is_question(question):
            suggested_questions.append(question)
    return suggested_questions


# pdf_doc = [r'C:/Users/waqar/Downloads/TLILIC0003-Learner-Guide_Apr20.pdf']
# api_key = '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'
# questions = get_suggested_questions(pdf_doc, api_key)
# questions = ['what are the injury causes at work?', 'What happened to the worker who sustained injuries by fall?', 'are some examples of fall from heights?', 'What 3x component causes a person to slip on wet slippery surface?', 'what are the injury causes at work?', 'What happened to the worker who sustained injuries by fall?', 'are some examples of fall from heights?', 'What 3x component causes a person to slip on wet slippery surface?', 'what are the injury causes at work?', 'What happened to the worker who sustained injuries by fall?', 'are some examples of fall from heights?', 'What 3x component causes a person to slip on wet slippery surface?', 'what are the injury causes at work?', 'What happened to the worker who sustained injuries by fall?', 'are some examples of fall from heights?', 'What 3x component causes a person to slip on wet slippery surface?']
# questions = list(set(questions))
# print(questions)
# questions = 'What is my name.'
# if not questions.strip().endswith('?') and not questions.endswith('.'):
#     print('a')
# else:
#     print('b')
