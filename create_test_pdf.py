import os
import tempfile
import logging
from datetime import datetime

# Criar um arquivo PDF simples para testes
def create_test_pdf():
    try:
        import fitz  # PyMuPDF
        
        # Criar um novo documento PDF
        doc = fitz.open()
        page = doc.new_page()
        
        # Adicionar texto ao PDF
        text = """
        # Documento de Teste para Aplicação RAG
        
        ## Introdução
        
        Este é um documento de teste para a aplicação RAG (Retrieval-Augmented Generation) 
        que utiliza LangChain, FAISS, OpenAI e Streamlit.
        
        ## Sobre LangChain
        
        LangChain é uma biblioteca para construir aplicações com modelos de linguagem. 
        Ela permite criar aplicações RAG de forma eficiente, conectando modelos de linguagem 
        a outras fontes de dados e permitindo interações mais complexas.
        
        ## Sobre FAISS
        
        FAISS (Facebook AI Similarity Search) é uma biblioteca para busca eficiente de vetores similares. 
        É frequentemente usada em aplicações RAG para indexar e recuperar embeddings de forma rápida e eficiente.
        
        ## Sobre OpenAI
        
        A OpenAI desenvolveu modelos de linguagem como GPT-4 que podem ser usados para gerar 
        respostas baseadas em contexto. Esses modelos são fundamentais para aplicações RAG.
        
        ## Sobre Streamlit
        
        Streamlit é uma biblioteca Python que facilita a criação de aplicações web interativas. 
        É ideal para criar interfaces para aplicações de machine learning e processamento de dados.
        """
        
        # Inserir texto na página
        rect = fitz.Rect(50, 50, 550, 800)
        page.insert_text(rect.tl, text, fontsize=11)
        
        # Salvar o PDF
        doc.save("test.pdf")
        doc.close()
        
        print("Arquivo PDF de teste criado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao criar arquivo PDF de teste: {str(e)}")
        return False

if __name__ == "__main__":
    create_test_pdf()
