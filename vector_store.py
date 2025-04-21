import os
import logging
from typing import List, Dict, Any, Optional
import pickle

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorStore:
    """
    Classe para gerenciar o armazenamento vetorial com FAISS e embeddings da OpenAI.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Inicializa o armazenamento vetorial.
        
        Args:
            openai_api_key: Chave de API da OpenAI (opcional, pode ser definida como variável de ambiente)
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("Chave de API da OpenAI não fornecida. Defina OPENAI_API_KEY como variável de ambiente.")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=self.openai_api_key
        )
        self.vector_store = None
        logger.info("VectorStore inicializado com modelo text-embedding-3-small")
    
    def create_vector_store(self, chunks_with_metadata: List[Dict[str, Any]]) -> None:
        """
        Cria um armazenamento vetorial a partir de chunks com metadados.
        
        Args:
            chunks_with_metadata: Lista de dicionários contendo chunks com metadados
        """
        if not chunks_with_metadata:
            logger.warning("Nenhum chunk fornecido para criar o armazenamento vetorial")
            return
        
        logger.info(f"Criando armazenamento vetorial com {len(chunks_with_metadata)} chunks")
        
        # Extrair textos e metadados
        texts = [chunk["content"] for chunk in chunks_with_metadata]
        metadatas = [
            {
                "chunk_id": chunk["chunk_id"],
                "title": chunk["title"],
                "token_count": chunk["token_count"]
            } 
            for chunk in chunks_with_metadata
        ]
        
        # Criar armazenamento FAISS
        try:
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
            logger.info("Armazenamento vetorial FAISS criado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar armazenamento vetorial: {str(e)}")
            raise
    
    def save_vector_store(self, file_path: str) -> bool:
        """
        Salva o armazenamento vetorial no disco.
        
        Args:
            file_path: Caminho para salvar o armazenamento vetorial
            
        Returns:
            True se o armazenamento foi salvo com sucesso, False caso contrário
        """
        if not self.vector_store:
            logger.warning("Nenhum armazenamento vetorial para salvar")
            return False
        
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Salvar o armazenamento vetorial
            self.vector_store.save_local(file_path)
            logger.info(f"Armazenamento vetorial salvo em: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar armazenamento vetorial: {str(e)}")
            return False
    
    def load_vector_store(self, file_path: str) -> bool:
        """
        Carrega o armazenamento vetorial do disco.
        
        Args:
            file_path: Caminho para carregar o armazenamento vetorial
            
        Returns:
            True se o armazenamento foi carregado com sucesso, False caso contrário
        """
        if not os.path.exists(file_path):
            logger.warning(f"Arquivo não encontrado: {file_path}")
            return False
        
        try:
            self.vector_store = FAISS.load_local(
                folder_path=file_path,
                embeddings=self.embeddings
            )
            logger.info(f"Armazenamento vetorial carregado de: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar armazenamento vetorial: {str(e)}")
            return False
    
    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Realiza uma busca por similaridade no armazenamento vetorial.
        
        Args:
            query: Consulta para buscar
            k: Número de resultados a retornar
            
        Returns:
            Lista de documentos similares com seus metadados
        """
        if not self.vector_store:
            logger.warning("Nenhum armazenamento vetorial para buscar")
            return []
        
        try:
            logger.info(f"Realizando busca por similaridade para: '{query}' (k={k})")
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Formatar resultados
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            logger.info(f"Busca concluída. {len(formatted_results)} resultados encontrados")
            return formatted_results
        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {str(e)}")
            return []
