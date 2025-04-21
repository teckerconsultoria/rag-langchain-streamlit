import os
import logging
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Classe para gerar respostas usando o modelo GPT-4 da OpenAI com base em chunks recuperados.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Inicializa o gerador de respostas.
        
        Args:
            openai_api_key: Chave de API da OpenAI (opcional, pode ser definida como variável de ambiente)
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("Chave de API da OpenAI não fornecida. Defina OPENAI_API_KEY como variável de ambiente.")
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            openai_api_key=self.openai_api_key
        )
        logger.info("ResponseGenerator inicializado com modelo GPT-4")
    
    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera uma resposta com base na consulta e nos chunks de contexto recuperados.
        
        Args:
            query: Consulta do usuário
            context_chunks: Lista de chunks de contexto recuperados
            
        Returns:
            Dicionário contendo a resposta gerada e informações sobre as fontes
        """
        if not context_chunks:
            logger.warning("Nenhum chunk de contexto fornecido para gerar resposta")
            return {
                "response": "Não foi possível gerar uma resposta, pois não há informações relevantes disponíveis.",
                "sources": []
            }
        
        logger.info(f"Gerando resposta para: '{query}' com {len(context_chunks)} chunks de contexto")
        
        # Preparar o contexto a partir dos chunks
        context_text = ""
        sources = []
        
        for i, chunk in enumerate(context_chunks):
            # Adicionar o conteúdo do chunk ao contexto
            chunk_text = chunk["content"]
            context_text += f"\n\nTrecho {i+1}:\n{chunk_text}"
            
            # Adicionar informações sobre a fonte
            sources.append({
                "chunk_id": chunk["metadata"]["chunk_id"],
                "title": chunk["metadata"]["title"],
                "score": chunk["score"] if "score" in chunk else None
            })
        
        # Criar o template do prompt
        template = """
        Você é um assistente de IA especializado em responder perguntas com base em informações fornecidas.
        
        Responda à pergunta do usuário usando apenas as informações contidas nos trechos de contexto abaixo.
        Se a informação não estiver presente nos trechos, indique que não há informações suficientes para responder.
        Não use conhecimentos externos além dos trechos fornecidos.
        
        Contexto:
        {context}
        
        Pergunta: {query}
        
        Responda de forma clara, concisa e informativa. Cite os trechos específicos que você usou para formular sua resposta.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Preparar os parâmetros para o prompt
        prompt_params = {
            "context": context_text,
            "query": query
        }
        
        try:
            # Gerar a resposta
            chain = prompt | self.llm
            response = chain.invoke(prompt_params)
            response_text = response.content
            
            logger.info("Resposta gerada com sucesso")
            
            return {
                "response": response_text,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {str(e)}")
            return {
                "response": f"Ocorreu um erro ao gerar a resposta: {str(e)}",
                "sources": sources
            }
