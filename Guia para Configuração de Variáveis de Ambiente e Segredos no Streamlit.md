# Guia para Configuração de Variáveis de Ambiente e Segredos no Streamlit

Este documento explica como configurar variáveis de ambiente e outros segredos para sua aplicação Streamlit usando o formato TOML, garantindo que informações sensíveis sejam gerenciadas de forma segura.

## 1. Configuração Local (Desenvolvimento)

### Criando o arquivo secrets.toml

1. Crie um diretório `.streamlit` na raiz do seu projeto:
   ```bash
   mkdir -p .streamlit
   ```

2. Dentro deste diretório, crie um arquivo chamado `secrets.toml`:
   ```bash
   touch .streamlit/secrets.toml
   ```

3. Edite o arquivo `secrets.toml` e adicione suas variáveis de ambiente e segredos:
   ```toml
   # Chave da API OpenAI
   openai_api_key = "sua_chave_api_aqui"
   
   # Configurações de banco de dados (se necessário)
   [database]
   username = "usuario_db"
   password = "senha_segura_db"
   host = "localhost"
   port = 5432
   database = "nome_do_banco"
   
   # Outras configurações (se necessário)
   [aws]
   access_key = "sua_access_key_aws"
   secret_key = "sua_secret_key_aws"
   ```

4. **IMPORTANTE**: Adicione `.streamlit/secrets.toml` ao seu arquivo `.gitignore` para evitar que segredos sejam enviados ao repositório:
   ```bash
   echo ".streamlit/secrets.toml" >> .gitignore
   ```

## 2. Acessando Segredos no Código

Para acessar os segredos em sua aplicação Streamlit:

```python
import streamlit as st

# Acessando um segredo de nível superior
api_key = st.secrets["openai_api_key"]

# Acessando segredos aninhados
db_username = st.secrets["database"]["username"]
db_password = st.secrets["database"]["password"]

# Verificando se um segredo existe
if "aws" in st.secrets:
    aws_access_key = st.secrets["aws"]["access_key"]
```

## 3. Configuração na Nuvem (Streamlit Cloud)

Ao implantar sua aplicação no Streamlit Cloud, você precisa configurar os segredos no painel de controle:

1. Faça login no [Streamlit Cloud](https://share.streamlit.io/)
2. Selecione sua aplicação
3. Clique em "Settings" (⚙️) > "Secrets"
4. Cole o conteúdo do seu arquivo `secrets.toml` na caixa de texto
5. Clique em "Save"

O Streamlit Cloud criptografa esses segredos e os disponibiliza para sua aplicação em tempo de execução de forma segura.

## 4. Boas Práticas

- **Nunca compartilhe** seu arquivo `secrets.toml` ou o inclua em repositórios públicos
- Crie um arquivo `secrets.toml.example` com valores fictícios para documentação
- Use nomes de variáveis descritivos para facilitar a manutenção
- Organize segredos relacionados em seções usando o formato TOML
- Considere usar diferentes segredos para ambientes de desenvolvimento e produção

## 5. Exemplo de Implementação

Aqui está um exemplo de como usar segredos em uma aplicação RAG:

```python
import streamlit as st
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Acessar a chave da API OpenAI dos segredos
api_key = st.secrets["openai_api_key"]

# Configurar os componentes com a chave da API
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=api_key
)

llm = ChatOpenAI(
    model=st.secrets["app_settings"]["model_name"],
    temperature=0.2,
    openai_api_key=api_key
)

# Usar os componentes na aplicação
# ...
```

## 6. Recursos Adicionais

- [Documentação oficial do Streamlit sobre segredos](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)
- [Formato TOML](https://toml.io/en/)
- [Melhores práticas de segurança para aplicações Streamlit](https://docs.streamlit.io/knowledge-base/deploy/best-practices-for-securing-your-streamlit-app)
