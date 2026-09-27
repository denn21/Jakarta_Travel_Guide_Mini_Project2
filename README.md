# 🧳 Jakarta Travel Guide Assistant

A RAG (Retrieval-Augmented Generation) chatbot that answers questions about tourist destinations in Jakarta — built with **LangChain**, **Groq**, **ChromaDB**, and **Streamlit**.

The assistant only answers based on the source documents provided (no hallucinated facts, no general knowledge fallback), making it a reliable, document-grounded travel guide.

## ✨ Features

- 💬 Conversational chat interface (Streamlit `st.chat_message`)
- 📚 Answers strictly grounded in your own PDF documents (no internet, no made-up info)
- 🔍 Retrieval-Augmented Generation pipeline: PDF → chunking → embedding → vector search → LLM
- 🎯 Example question buttons + follow-up question suggestions to keep users engaged
- 👍 Thumbs up/down feedback on every answer
- 🎨 Custom light, cheerful theme

## 🛠️ Tech Stack

| Component      | Tool                          |
|----------------|--------------------------------|
| LLM            | Groq (`openai/gpt-oss-120b`)   |
| Framework      | LangChain (LCEL)                |
| Vector Store   | ChromaDB                        |
| PDF Loader     | PyMuPDF4LLM                     |
| UI             | Streamlit                       |

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Add your knowledge documents
Place your source PDF files inside the `knowledge_docs/` folder.

### 5. Run the app
```bash
streamlit run app.py
```

## 📁 Project Structure

```
.
├── app.py               # Streamlit UI
├── rag_chatbot.py        # RAG pipeline (loading, chunking, retrieval, chain)
├── system_prompt.md      # System prompt controlling the assistant's behavior
├── knowledge_docs/        # Source PDF documents
├── .env                   # API keys (not committed)
└── requirements.txt
```

## ⚠️ Disclaimer

This assistant only answers based on the documents provided as its knowledge base. It is not an official travel agency, booking service, or emergency service, and does not provide real-time information (traffic, weather, availability).

## 👤 Author

Made by **Dennis Fahriansyah**
