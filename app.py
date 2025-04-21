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
    page_title="Aplicação RAG com LangChain, FAISS e OpenAI",
    page_icon="📚",
    layout="wide"
)

# Diretório para salvar o índice FAISS
INDEX_DIR = "faiss_index"
os.makedirs(INDEX_DIR, exist_ok=True)

# Inicializar sessão state
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []

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
        openai_api_key = st.text_input("Chave da API OpenAI", type="password")
        if openai_api_key:
            st.session_state.openai_api_key = openai_api_key
        elif "openai_api_key" not in st.session_state:
            st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Informações sobre o documento processado
        st.header("Informações")
        if st.session_state.pdf_processed:
            st.success(f"Documento processado: {st.session_state.pdf_name}")
            st.info(f"Número de chunks: {len(st.session_state.chunks)}")
        else:
            st.info("Nenhum documento processado")
    
    # Abas para upload e consulta
    tab1, tab2 = st.tabs(["Upload de Documento", "Consulta"])
    
    # Aba de upload
    with tab1:
        st.header("Upload de Documento PDF")
        st.markdown("Faça upload de um documento PDF para processamento e indexação.")
        
        uploaded_file = st.file_uploader("Escolha um arquivo PDF", type="pdf")
        
        if uploaded_file is not None:
            if st.button("Processar PDF"):
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
                        
                        st.markdown("### Fontes:")
                        for i, source in enumerate(response_data["sources"]):
                            st.markdown(f"**Trecho {i+1}:** {source['title']} (Score: {source['score']:.4f})")

if __name__ == "__main__":
    main()
