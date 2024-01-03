import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import os

os.environ["OPENAI_API_KEY"] = "" #add your API key here

def upload_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        doc_path.set(file_path)

def submit_and_open():
    if not doc_path.get():
        messagebox.showerror("Error", "Please upload a PDF first.")
        return

    pdf_reader = PdfReader(doc_path.get())
    pdf_text = ""
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=800,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_text(pdf_text)

    embeddings = OpenAIEmbeddings()
    document_search = FAISS.from_texts(texts, embeddings)

    chain = load_qa_chain(OpenAI(), chain_type="stuff")

    query = query_entry.get()
    if not query:
        messagebox.showerror("Error, Please enter a query.")
        return

    docs = document_search.similarity_search(query)
    
    result = chain.run(input_documents=docs, question=query)

    result_text = f"Query: {query} \nAnswer: {result}"
    
    output_text.config(state=tk.NORMAL)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, result_text)
    output_text.config(state=tk.DISABLED)

root = tk.Tk()
root.title("PDF QA System")

doc_path = tk.StringVar()

tk.Label(root, text="Selected PDF Path:").pack(pady=10)
tk.Label(root, textvariable=doc_path).pack(pady=10)

tk.Button(root, text="Upload PDF", command=upload_pdf).pack(pady=20)

query_entry = tk.Entry(root, width=50)
query_entry.pack(pady=10, padx=10)

submit_button = tk.Button(root, text="Submit Query", command=submit_and_open)
submit_button.pack(pady=20)

output_text = tk.Text(root, height=30, width=100, state=tk.DISABLED)
output_text.pack(pady=10, padx=10)

root.mainloop()
