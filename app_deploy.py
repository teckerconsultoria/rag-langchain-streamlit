import streamlit as st
import os
import tempfile
import logging
from datetime import datetime

from pdf_processor import extract_text_from_pdf, chunk_pdf_text
from vector_store import VectorStore
from response_generator import ResponseGenerator

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar página Streamlit
st.set_page_config(
    page_title="RAG com LangChain, FAISS e OpenAI",
    page_icon="📚",
    layout="wide"
)

# Diretório para salvar o índice FAISS
INDEX_DIR = "faiss_index"
os.makedirs(INDEX_DIR, exist_ok=True)

# Adicionar CSS personalizado para melhorar a aparência em implantação web
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(76, 175, 80, 0.1);
    }
    .upload-btn {
        width: 100%;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar sessão state
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "history" not in st.session_state:
    st.session_state.history = []

# Configuração para implantação web
if "OPENAI_API_KEY" in os.environ:
    default_api_key = os.environ["OPENAI_API_KEY"]
else:
    default_api_key = ""

def process_pdf(pdf_file):
    """
    Processa o arquivo PDF, extrai texto e cria chunks.
    """
    try:
        # Salvar o arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_path = tmp_file.name
        
        # Extrair texto do PDF
        logger.info(f"Processando PDF: {pdf_file.name}")
        text = extract_text_from_pdf(tmp_path)
        
        if not text:
            st.error("Não foi possível extrair texto do PDF. Verifique se o arquivo é válido.")
            return False
        
        # Dividir texto em chunks
        chunks = chunk_pdf_text(text)
        st.session_state.chunks = chunks
        
        # Criar e salvar o armazenamento vetorial
        vector_store = VectorStore(openai_api_key=st.session_state.openai_api_key)
        vector_store.create_vector_store(chunks)
        
        # Salvar o índice FAISS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        index_path = os.path.join(INDEX_DIR, f"index_{timestamp}")
        vector_store.save_vector_store(index_path)
        
        # Atualizar o estado da sessão
        st.session_state.vector_store = vector_store
        st.session_state.pdf_processed = True
        st.session_state.pdf_name = pdf_file.name
        
        # Remover arquivo temporário
        os.unlink(tmp_path)
        
        return True
    except Exception as e:
        logger.error(f"Erro ao processar PDF: {str(e)}")
        st.error(f"Erro ao processar PDF: {str(e)}")
        return False

def generate_answer(query):
    """
    Gera uma resposta para a consulta do usuário.
    """
    try:
        if not st.session_state.vector_store:
            st.error("Nenhum documento processado. Faça upload de um PDF primeiro.")
            return None
        
        # Buscar chunks relevantes
        results = st.session_state.vector_store.similarity_search(query)
        
        if not results:
            st.warning("Não foram encontrados trechos relevantes para sua consulta.")
            return None
        
        # Gerar resposta
        response_generator = ResponseGenerator(openai_api_key=st.session_state.openai_api_key)
        response_data = response_generator.generate_response(query, results)
        
        # Adicionar à história
        st.session_state.history.append({
            "query": query,
            "response": response_data["response"],
            "sources": response_data["sources"]
        })
        
        return response_data
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {str(e)}")
        st.error(f"Erro ao gerar resposta: {str(e)}")
        return None

def main():
    # Título e descrição
    st.title("📚 Aplicação RAG com LangChain, FAISS e OpenAI")
    st.markdown("""
    Esta aplicação permite fazer upload de documentos PDF e fazer perguntas sobre seu conteúdo.
    O sistema usa LangChain, FAISS e OpenAI para processar o documento, indexar seu conteúdo e gerar respostas.
    """)
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("Configurações")
        
        # Chave da API OpenAI
        openai_api_key = st.text_input("Chave da API OpenAI", value=default_api_key, type="password")
        if openai_api_key:
            st.session_state.openai_api_key = openai_api_key
        elif "openai_api_key" not in st.session_state:
            st.session_state.openai_api_key = default_api_key
        
        # Informações sobre o documento processado
        st.header("Informações")
        if st.session_state.pdf_processed:
            st.success(f"Documento processado: {st.session_state.pdf_name}")
            st.info(f"Número de chunks: {len(st.session_state.chunks)}")
            
            # Botão para limpar sessão
            if st.button("Limpar Sessão"):
                st.session_state.vector_store = None
                st.session_state.pdf_processed = False
                st.session_state.pdf_name = None
                st.session_state.chunks = []
                st.session_state.history = []
                st.experimental_rerun()
        else:
            st.info("Nenhum documento processado")
    
    # Abas para upload e consulta
    tab1, tab2, tab3 = st.tabs(["Upload de Documento", "Consulta", "Histórico"])
    
    # Aba de upload
    with tab1:
        st.header("Upload de Documento PDF")
        st.markdown("Faça upload de um documento PDF para processamento e indexação.")
        
        uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")
        
        if uploaded_file is not None:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"Arquivo selecionado: {uploaded_file.name}")
            with col2:
                if st.button("Processar PDF", use_container_width=True, type="primary"):
                    with st.spinner("Processando o documento..."):
                        success = process_pdf(uploaded_file)
                        if success:
                            st.success(f"Documento '{uploaded_file.name}' processado com sucesso!")
                            st.balloons()
    
    # Aba de consulta
    with tab2:
        st.header("Consulta ao Documento")
        
        if not st.session_state.pdf_processed:
            st.warning("Faça upload e processe um documento PDF primeiro.")
        else:
            st.markdown(f"Faça perguntas sobre o documento: **{st.session_state.pdf_name}**")
            
            query = st.text_input("Digite sua pergunta")
            
            if query:
                with st.spinner("Gerando resposta..."):
                    response_data = generate_answer(query)
                    
                    if response_data:
                        st.markdown("### Resposta:")
                        st.markdown(response_data["response"])
                        
                        with st.expander("Ver fontes"):
                            for i, source in enumerate(response_data["sources"]):
                                st.markdown(f"**Trecho {i+1}:** {source['title']} (Score: {source['score']:.4f})")
    
    # Aba de histórico
    with tab3:
        st.header("Histórico de Consultas")
        
        if not st.session_state.history:
            st.info("Nenhuma consulta realizada ainda.")
        else:
            for i, item in enumerate(reversed(st.session_state.history)):
                with st.expander(f"Consulta {len(st.session_state.history) - i}: {item['query']}"):
                    st.markdown("### Resposta:")
                    st.markdown(item["response"])
                    
                    st.markdown("### Fontes:")
                    for j, source in enumerate(item["sources"]):
                        st.markdown(f"**Trecho {j+1}:** {source['title']} (Score: {source['score']:.4f})")
    
    # Rodapé
    st.markdown("""
    <div class="footer">
        <p>Aplicação RAG com LangChain, FAISS e OpenAI | Desenvolvido com Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
