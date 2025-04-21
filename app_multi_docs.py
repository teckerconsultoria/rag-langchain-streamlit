import streamlit as st
import os
import tempfile
import logging
from datetime import datetime

from pdf_processor import extract_text_from_pdf, chunk_pdf_text
from knowledge_base import KnowledgeBase
from file_manager import FileManager
from response_generator import ResponseGenerator

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar página Streamlit
st.set_page_config(
    page_title="RAG com Base de Conhecimento",
    page_icon="📚",
    layout="wide"
)

# Diretório para a base de conhecimento
KB_DIR = "knowledge_base"
os.makedirs(KB_DIR, exist_ok=True)

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
    .document-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #eee;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
    .document-card h4 {
        margin-top: 0;
    }
    .document-actions {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
    }
    .filter-section {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuração para implantação web
if "OPENAI_API_KEY" in os.environ:
    default_api_key = os.environ["OPENAI_API_KEY"]
else:
    default_api_key = ""

def initialize_session_state():
    """Inicializa o estado da sessão com valores padrão."""
    if "knowledge_base" not in st.session_state:
        st.session_state.knowledge_base = None
    if "file_manager" not in st.session_state:
        st.session_state.file_manager = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "selected_docs" not in st.session_state:
        st.session_state.selected_docs = []
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = default_api_key

def initialize_knowledge_base():
    """Inicializa a base de conhecimento."""
    if st.session_state.knowledge_base is None:
        st.session_state.knowledge_base = KnowledgeBase(
            openai_api_key=st.session_state.openai_api_key,
            kb_path=KB_DIR
        )
        st.session_state.file_manager = FileManager(st.session_state.knowledge_base)
        logger.info("Base de conhecimento inicializada")

def generate_answer(query, filter_docs=None):
    """
    Gera uma resposta para a consulta do usuário.
    
    Args:
        query: Consulta do usuário
        filter_docs: Lista opcional de IDs de documentos para filtrar a busca
    
    Returns:
        Dados da resposta ou None se ocorrer um erro
    """
    try:
        if not st.session_state.knowledge_base:
            st.error("Base de conhecimento não inicializada.")
            return None
        
        # Buscar chunks relevantes
        results = st.session_state.knowledge_base.similarity_search(
            query, 
            k=3, 
            filter_doc_ids=filter_docs
        )
        
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
            "sources": response_data["sources"],
            "timestamp": datetime.now().isoformat(),
            "filter_docs": filter_docs
        })
        
        return response_data
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {str(e)}")
        st.error(f"Erro ao gerar resposta: {str(e)}")
        return None

