import fitz  # PyMuPDF
import os
import logging
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrai texto de um arquivo PDF usando PyMuPDF.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        
    Returns:
        Texto extraído do PDF
    """
    logger.info(f"Extraindo texto do PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        logger.error(f"Arquivo não encontrado: {pdf_path}")
        return ""
    
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc):
                logger.info(f"Processando página {page_num + 1}/{len(doc)}")
                text += page.get_text()
        
        logger.info(f"Extração concluída. Total de caracteres: {len(text)}")
        return text
    except Exception as e:
        logger.error(f"Erro ao extrair texto do PDF: {str(e)}")
        return ""

def num_tokens_from_string(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Retorna o número de tokens em uma string.
    
    Args:
        text: Texto para contar tokens
        encoding_name: Nome do encoding a ser usado
        
    Returns:
        Número de tokens
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens

def chunk_pdf_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Divide o texto em chunks com metadados.
    
    Args:
        text: Texto completo do PDF
        chunk_size: Tamanho aproximado de cada chunk em tokens
        chunk_overlap: Sobreposição entre chunks em tokens
        
    Returns:
        Lista de dicionários contendo chunks com metadados
    """
    logger.info(f"Dividindo texto em chunks. Tamanho alvo: {chunk_size} tokens, Sobreposição: {chunk_overlap} tokens")
    
    if not text:
        logger.warning("Texto vazio, nenhum chunk gerado")
        return []
    
    # Usar o RecursiveCharacterTextSplitter para dividir o texto
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=lambda text: num_tokens_from_string(text),
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Dividir o texto em chunks
    chunks = text_splitter.split_text(text)
    
    # Adicionar metadados aos chunks
    chunks_with_metadata = []
    for i, chunk_text in enumerate(chunks):
        chunk_data = {
            "chunk_id": i,
            "title": f"Chunk {i+1}",
            "content": chunk_text,
            "token_count": num_tokens_from_string(chunk_text)
        }
        chunks_with_metadata.append(chunk_data)
    
    logger.info(f"Gerados {len(chunks_with_metadata)} chunks")
    
    # Registrar estatísticas dos chunks
    if chunks_with_metadata:
        token_counts = [chunk["token_count"] for chunk in chunks_with_metadata]
        avg_tokens = sum(token_counts) / len(token_counts)
        logger.info(f"Estatísticas dos chunks - Média de tokens: {avg_tokens:.2f}, "
                   f"Mín: {min(token_counts)}, Máx: {max(token_counts)}")
    
    return chunks_with_metadata
