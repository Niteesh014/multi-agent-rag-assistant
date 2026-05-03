
import streamlit as st
import os
import json
import shutil
import gc
from datetime import datetime

st.set_page_config(
    page_title="🤖 Multi-Agent RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PATHS
DOCS_PATH = "/content/drive/MyDrive/MultiAgent_RAG_Project/documents"
VECTOR_DB_PATH = "/content/local_chroma_db"
MEMORY_FILE = "/content/drive/MyDrive/MultiAgent_RAG_Project/memory/user_memory.json"

# ═══════ CACHED RESOURCES ═══════
@st.cache_resource
def load_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

@st.cache_resource
def load_groq():
    from groq import Groq
    return Groq(api_key=os.environ["GROQ_API_KEY"])

@st.cache_resource
def load_tavily():
    from tavily import TavilyClient
    return TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# ═══════ VECTOR DB ═══════
def get_vectorstore():
    from langchain_chroma import Chroma
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    return Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=load_embeddings(),
        collection_name="research_papers"
    )

def get_db_count():
    try:
        vs = get_vectorstore()
        count = vs._collection.count()
        del vs
        gc.collect()
        return count
    except:
        return 0

def search_db(query, k=5):
    try:
        vs = get_vectorstore()
        results = vs.similarity_search(query, k=k)
        del vs
        gc.collect()
        return results
    except:
        return []

# ═══════ PDF FUNCTIONS ═══════
def process_new_pdf(file_bytes, filename):
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_chroma import Chroma

    os.makedirs(DOCS_PATH, exist_ok=True)
    pdf_path = os.path.join(DOCS_PATH, filename)
    with open(pdf_path, "wb") as f:
        f.write(file_bytes)

    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(pages)

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    vs = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=load_embeddings(),
        collection_name="research_papers"
    )
    vs.add_documents(chunks)
    del vs
    gc.collect()

    return len(pages), len(chunks)

def get_pdf_list():
    if not os.path.exists(DOCS_PATH):
        return []
    return [f for f in os.listdir(DOCS_PATH) if f.endswith(".pdf")]

def nuclear_reset():
    gc.collect()
    if os.path.exists(DOCS_PATH):
        for f in os.listdir(DOCS_PATH):
            if f.endswith(".pdf"):
                try:
                    os.remove(os.path.join(DOCS_PATH, f))
                except:
                    pass
    if os.path.exists(VECTOR_DB_PATH):
        try:
            shutil.rmtree(VECTOR_DB_PATH)
        except:
            pass
    save_memory({"facts": [], "created": datetime.now().isoformat()})
    os.makedirs(DOCS_PATH, exist_ok=True)
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    st.session_state.messages = []

def delete_all_pdfs_only():
    gc.collect()
    if os.path.exists(DOCS_PATH):
        for f in os.listdir(DOCS_PATH):
            if f.endswith(".pdf"):
                try:
                    os.remove(os.path.join(DOCS_PATH, f))
                except:
                    pass
    if os.path.exists(VECTOR_DB_PATH):
        try:
            shutil.rmtree(VECTOR_DB_PATH)
        except:
            pass
    os.makedirs(DOCS_PATH, exist_ok=True)
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)

def delete_single_pdf(filename):
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_chroma import Chroma

    pdf_path = os.path.join(DOCS_PATH, filename)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    gc.collect()
    if os.path.exists(VECTOR_DB_PATH):
        try:
            shutil.rmtree(VECTOR_DB_PATH)
        except:
            pass
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)

    remaining = [f for f in os.listdir(DOCS_PATH) if f.endswith(".pdf")]
    if remaining:
        all_chunks = []
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        for pdf in remaining:
            loader = PyPDFLoader(os.path.join(DOCS_PATH, pdf))
            pages = loader.load()
            chunks = splitter.split_documents(pages)
            all_chunks.extend(chunks)
        vs = Chroma.from_documents(
            documents=all_chunks,
            embedding=load_embeddings(),
            persist_directory=VECTOR_DB_PATH,
            collection_name="research_papers"
        )
        del vs
        gc.collect()

# ═══════ MEMORY ═══════
def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {"facts": [], "created": datetime.now().isoformat()}

