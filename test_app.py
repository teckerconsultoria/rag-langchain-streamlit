import os
import sys
import logging
from pdf_processor import extract_text_from_pdf, chunk_pdf_text
from vector_store import VectorStore
from response_generator import ResponseGenerator

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pdf_processing():
    """
    Testa as funções de processamento de PDF.
    """
    logger.info("=== Teste de Processamento de PDF ===")
    
    # Verificar se existe um PDF de teste
    pdf_path = "test.pdf"
    if not os.path.exists(pdf_path):
        logger.warning(f"Arquivo de teste {pdf_path} não encontrado. Pulando teste de processamento de PDF.")
        return False
    
    # Extrair texto do PDF
    logger.info(f"Extraindo texto de {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        logger.error("Falha ao extrair texto do PDF.")
        return False
    
    logger.info(f"Texto extraído com sucesso. Tamanho: {len(text)} caracteres")
    
    # Dividir texto em chunks
    logger.info("Dividindo texto em chunks")
    chunks = chunk_pdf_text(text)
    
    if not chunks:
        logger.error("Falha ao dividir texto em chunks.")
        return False
    
    logger.info(f"Texto dividido em {len(chunks)} chunks")
    
    # Exibir informações sobre os chunks
    for i, chunk in enumerate(chunks[:2]):  # Mostrar apenas os 2 primeiros chunks
        logger.info(f"Chunk {i+1}/{len(chunks)}:")
        logger.info(f"  ID: {chunk['chunk_id']}")
        logger.info(f"  Título: {chunk['title']}")
        logger.info(f"  Tokens: {chunk['token_count']}")
        logger.info(f"  Conteúdo (primeiros 100 caracteres): {chunk['content'][:100]}...")
    
    logger.info("Teste de processamento de PDF concluído com sucesso!")
    return True

def test_vector_store(chunks=None):
    """
    Testa o armazenamento vetorial com FAISS.
    """
    logger.info("=== Teste de Armazenamento Vetorial ===")
    
    # Verificar se há uma chave de API da OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.warning("Chave de API da OpenAI não encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
        return False
    
    # Criar chunks de teste se não fornecidos
    if not chunks:
        test_chunks = [
            {
                "chunk_id": 0,
                "title": "Chunk de Teste 1",
                "content": "Este é um texto de teste para o armazenamento vetorial FAISS.",
                "token_count": 15
            },
            {
                "chunk_id": 1,
                "title": "Chunk de Teste 2",
                "content": "LangChain é uma biblioteca para construir aplicações com modelos de linguagem.",
                "token_count": 16
            }
        ]
    else:
        test_chunks = chunks
    
    # Inicializar o armazenamento vetorial
    logger.info("Inicializando VectorStore")
    vector_store = VectorStore(openai_api_key=openai_api_key)
    
    # Criar o armazenamento vetorial
    logger.info("Criando armazenamento vetorial")
    try:
        vector_store.create_vector_store(test_chunks)
    except Exception as e:
        logger.error(f"Falha ao criar armazenamento vetorial: {str(e)}")
        return False
    
    # Salvar o armazenamento vetorial
    logger.info("Salvando armazenamento vetorial")
    index_path = "test_index"
    if not vector_store.save_vector_store(index_path):
        logger.error("Falha ao salvar armazenamento vetorial.")
        return False
    
    # Carregar o armazenamento vetorial
    logger.info("Carregando armazenamento vetorial")
    if not vector_store.load_vector_store(index_path):
        logger.error("Falha ao carregar armazenamento vetorial.")
        return False
    
    # Realizar uma busca por similaridade
    logger.info("Realizando busca por similaridade")
    query = "O que é LangChain?"
    results = vector_store.similarity_search(query)
    
    if not results:
        logger.error("Falha ao realizar busca por similaridade.")
        return False
    
    logger.info(f"Busca concluída. {len(results)} resultados encontrados")
    
    # Exibir resultados
    for i, result in enumerate(results):
        logger.info(f"Resultado {i+1}/{len(results)}:")
        logger.info(f"  Conteúdo: {result['content'][:100]}...")
        logger.info(f"  Score: {result['score']}")
    
    logger.info("Teste de armazenamento vetorial concluído com sucesso!")
    return True

def test_response_generation():
    """
    Testa a geração de respostas com OpenAI.
    """
    logger.info("=== Teste de Geração de Respostas ===")
    
    # Verificar se há uma chave de API da OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.warning("Chave de API da OpenAI não encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
        return False
    
    # Criar chunks de teste
    test_chunks = [
        {
            "content": "LangChain é uma biblioteca para construir aplicações com modelos de linguagem. Ela permite criar aplicações RAG (Retrieval-Augmented Generation) de forma eficiente.",
            "metadata": {
                "chunk_id": 0,
                "title": "Sobre LangChain",
                "token_count": 30
            },
            "score": 0.85
        },
        {
            "content": "FAISS (Facebook AI Similarity Search) é uma biblioteca para busca eficiente de vetores similares. É frequentemente usada em aplicações RAG para indexar e recuperar embeddings.",
            "metadata": {
                "chunk_id": 1,
                "title": "Sobre FAISS",
                "token_count": 32
            },
            "score": 0.75
        }
    ]
    
    # Inicializar o gerador de respostas
    logger.info("Inicializando ResponseGenerator")
    response_generator = ResponseGenerator(openai_api_key=openai_api_key)
    
    # Gerar uma resposta
    logger.info("Gerando resposta")
    query = "O que é LangChain e FAISS?"
    try:
        response_data = response_generator.generate_response(query, test_chunks)
    except Exception as e:
        logger.error(f"Falha ao gerar resposta: {str(e)}")
        return False
    
    if not response_data or "response" not in response_data:
        logger.error("Falha ao gerar resposta.")
        return False
    
    # Exibir resposta
    logger.info("Resposta gerada:")
    logger.info(response_data["response"])
    
    logger.info("Fontes:")
    for i, source in enumerate(response_data["sources"]):
        logger.info(f"  Fonte {i+1}: {source['title']} (ID: {source['chunk_id']}, Score: {source['score']})")
    
    logger.info("Teste de geração de respostas concluído com sucesso!")
    return True

def main():
    """
    Função principal para executar os testes.
    """
    logger.info("Iniciando testes da aplicação RAG")
    
    # Testar processamento de PDF
    pdf_success = test_pdf_processing()
    
    # Testar armazenamento vetorial
    vector_success = test_vector_store()
    
    # Testar geração de respostas
    response_success = test_response_generation()
    
    # Resumo dos testes
    logger.info("=== Resumo dos Testes ===")
    logger.info(f"Processamento de PDF: {'SUCESSO' if pdf_success else 'FALHA'}")
    logger.info(f"Armazenamento Vetorial: {'SUCESSO' if vector_success else 'FALHA'}")
    logger.info(f"Geração de Respostas: {'SUCESSO' if response_success else 'FALHA'}")
    
    if pdf_success and vector_success and response_success:
        logger.info("Todos os testes foram concluídos com sucesso!")
        return 0
    else:
        logger.warning("Alguns testes falharam. Verifique os logs para mais detalhes.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
