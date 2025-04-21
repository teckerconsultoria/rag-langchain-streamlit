import os
import tempfile
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

import streamlit as st

from pdf_processor import extract_text_from_pdf, chunk_pdf_text

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileManager:
    """
    Classe para gerenciar o upload e processamento de múltiplos arquivos PDF.
    """
    
    def __init__(self, knowledge_base):
        """
        Inicializa o gerenciador de arquivos.
        
        Args:
            knowledge_base: Instância da classe KnowledgeBase para armazenar os documentos processados
        """
        self.knowledge_base = knowledge_base
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"FileManager inicializado com diretório temporário: {self.temp_dir}")
    
    def process_file(self, file, display_progress=True) -> Optional[str]:
        """
        Processa um único arquivo PDF e adiciona à base de conhecimento.
        
        Args:
            file: Objeto de arquivo do Streamlit
            display_progress: Se True, exibe barras de progresso no Streamlit
            
        Returns:
            ID do documento adicionado ou None se ocorrer um erro
        """
        try:
            file_name = file.name
            
            # Exibir progresso
            if display_progress:
                progress_text = st.empty()
                progress_bar = st.progress(0)
                progress_text.text(f"Processando arquivo: {file_name}")
                progress_bar.progress(10)
            
            # Salvar o arquivo temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=self.temp_dir) as tmp_file:
                tmp_file.write(file.getvalue())
                tmp_path = tmp_file.name
            
            if display_progress:
                progress_bar.progress(30)
                progress_text.text(f"Extraindo texto de: {file_name}")
            
            # Extrair texto do PDF
            logger.info(f"Processando PDF: {file_name}")
            text = extract_text_from_pdf(tmp_path)
            
            if not text:
                if display_progress:
                    progress_text.error(f"Não foi possível extrair texto de: {file_name}")
                    progress_bar.empty()
                logger.error(f"Não foi possível extrair texto de: {file_name}")
                return None
            
            if display_progress:
                progress_bar.progress(50)
                progress_text.text(f"Dividindo texto em chunks: {file_name}")
            
            # Dividir texto em chunks
            chunks = chunk_pdf_text(text)
            
            if display_progress:
                progress_bar.progress(70)
                progress_text.text(f"Adicionando documento à base de conhecimento: {file_name}")
            
            # Adicionar à base de conhecimento
            doc_id = self.knowledge_base.add_document(file_name, chunks)
            
            # Remover arquivo temporário
            os.unlink(tmp_path)
            
            if display_progress:
                progress_bar.progress(100)
                progress_text.text(f"Documento processado com sucesso: {file_name}")
                # Limpar após alguns segundos
                import time
                time.sleep(1)
                progress_text.empty()
                progress_bar.empty()
            
            logger.info(f"Arquivo {file_name} processado e adicionado à base de conhecimento com ID: {doc_id}")
            return doc_id
        
        except Exception as e:
            if display_progress:
                st.error(f"Erro ao processar arquivo {file.name}: {str(e)}")
            logger.error(f"Erro ao processar arquivo {file.name}: {str(e)}")
            return None
    
    def process_multiple_files(self, files) -> Dict[str, str]:
        """
        Processa múltiplos arquivos PDF e adiciona à base de conhecimento.
        
        Args:
            files: Lista de objetos de arquivo do Streamlit
            
        Returns:
            Dicionário mapeando nomes de arquivos para IDs de documentos
        """
        results = {}
        
        if not files:
            logger.warning("Nenhum arquivo fornecido para processamento")
            return results
        
        # Criar um container para exibir o progresso
        progress_container = st.container()
        
        with progress_container:
            st.write(f"Processando {len(files)} arquivos...")
            overall_progress = st.progress(0)
            file_progress = st.empty()
            
            for i, file in enumerate(files):
                file_name = file.name
                file_progress.text(f"Processando arquivo {i+1}/{len(files)}: {file_name}")
                
                # Processar o arquivo sem exibir progresso individual (para evitar poluição visual)
                doc_id = self.process_file(file, display_progress=False)
                
                if doc_id:
                    results[file_name] = doc_id
                    st.success(f"✅ {file_name} processado com sucesso")
                else:
                    st.error(f"❌ Erro ao processar {file_name}")
                
                # Atualizar progresso geral
                overall_progress.progress((i + 1) / len(files))
            
            # Limpar progresso individual ao finalizar
            file_progress.empty()
            
            # Mostrar resumo
            if results:
                st.success(f"{len(results)} de {len(files)} arquivos processados com sucesso")
            else:
                st.error("Nenhum arquivo foi processado com sucesso")
        
        return results
    
    def cleanup(self):
        """Limpa arquivos temporários."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info(f"Diretório temporário removido: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Erro ao limpar diretório temporário: {str(e)}")