def save_memory(data):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def extract_facts(message):
    client = load_groq()
    prompt = f"""Extract personal facts about the user from: "{message}"
Return ONLY JSON list like ["User likes X"]. Empty list [] if nothing.
Output:"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    try:
        text = response.choices[0].message.content.strip().replace("```json", "").replace("```", "")
        return json.loads(text)
    except:
        return []

# ═══════ AGENTS ═══════
def researcher_agent(query):
    chunks = search_db(query, k=5)
    if not chunks:
        return None, []
    context = "\n\n".join([
        f"[{c.metadata.get('source','').split('/')[-1]}, p.{c.metadata.get('page','')}]\n{c.page_content}"
        for c in chunks
    ])
    prompt = f"Research expert. Answer from these documents:\n{context}\n\nQuestion: {query}\n\n3-4 sentence focused answer:"
    client = load_groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    sources = [f"📄 {c.metadata.get('source','').split('/')[-1]} (p.{c.metadata.get('page','')})" for c in chunks[:3]]
    return response.choices[0].message.content, sources

def web_agent(query):
    try:
        tavily = load_tavily()
        results = tavily.search(query=query, max_results=3)
        context = "\n\n".join([f"[{r['title']}]\n{r['content']}" for r in results["results"]])
        prompt = f"Web research expert. Summarize:\n{context}\n\nQuestion: {query}\n\n3-4 sentences:"
        client = load_groq()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        sources = [f"🌐 [{r['title']}]({r['url']})" for r in results["results"]]
        return response.choices[0].message.content, sources
    except:
        return None, []

def memory_agent(query, memory_data):
    if not memory_data["facts"]:
        return None, []
    facts = "\n".join(f"- {f}" for f in memory_data["facts"])
    prompt = f"User memory:\n{facts}\n\nQuestion: {query}\nProvide relevant personal context in 1-2 sentences, or say No personal context."
    client = load_groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content, ["🧠 Personal Memory"]

def writer_agent(query, agent_outputs):
    combined = ""
    for name, output in agent_outputs.items():
        if output[0]:
            combined += f"\n--- {name} ---\n{output[0]}\n"
    client = load_groq()
    prompt = f"Synthesize a comprehensive answer:\n{combined}\n\nQuestion: {query}\n\nFinal answer:"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content

def orchestrate(query, memory_data):
    client = load_groq()
    decision_prompt = f"""Question: {query}
Pick agents (comma-separated): RESEARCHER (PDFs/research), WEB_SURFER (latest/current info), MEMORY_KEEPER (personal questions)
Decision:"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": decision_prompt}],
        temperature=0.0
    )
    decision = response.choices[0].message.content.upper()
    outputs = {}
    all_sources = []
    agents_used = []
    has_pdfs = get_db_count() > 0

    if "RESEARCHER" in decision and has_pdfs:
        ans, srcs = researcher_agent(query)
        if ans:
            outputs["📚 Researcher"] = (ans, srcs)
            all_sources.extend(srcs)
            agents_used.append("📚 Researcher")

    if "WEB" in decision:
        ans, srcs = web_agent(query)
        if ans:
            outputs["🌐 Web Surfer"] = (ans, srcs)
            all_sources.extend(srcs)
            agents_used.append("🌐 Web Surfer")

    if "MEMORY" in decision:
        ans, srcs = memory_agent(query, memory_data)
        if ans and "No personal" not in ans:
            outputs["🧠 Memory Keeper"] = (ans, srcs)
            all_sources.extend(srcs)
            agents_used.append("🧠 Memory Keeper")

    if not outputs:
        if has_pdfs:
            ans, srcs = researcher_agent(query)
            if ans:
                outputs["📚 Researcher"] = (ans, srcs)
                all_sources.extend(srcs)
                agents_used.append("📚 Researcher")
        else:
            ans, srcs = web_agent(query)
            if ans:
                outputs["🌐 Web Surfer"] = (ans, srcs)
                all_sources.extend(srcs)
                agents_used.append("🌐 Web Surfer")

    if not outputs:
        return "Please upload PDFs or ask a web-based question.", [], []

    final = writer_agent(query, outputs)
    return final, all_sources, agents_used

# ═══════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════