def display_document_list():
    """Exibe a lista de documentos na base de conhecimento."""
    documents = st.session_state.knowledge_base.get_all_documents()
    
    if not documents:
        st.info("Nenhum documento na base de conhecimento.")
        return
    
    st.write(f"### Documentos na Base de Conhecimento ({len(documents)})")
    
    for doc_id, doc_info in documents.items():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="document-card">
                    <h4>{doc_info['name']}</h4>
                    <p>Adicionado em: {doc_info['added_at'][:16].replace('T', ' às ')}</p>
                    <p>Chunks: {doc_info['chunk_count']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='document-actions'>", unsafe_allow_html=True)
                if st.button(f"Remover", key=f"remove_{doc_id}"):
                    if st.session_state.knowledge_base.remove_document(doc_id):
                        st.success(f"Documento '{doc_info['name']}' removido com sucesso!")
                        st.experimental_rerun()
                    else:
                        st.error(f"Erro ao remover documento '{doc_info['name']}'")
                st.markdown("</div>", unsafe_allow_html=True)

def main():
    # Inicializar estado da sessão
    initialize_session_state()
    
    # Título e descrição
    st.title("📚 Base de Conhecimento RAG")
    st.markdown("""
    Esta aplicação permite criar uma base de conhecimento a partir de múltiplos documentos PDF.
    Faça upload de vários arquivos, processe-os e faça perguntas sobre seu conteúdo.
    """)
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("Configurações")
        
        # Chave da API OpenAI
        openai_api_key = st.text_input("Chave da API OpenAI", value=st.session_state.openai_api_key, type="password")
        if openai_api_key:
            st.session_state.openai_api_key = openai_api_key
            # Reinicializar a base de conhecimento se a chave mudar
            if st.session_state.knowledge_base is not None and st.session_state.knowledge_base.openai_api_key != openai_api_key:
                st.session_state.knowledge_base = None
                st.experimental_rerun()
        
        # Inicializar a base de conhecimento
        initialize_knowledge_base()
        
        # Informações sobre a base de conhecimento
        st.header("Informações")
        documents = st.session_state.knowledge_base.get_all_documents()
        st.info(f"Documentos na base: {len(documents)}")
        
        # Botão para limpar sessão
        if st.button("Limpar Histórico de Consultas"):
            st.session_state.history = []
            st.success("Histórico de consultas limpo!")
    
    # Abas para upload, gerenciamento, consulta e histórico
    tab1, tab2, tab3, tab4 = st.tabs([
        "Upload de Documentos", 
        "Gerenciar Base de Conhecimento", 
        "Consulta", 
        "Histórico"
    ])
    
    # Aba de upload
    with tab1:
        st.header("Upload de Documentos PDF")
        st.markdown("Faça upload de um ou mais documentos PDF para adicionar à base de conhecimento.")
        
        # Upload de múltiplos arquivos
        uploaded_files = st.file_uploader(
            "Escolha um ou mais arquivos PDF", 
            type="pdf",
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.write(f"Arquivos selecionados: {len(uploaded_files)}")
            
            # Botão para processar todos os arquivos
            if st.button("Processar Todos os Arquivos", type="primary"):
                with st.spinner("Processando arquivos..."):
                    results = st.session_state.file_manager.process_multiple_files(uploaded_files)
                    
                    if results:
                        st.success(f"{len(results)} arquivos processados e adicionados à base de conhecimento!")
                        st.balloons()
    
    # Aba de gerenciamento
    with tab2:
        st.header("Gerenciar Base de Conhecimento")
        
        # Exibir lista de documentos
        display_document_list()
    
    # Aba de consulta
    with tab3:
        st.header("Consulta à Base de Conhecimento")
        
        documents = st.session_state.knowledge_base.get_all_documents()
        
        if not documents:
            st.warning("A base de conhecimento está vazia. Adicione documentos na aba 'Upload de Documentos'.")
        else:
            # Seção de filtros
            with st.expander("Filtrar documentos para consulta", expanded=True):
                st.markdown("Selecione os documentos que deseja incluir na consulta:")
                
                # Opção para selecionar todos
                all_selected = st.checkbox("Selecionar todos", value=True)
                
                # Lista de documentos com checkboxes
                selected_docs = []
                
                if all_selected:
                    selected_docs = list(documents.keys())
                else:
                    for doc_id, doc_info in documents.items():
                        if st.checkbox(f"{doc_info['name']}", value=False, key=f"filter_{doc_id}"):
                            selected_docs.append(doc_id)
                
                st.session_state.selected_docs = selected_docs
            
            # Exibir número de documentos selecionados
            if selected_docs:
                st.info(f"{len(selected_docs)} documentos selecionados para consulta")
            else:
                st.warning("Nenhum documento selecionado. A consulta não retornará resultados.")
            
            # Campo de consulta
            query = st.text_input("Digite sua pergunta")
            
            if query:
                if not selected_docs:
                    st.error("Selecione pelo menos um documento para consulta.")
                else:
                    with st.spinner("Gerando resposta..."):
                        response_data = generate_answer(query, filter_docs=selected_docs)
                        
                        if response_data:
                            st.markdown("### Resposta:")
                            st.markdown(response_data["response"])
                            
                            with st.expander("Ver fontes"):
                                for i, source in enumerate(response_data["sources"]):
                                    # Acesso seguro aos metadados
                                    doc_name = "Desconhecido"
                                    if isinstance(source, dict):
                                        # Verificar se metadata existe e é um dicionário
                                        if "metadata" in source and isinstance(source["metadata"], dict):
                                            doc_name = source["metadata"].get("doc_name", "Desconhecido")
                                        # Caso alternativo: verificar se doc_name está diretamente no source
                                        elif "doc_name" in source:
                                            doc_name = source["doc_name"]
                                    
                                    # Acesso seguro ao score
                                    score = 0.0
                                    if isinstance(source, dict) and "score" in source:
                                        score = source["score"]
                                    
                                    st.markdown(f"**Trecho {i+1}:** De '{doc_name}' (Score: {score:.4f})")
                                    
                                    # Acesso seguro ao conteúdo
                                    content = ""
                                    if isinstance(source, dict) and "content" in source:
                                        content = source["content"]
                                    
                                    if content:
                                        st.markdown(f"*{content[:200]}...*")
    
    # Aba de histórico
    with tab4:
        st.header("Histórico de Consultas")
        
        if not st.session_state.history:
            st.info("Nenhuma consulta realizada ainda.")
        else:
            for i, item in enumerate(reversed(st.session_state.history)):
                with st.expander(f"Consulta {len(st.session_state.history) - i}: {item['query']}"):
                    st.markdown(f"**Data:** {item['timestamp'][:16].replace('T', ' às ')}")
                    
                    # Mostrar documentos filtrados, se houver
                    if item.get('filter_docs'):
                        doc_names = []
                        for doc_id in item['filter_docs']:
                            docs = st.session_state.knowledge_base.get_all_documents()
                            if doc_id in docs:
                                doc_names.append(docs[doc_id]['name'])
                        
                        if doc_names:
                            st.markdown(f"**Documentos consultados:** {', '.join(doc_names)}")
                    
                    st.markdown("### Resposta:")
                    st.markdown(item["response"])
                    
                    st.markdown("### Fontes:")
                    for j, source in enumerate(item.get("sources", [])):
                        # Acesso seguro aos dados da fonte no histórico
                        title = "Desconhecido"
                        score = 0.0
                        
                        if isinstance(source, dict):
                            if "title" in source:
                                title = source["title"]
                            if "score" in source:
                                score = source["score"]
                        
                        st.markdown(f"**Trecho {j+1}:** {title} (Score: {score:.4f})")
    
    # Rodapé
    st.markdown("""
    <div class="footer">
        <p>Base de Conhecimento RAG com LangChain, FAISS e OpenAI | Desenvolvido com Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
