# Aplicação RAG com LangChain, FAISS, OpenAI e Streamlit

Este projeto implementa uma aplicação de Retrieval-Augmented Generation (RAG) utilizando LangChain, FAISS, OpenAI e Streamlit. A aplicação permite fazer upload de documentos PDF, extrair seu conteúdo, dividir em chunks, gerar embeddings, indexar com FAISS e realizar consultas usando o GPT-4.

## Funcionalidades

- Upload de arquivos PDF
- Extração de texto usando PyMuPDF
- Divisão do texto em chunks com metadados (chunk_id, title, content)
- Geração de embeddings usando o modelo text-embedding-3-small da OpenAI
- Indexação vetorial com FAISS
- Salvamento do índice FAISS no disco
- Interface de usuário com Streamlit
- Consultas ao documento usando GPT-4
- Exibição de respostas em formato Markdown com fontes

## Estrutura do Projeto

- `app.py`: Aplicação principal com interface Streamlit
- `pdf_processor.py`: Funções para processamento de PDF e divisão em chunks
- `vector_store.py`: Classe para gerenciar o armazenamento vetorial com FAISS
- `response_generator.py`: Classe para gerar respostas usando GPT-4
- `test_app.py`: Script para testar as funcionalidades da aplicação
- `create_test_pdf.py`: Script para criar um PDF de teste
- `requirements.txt`: Lista de dependências do projeto

## Requisitos

- Python 3.10+
- Dependências listadas em `requirements.txt`
- Chave de API da OpenAI

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure sua chave de API da OpenAI:

```bash
export OPENAI_API_KEY="sua_chave_api_openai"
```

## Uso

Execute a aplicação Streamlit:

```bash
streamlit run app.py
```

A aplicação será aberta no navegador e você poderá:

1. Inserir sua chave de API da OpenAI (se não estiver definida como variável de ambiente)
2. Fazer upload de um arquivo PDF
3. Processar o documento
4. Fazer perguntas sobre o conteúdo do documento

## Detalhes de Implementação

### Processamento de PDF

O módulo `pdf_processor.py` utiliza PyMuPDF para extrair texto de arquivos PDF e dividir o conteúdo em chunks de aproximadamente 500-1000 tokens, com sobreposição configurável. Cada chunk contém metadados como ID, título e contagem de tokens.

### Armazenamento Vetorial

O módulo `vector_store.py` implementa a classe `VectorStore` que gerencia a criação de embeddings usando o modelo text-embedding-3-small da OpenAI e a indexação com FAISS. A classe também fornece métodos para salvar e carregar o índice do disco, além de realizar buscas por similaridade.

### Geração de Respostas

O módulo `response_generator.py` implementa a classe `ResponseGenerator` que utiliza o modelo GPT-4 da OpenAI para gerar respostas com base nos chunks recuperados. A classe formata a resposta em Markdown e inclui informações sobre as fontes utilizadas.

### Interface Streamlit

A interface do usuário é implementada com Streamlit e inclui:
- Upload de arquivos PDF
- Processamento e indexação do documento
- Campo de consulta para fazer perguntas
- Exibição de respostas em formato Markdown com fontes

## Testes

O script `test_app.py` pode ser usado para testar as principais funcionalidades da aplicação:

```bash
python test_app.py
```

Para criar um PDF de teste para fins de desenvolvimento:

```bash
python create_test_pdf.py
```
