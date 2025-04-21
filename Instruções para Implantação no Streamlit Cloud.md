# Instruções para Implantação no Streamlit Cloud

Este documento fornece instruções detalhadas para implantar a aplicação RAG no Streamlit Cloud, resolvendo o erro de importação do PyMuPDF.

## Arquivos Necessários

Certifique-se de que os seguintes arquivos estejam presentes no seu repositório:

1. `app_deploy.py` - Arquivo principal da aplicação Streamlit
2. `pdf_processor.py` - Módulo para processamento de PDF
3. `vector_store.py` - Módulo para armazenamento vetorial com FAISS
4. `response_generator.py` - Módulo para geração de respostas com OpenAI
5. `requirements.txt` - Lista de dependências Python (atualizada)
6. `packages.txt` - Lista de dependências do sistema para o PyMuPDF

## Passos para Implantação

### 1. Prepare seu Repositório GitHub

1. Crie um repositório no GitHub (se ainda não tiver um)
2. Faça upload de todos os arquivos da aplicação, incluindo:
   - Todos os arquivos Python (.py)
   - O arquivo `requirements.txt` atualizado
   - O arquivo `packages.txt` recém-criado

### 2. Configure a Implantação no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io/)
2. Faça login com sua conta (crie uma se necessário)
3. Clique em "New app"
4. Selecione seu repositório GitHub
5. Configure as seguintes opções:
   - **Repository**: Seu repositório GitHub
   - **Branch**: main (ou a branch que contém seu código)
   - **Main file path**: `app_deploy.py`
   - **Advanced settings**:
     - Adicione a variável de ambiente `OPENAI_API_KEY` com sua chave da API OpenAI

### 3. Implante a Aplicação

1. Clique em "Deploy"
2. Aguarde a conclusão do processo de implantação
   - O Streamlit Cloud detectará automaticamente o arquivo `packages.txt` e instalará as dependências do sistema
   - Em seguida, instalará as dependências Python listadas em `requirements.txt`

### 4. Verifique a Implantação

1. Após a conclusão da implantação, acesse a URL fornecida pelo Streamlit Cloud
2. Verifique se a aplicação está funcionando corretamente:
   - Teste o upload de um PDF
   - Teste a consulta ao documento

## Solução de Problemas

Se ainda encontrar problemas após seguir estas instruções:

1. **Verifique os logs de implantação** no Streamlit Cloud para identificar erros específicos
2. **Verifique as versões das dependências** em `requirements.txt` para garantir compatibilidade
3. **Certifique-se de que o arquivo `packages.txt`** está na raiz do repositório
4. **Verifique se a variável de ambiente `OPENAI_API_KEY`** está configurada corretamente

## Notas Importantes

- O Streamlit Cloud tem um limite de tamanho para arquivos de upload (200MB)
- A aplicação ficará inativa após um período sem uso, mas será reiniciada automaticamente quando acessada
- Considere configurar um arquivo `.streamlit/config.toml` para personalizar a aparência da aplicação