st.title("🤖 Multi-Agent Research Assistant")
st.caption("Powered by RAG + Web Search + Persistent Memory | Built by Niteesh 🚀")
st.divider()

with st.sidebar:
    st.header("📊 Dashboard")

    pdf_count = len(get_pdf_list())
    db_count = get_db_count()
    memory_data = load_memory()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📄 PDFs", pdf_count)
        st.metric("🧠 Memories", len(memory_data["facts"]))
    with col2:
        st.metric("📦 Chunks", db_count)
        st.metric("🤖 Agents", 4)

    st.divider()

    st.subheader("📤 Upload New PDF")
    uploaded_file = st.file_uploader("Add a research paper", type=["pdf"], key="pdf_uploader")
    if uploaded_file is not None:
        if st.button("🚀 Process & Add", type="primary", use_container_width=True):
            with st.spinner(f"Processing {uploaded_file.name}..."):
                file_bytes = uploaded_file.read()
                pages, chunks = process_new_pdf(file_bytes, uploaded_file.name)
                st.success(f"✅ Added! {pages} pages, {chunks} chunks")
                st.balloons()
                st.rerun()

    st.divider()

    st.subheader("📚 Loaded PDFs")
    pdfs = get_pdf_list()
    if pdfs:
        for pdf in pdfs:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"📄 {pdf}")
            with col_b:
                if st.button("❌", key=f"del_{pdf}"):
                    delete_single_pdf(pdf)
                    st.rerun()
    else:
        st.info("No PDFs loaded")

    st.divider()

    st.subheader("🧠 Your Memories")
    if memory_data["facts"]:
        for fact in memory_data["facts"][:5]:
            st.markdown(f"• {fact}")
        if len(memory_data["facts"]) > 5:
            st.caption(f"... and {len(memory_data['facts']) - 5} more")
    else:
        st.info("No memories yet")

    st.divider()

    st.subheader("⚙️ Actions")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col_b:
        if st.button("🧠 Clear Memory", use_container_width=True):
            save_memory({"facts": [], "created": datetime.now().isoformat()})
            st.rerun()

    st.divider()

    st.subheader("⚠️ Danger Zone")
    with st.expander("🔥 Reset Options"):
        st.warning("Cannot be undone!")
        if st.button("🗑️ Delete All PDFs", use_container_width=True):
            delete_all_pdfs_only()
            st.success("Deleted!")
            st.rerun()
        if st.button("💥 NUCLEAR RESET", type="primary", use_container_width=True):
            nuclear_reset()
            st.success("🎉 Reset complete!")
            st.balloons()
            st.rerun()

    st.divider()
    st.subheader("🤖 Active Agents")
    st.markdown("📚 **Researcher** - PDFs")
    st.markdown("🌐 **Web Surfer** - Internet")
    st.markdown("🧠 **Memory Keeper** - You")
    st.markdown("✍️ **Writer** - Synthesis")

# ═══════ MAIN CHAT ═══════
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    if pdf_count == 0:
        st.warning("📤 No PDFs uploaded yet! Upload one in the sidebar, or ask web questions.")
    else:
        st.info("👋 Welcome! Ask me anything about your research papers!")
    with st.expander("💡 Try these example questions"):
        st.markdown("""
        - **PDF:** What is the main contribution of this paper?
        - **Web:** What are the latest AI breakthroughs in 2026?
        - **Personal:** What is my name and what am I working on?
        - **Combined:** Based on my project, what should I learn from these papers?
        """)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "agents" in msg and msg["agents"]:
            st.caption("🤖 Agents: " + " | ".join(msg["agents"]))
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 Sources"):
                for s in msg["sources"]:
                    st.markdown(f"- {s}")

if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agents collaborating..."):
            memory_data = load_memory()
            new_facts = extract_facts(prompt)
            for fact in new_facts:
                if fact not in memory_data["facts"]:
                    memory_data["facts"].append(fact)
            save_memory(memory_data)
            answer, sources, agents = orchestrate(prompt, memory_data)
            st.markdown(answer)
            if agents:
                st.caption("🤖 Agents: " + " | ".join(agents))
            if sources:
                with st.expander("📚 Sources"):
                    for s in sources:
                        st.markdown(f"- {s}")
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "agents": agents,
            "sources": sources
        })
        st.rerun()
