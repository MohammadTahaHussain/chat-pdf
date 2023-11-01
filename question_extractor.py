import re
from PyPDF2 import PdfReader
# from question_check import is_question


def get_pdf_text(pdf_docs):
    text = ""
    for pdf_doc in pdf_docs:
        pdf_reader = PdfReader(pdf_doc)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_pdf_questions(pdf_docs):
    raw_text = get_pdf_text(pdf_docs)
    question_pattern = r'Question \d+\s+(.+?)(?=(Question \d+|\Z))'
    questions = re.findall(question_pattern, raw_text, re.DOTALL)
    extracted_questions = []
    for i, question in enumerate(questions, start=1):
        temp_question = '\n'.join(map(str, question))
        pattern = r'(.*?)(?=\n\d\.|\n\n|\Z)'
        sentences = re.split(r'\n(?=\d)', temp_question)
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        temp_question = sentences[0]
        sentences = re.split(r'\n\s*\n+', temp_question)
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        temp_question = sentences[0]
        # Find the first match in the text
        match = re.search(pattern, temp_question, re.DOTALL)

        if match:
            question1 = match.group(1)
            tokens = re.findall(r'\w+', question1)
            # question1 = ' '.join(tokens[:100])
            if len(tokens) <= 20:
                extracted_questions.append(question1.strip().replace('\n', ' '))

    return extracted_questions


# pdf_docs = ['PDFF.pdf']
# extracted_questions = get_pdf_questions(pdf_docs)
# #
# # for i, question in enumerate(extracted_questions):
# #     question = question.replace('\n', ' ')
# #     print(f"Question {i+1}: {question} : {is_question(question)}")
#
# # print(extracted_questions)
# c = 1
# for x in extracted_questions:
#     tokens = re.findall(r'\w+', x)
#     if len(x) <= 100:
#         print("{0}: {1}".format(c, x))
#         c+=1
#     else:
#         print("{0}: {1}".format(c, ' '.join(tokens[:100])))
#         c+=1


