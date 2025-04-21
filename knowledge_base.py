import os
import logging
from typing import List, Dict, Any, Optional
import pickle
import uuid
from datetime import datetime

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeBase:
    """
    Classe para gerenciar uma base de conhecimento com múltiplos documentos usando FAISS e embeddings da OpenAI.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, kb_path: str = "knowledge_base"):
        """
        Inicializa a base de conhecimento.
        
        Args:
            openai_api_key: Chave de API da OpenAI (opcional, pode ser definida como variável de ambiente)
            kb_path: Caminho para armazenar a base de conhecimento
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("Chave de API da OpenAI não fornecida. Defina OPENAI_API_KEY como variável de ambiente.")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=self.openai_api_key
        )
        
        self.kb_path = kb_path
        os.makedirs(self.kb_path, exist_ok=True)
        
        self.vector_store = None
        self.documents = {}  # Dicionário para rastrear documentos adicionados
        self.metadata_path = os.path.join(self.kb_path, "metadata.pkl")
        
        # Carregar metadados existentes, se houver
        self._load_metadata()
        
        # Carregar o índice FAISS existente, se houver
        self._load_index()
        
        logger.info("KnowledgeBase inicializada com modelo text-embedding-3-small")
    
    def _load_metadata(self):
        """Carrega os metadados da base de conhecimento do disco."""
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'rb') as f:
                    self.documents = pickle.load(f)
                logger.info(f"Metadados carregados: {len(self.documents)} documentos encontrados")
            except Exception as e:
                logger.error(f"Erro ao carregar metadados: {str(e)}")
                self.documents = {}
    
    def _save_metadata(self):
        """Salva os metadados da base de conhecimento no disco."""
        try:
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.documents, f)
            logger.info(f"Metadados salvos: {len(self.documents)} documentos")
        except Exception as e:
            logger.error(f"Erro ao salvar metadados: {str(e)}")
    
    def _load_index(self):
        """Carrega o índice FAISS do disco."""
        index_path = os.path.join(self.kb_path, "index")
        if os.path.exists(index_path):
            try:
                self.vector_store = FAISS.load_local(
                    folder_path=index_path,
                    embeddings=self.embeddings
                )
                logger.info(f"Índice FAISS carregado de: {index_path}")
            except Exception as e:
                logger.error(f"Erro ao carregar índice FAISS: {str(e)}")
                self.vector_store = None
    
    def _save_index(self):
        """Salva o índice FAISS no disco."""
        if not self.vector_store:
            logger.warning("Nenhum índice FAISS para salvar")
            return False
        
        try:
            index_path = os.path.join(self.kb_path, "index")
            self.vector_store.save_local(index_path)
            logger.info(f"Índice FAISS salvo em: {index_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar índice FAISS: {str(e)}")
            return False
    
    def add_document(self, doc_name: str, chunks_with_metadata: List[Dict[str, Any]]) -> str:
        """
        Adiciona um documento à base de conhecimento.
        
        Args:
            doc_name: Nome do documento
            chunks_with_metadata: Lista de dicionários contendo chunks com metadados
            
        Returns:
            ID do documento adicionado
        """
        if not chunks_with_metadata:
            logger.warning(f"Nenhum chunk fornecido para o documento: {doc_name}")
            return None
        
        # Gerar ID único para o documento
        doc_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Adicionar informações do documento ao registro
        self.documents[doc_id] = {
            "name": doc_name,
            "added_at": timestamp,
            "chunk_count": len(chunks_with_metadata)
        }
        
        # Adicionar ID do documento aos metadados de cada chunk
        for chunk in chunks_with_metadata:
            chunk["doc_id"] = doc_id
            chunk["doc_name"] = doc_name
        
        # Extrair textos e metadados
        texts = [chunk["content"] for chunk in chunks_with_metadata]
        metadatas = [
            {
                "chunk_id": chunk["chunk_id"],
                "title": chunk["title"],
                "token_count": chunk["token_count"],
                "doc_id": chunk["doc_id"],
                "doc_name": chunk["doc_name"]
            } 
            for chunk in chunks_with_metadata
        ]
        
        try:
            # Se já existe um índice, adicionar a ele
            if self.vector_store:
                self.vector_store.add_texts(texts=texts, metadatas=metadatas)
                logger.info(f"Adicionado documento '{doc_name}' ao índice existente")
            # Caso contrário, criar um novo índice
            else:
                self.vector_store = FAISS.from_texts(
                    texts=texts,
                    embedding=self.embeddings,
                    metadatas=metadatas
                )
                logger.info(f"Criado novo índice com documento '{doc_name}'")
            
            # Salvar o índice e os metadados
            self._save_index()
            self._save_metadata()
            
            logger.info(f"Documento '{doc_name}' adicionado à base de conhecimento com ID: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Erro ao adicionar documento à base de conhecimento: {str(e)}")
            return None
    
    def remove_document(self, doc_id: str) -> bool:
        """
        Remove um documento da base de conhecimento.
        
        Args:
            doc_id: ID do documento a ser removido
            
        Returns:
            True se o documento foi removido com sucesso, False caso contrário
        """
        if doc_id not in self.documents:
            logger.warning(f"Documento com ID {doc_id} não encontrado")
            return False
        
        try:
            # Remover o documento do registro
            doc_name = self.documents[doc_id]["name"]
            del self.documents[doc_id]
            
            # Reconstruir o índice FAISS sem o documento removido
            # Nota: FAISS não suporta remoção direta, então precisamos reconstruir o índice
            self._rebuild_index()
            
            logger.info(f"Documento '{doc_name}' (ID: {doc_id}) removido da base de conhecimento")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover documento: {str(e)}")
            return False
    
    def _rebuild_index(self):
        """Reconstrói o índice FAISS com base nos documentos atuais."""
        # Esta é uma implementação simplificada
        # Em uma aplicação real, você precisaria armazenar os chunks originais
        # ou implementar uma estratégia mais eficiente
        
        # Por enquanto, apenas salvamos os metadados
        self._save_metadata()
        logger.warning("Reconstrução do índice não implementada completamente")
        
        # Em uma implementação completa, você faria algo como:
        # 1. Consultar todos os chunks de documentos restantes
        # 2. Criar um novo índice FAISS com esses chunks
        # 3. Salvar o novo índice
    
    def get_all_documents(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna informações sobre todos os documentos na base de conhecimento.
        
        Returns:
            Dicionário com informações sobre os documentos
        """
        return self.documents
    
    def similarity_search(self, query: str, k: int = 3, filter_doc_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Realiza uma busca por similaridade na base de conhecimento.
        
        Args:
            query: Consulta para buscar
            k: Número de resultados a retornar
            filter_doc_ids: Lista opcional de IDs de documentos para filtrar a busca
            
        Returns:
            Lista de documentos similares com seus metadados
        """
        if not self.vector_store:
            logger.warning("Nenhum índice FAISS para buscar")
            return []
        
        try:
            logger.info(f"Realizando busca por similaridade para: '{query}' (k={k})")
            
            # Se houver filtro de documentos, aplicá-lo
            if filter_doc_ids:
                # Implementação simplificada - em uma aplicação real,
                # você usaria o mecanismo de filtragem do FAISS
                results = self.vector_store.similarity_search_with_score(query, k=k*2)  # Buscar mais resultados para filtrar depois
                
                # Filtrar resultados
                filtered_results = []
                for doc, score in results:
                    if doc.metadata.get("doc_id") in filter_doc_ids:
                        filtered_results.append((doc, score))
                
                # Limitar ao número k
                results = filtered_results[:k]
            else:
                results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Formatar resultados
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                    "doc_name": doc.metadata.get("doc_name", "Desconhecido")
                })
            
            logger.info(f"Busca concluída. {len(formatted_results)} resultados encontrados")
            return formatted_results
        except Exception as e:
            logger.error(f"Erro na busca por similaridade: {str(e)}")
            return []
