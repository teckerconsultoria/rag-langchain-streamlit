# Implantação da Aplicação RAG

Este documento contém instruções para implantar a aplicação RAG como um site permanente.

## Opções de Implantação

Existem várias opções para implantar a aplicação:

1. **Implantação com Streamlit Cloud** (recomendado para facilidade)
2. **Implantação com Docker** (recomendado para ambientes personalizados)
3. **Implantação em serviços de hospedagem** (para implantação permanente)

## 1. Implantação com Streamlit Cloud

A Streamlit Cloud é a maneira mais fácil de implantar aplicações Streamlit:

1. Crie uma conta em [share.streamlit.io](https://share.streamlit.io/)
2. Conecte sua conta GitHub
3. Faça upload do código para um repositório GitHub
4. Implante a aplicação diretamente do repositório

## 2. Implantação com Docker

Para implantar usando Docker:

```bash
# Clone o repositório (se estiver usando Git)
git clone <url-do-repositorio>
cd rag_app

# Crie um arquivo .env com sua chave API
cp .env.example .env
# Edite o arquivo .env e adicione sua chave API da OpenAI

# Construa e inicie os contêineres
docker-compose up -d
```

A aplicação estará disponível em http://localhost:8501

## 3. Implantação em Serviços de Hospedagem

Para implantação permanente, você pode usar:

- **Heroku**: Use o buildpack Python e configure a variável de ambiente OPENAI_API_KEY
- **AWS Elastic Beanstalk**: Faça upload do código com o Dockerfile
- **Google Cloud Run**: Implante usando o Dockerfile
- **Digital Ocean App Platform**: Conecte ao repositório GitHub

## Variáveis de Ambiente

Configure a seguinte variável de ambiente em qualquer plataforma:

- `OPENAI_API_KEY`: Sua chave API da OpenAI

## Considerações de Segurança

- Nunca compartilhe sua chave API da OpenAI
- Use variáveis de ambiente para armazenar chaves sensíveis
- Configure HTTPS para conexões seguras
- Considere adicionar autenticação para acesso à aplicação

## Manutenção

- Monitore o uso da API OpenAI para controlar custos
- Faça backup regular dos índices FAISS
- Atualize as dependências regularmente para segurança
