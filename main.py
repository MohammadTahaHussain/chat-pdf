import time

import openai
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplate import css
import pickle
import os.path
import re
from question_extractor import get_pdf_questions
import pandas as pd
from datetime import datetime
from suggested_question_extractor import get_suggested_questions


openai.api_key = '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'

def get_pdf_text(pdf_docs):
    text = ""
    for pdf_doc in pdf_docs:
        pdf_reader = PdfReader(pdf_doc)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(raw_text):
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_text(raw_text)
    return chunks


def get_conversation_chain(vector_store):
    llm = ChatOpenAI(model="gpt-3.5-turbo-0301")
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature": 0.5, "max_length": 512})
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, output_key='answer')

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory
    )

    return conversation_chain


def get_vectorstore(text_chunks):
    # embeddings = HuggingFaceInstructEmbeddings(model_name='hkunlp/instructor-xl')
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(text_chunks, embeddings)
    return vectorstore


def handle_userinput(user_question):
    try:
        response = st.session_state.conversation({'question': user_question+' Request for Conciseness: Please provide a short and direct answer.'})
        # st.session_state.chat_history = response['chat_history']
        data = {}
        for i, message in enumerate(response['chat_history']):
            if i % 2 == 0:
                data['Question'] = user_question
            else:
                # st.write(bot_template.replace(
                #     "{{MSG}}", message.content), unsafe_allow_html=True)
                data['Answer'] = message.content
        return data
    except Exception as ex:
        print(ex.args)
        print('got timed out, or rate limit increased.')
        time.sleep(300)
        return None






def main():
    load_dotenv()
    process_clicked = False
    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:")

    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "processed" not in st.session_state:
        st.session_state.processed = False
    tab1, tab2 = st.tabs(["Extracted Questions", "Suggested Questions"])


    process_btn = None
    with st.sidebar:
        st.subheader('Your documents')
        pdf_docs = st.file_uploader("Upload your answer's PDFs here.", accept_multiple_files=True)
        question_docs = st.file_uploader("Upload your question's PDFs here", accept_multiple_files=True)
        vector_file_name = None
        process_btn = st.button('Process')
        if len(pdf_docs) > 0:
            vector_file_name = pdf_docs[0].name
        if process_btn:
            with st.spinner('Processing'):
                #get pdf text

                raw_text = get_pdf_text(pdf_docs)
                #get text chunks
                text_chunks = get_text_chunks(raw_text)
                # st.write(text_chunks)
                #create vector store
                if os.path.exists(vector_file_name):
                    with open(vector_file_name, 'rb') as f:
                        vector_store = pickle.load(f)
                else:
                    vector_store = get_vectorstore(text_chunks)
                    with open(vector_file_name, 'wb') as f:
                        pickle.dump(vector_store, f)

                st.session_state.conversation = get_conversation_chain(vector_store)
                st.session_state.processed = True

    rest = 0
    if st.session_state.processed:
        with tab1:
            st.header("Extracted Questions and Answers")
            if st.button('Start Extraction'):
                progress_text = "Operation in progress. Please wait."
                my_bar = st.progress(0, text=progress_text)
                extracted_questions = get_pdf_questions(question_docs)
                results = []
                start_time = datetime.now()
                c = 1
                for questions in extracted_questions:
                    tokens = re.findall(r'\w+', questions)
                    if len(tokens) >=25:
                        c += 1
                        continue
                    if not questions.strip().endswith('?') and not questions.endswith('.'):
                        c += 1
                        continue
                    c+=1
                    data = handle_userinput(questions)
                    st.session_state.conversation.memory.clear()
                    if data:
                        try:
                            results.append(data)
                            progress_text = "Extracting: {0}/{1}".format(len(results), len(extracted_questions))
                            percentage = (len(results) / len(extracted_questions)) * 100
                            my_bar.progress(percentage/100, text=progress_text)
                        except Exception as ex:
                            print(ex.args)
                    rest+=1
                    if rest == 6:
                        time.sleep(30)
                        rest = 0
                time_elapsed = datetime.now() - start_time
                print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
                df = pd.DataFrame(results, index=range(1, len(results) + 1))
                df = df.replace('\n','<br>', regex=True)
                df_html = df.to_html(escape=False)
                my_bar.empty()
                # Display the HTML as markdown to preserve line breaks
                st.markdown(df_html, unsafe_allow_html=True)
        with tab2:
            questions = get_suggested_questions(pdf_docs, openai.api_key)
            questions = list(set(questions))
            d = []
            for q in questions:
                d.append({'Suggested Question': q})
            df2 = pd.DataFrame(d, index=range(1, len(d) + 1))
            df2 = df2.replace('\n', '<br>', regex=True)
            df_html2 = df2.to_html(escape=False)
            # Display the HTML as markdown to preserve line breaks
            st.markdown(df_html2, unsafe_allow_html=True)



if __name__ == '__main__':
    main()


