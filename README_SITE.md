# Aplicação RAG como Site Web Permanente

Este documento descreve a versão web da aplicação RAG com LangChain, FAISS, OpenAI e Streamlit, adaptada para implantação como um site permanente.

## Visão Geral da Interface

A aplicação possui uma interface moderna e responsiva com as seguintes características:

### Layout Geral
- Título principal "📚 Aplicação RAG com LangChain, FAISS e OpenAI" no topo
- Layout amplo para melhor aproveitamento do espaço da tela
- CSS personalizado para melhorar a aparência visual (cores, espaçamentos, bordas arredondadas)
- Rodapé informativo na parte inferior

### Barra Lateral (Sidebar)
- Seção de configurações com campo para inserir a chave da API OpenAI
- Seção de informações que mostra detalhes sobre o documento processado
- Botão para limpar a sessão e reiniciar a aplicação

### Sistema de Abas
- **Aba "Upload de Documento"**: Interface para fazer upload de arquivos PDF com botão de processamento
- **Aba "Consulta"**: Campo para digitar perguntas sobre o documento e visualizar respostas
- **Aba "Histórico"**: Registro de todas as consultas anteriores e suas respostas

### Elementos Visuais Aprimorados
- Notificações visuais (success, info, warning, error) para feedback ao usuário
- Animação de balões quando um documento é processado com sucesso
- Expansores (expanders) para mostrar/ocultar informações detalhadas como fontes
- Indicadores de carregamento (spinners) durante operações demoradas

### Funcionalidades Adicionais
- Sistema de histórico para manter registro de todas as consultas e respostas
- Exibição das fontes utilizadas para gerar cada resposta
- Gerenciamento de sessão aprimorado para persistência de dados

## Arquivos para Implantação Web

### Aplicação Principal
- `app_deploy.py`: Versão aprimorada da aplicação Streamlit com melhorias para web

### Configurações de Implantação
- `Dockerfile`: Configuração para containerização da aplicação
- `docker-compose.yml`: Configuração para orquestração de serviços
- `.streamlit/config.toml`: Configurações do Streamlit para implantação
- `.env.example`: Modelo para configuração de variáveis de ambiente

### Documentação
- `DEPLOYMENT.md`: Guia detalhado para implantação em diferentes ambientes

## Opções de Implantação

A aplicação pode ser implantada de várias formas:

1. **Streamlit Cloud** (recomendado para facilidade)
   - Hospedagem gratuita para aplicações Streamlit
   - Implantação direta a partir de repositório GitHub

2. **Docker** (recomendado para ambientes personalizados)
   - Implantação usando o Dockerfile e docker-compose.yml fornecidos
   - Configuração através de variáveis de ambiente

3. **Serviços de Hospedagem**
   - Heroku, AWS Elastic Beanstalk, Google Cloud Run, Digital Ocean App Platform
   - Instruções detalhadas disponíveis no arquivo DEPLOYMENT.md

## Considerações para Implantação Permanente

- Configure a variável de ambiente `OPENAI_API_KEY` para sua chave API da OpenAI
- Utilize HTTPS para conexões seguras
- Considere adicionar autenticação para controle de acesso
- Monitore o uso da API OpenAI para controlar custos
- Faça backup regular dos índices FAISS
- Atualize as dependências regularmente para segurança

## Diferenças em Relação à Versão Original

A versão web da aplicação inclui várias melhorias em relação à versão original:

1. **Interface aprimorada** com CSS personalizado e melhor organização visual
2. **Sistema de histórico** para consultas e respostas
3. **Gerenciamento de sessão** mais robusto
4. **Configurações para implantação** em diversos ambientes
5. **Documentação detalhada** para implantação permanente
