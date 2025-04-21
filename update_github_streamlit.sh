#!/bin/bash

# Script para criar uma nova branch no GitHub e preparar arquivos para o Streamlit Cloud
# Autor: Manus AI
# Data: 21 de abril de 2025

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Script de Atualização do Repositório GitHub e Streamlit Cloud ===${NC}"
echo -e "${YELLOW}Este script irá criar uma nova branch no GitHub e preparar os arquivos para deploy no Streamlit Cloud${NC}"
echo ""

# Verificar se git está instalado
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git não está instalado. Por favor, instale o Git primeiro.${NC}"
    exit 1
fi

# Configurações
REPO_URL="https://github.com/teckerconsultoria/rag-langchain-streamlit.git"
BRANCH_NAME="feature/multi-document-support"
TEMP_DIR="temp_repo"

# Criar diretório temporário
echo -e "${GREEN}Criando diretório temporário...${NC}"
mkdir -p $TEMP_DIR
cd $TEMP_DIR

# Clonar o repositório
echo -e "${GREEN}Clonando o repositório...${NC}"
git clone $REPO_URL .
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao clonar o repositório. Verifique a URL e suas credenciais.${NC}"
    cd ..
    rm -rf $TEMP_DIR
    exit 1
fi

# Criar nova branch
echo -e "${GREEN}Criando nova branch: $BRANCH_NAME...${NC}"
git checkout -b $BRANCH_NAME
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao criar a branch. Verifique se você tem permissões suficientes.${NC}"
    cd ..
    rm -rf $TEMP_DIR
    exit 1
fi

# Copiar os novos arquivos
echo -e "${GREEN}Copiando novos arquivos...${NC}"
cp ../knowledge_base.py .
cp ../file_manager.py .
cp ../app_multi_docs.py .
cp ../DEPLOYMENT_GUIDE_MULTI_DOCS.md .

# Verificar se packages.txt existe, se não, criar
if [ ! -f "packages.txt" ]; then
    echo -e "${YELLOW}Criando arquivo packages.txt...${NC}"
    cat > packages.txt << EOF
libmupdf-dev
libfreetype6-dev
libjpeg-dev
libharfbuzz-dev
libffi-dev
libjbig2dec0-dev
libopenjp2-7-dev
libssl-dev
EOF
fi

# Verificar e atualizar requirements.txt
echo -e "${GREEN}Atualizando requirements.txt...${NC}"
if [ -f "requirements.txt" ]; then
    # Verificar se as dependências necessárias estão presentes
    if ! grep -q "langchain-community" requirements.txt; then
        echo "langchain-community>=0.3.21" >> requirements.txt
    fi
    if ! grep -q "pymupdf" requirements.txt; then
        echo "pymupdf>=1.25.0" >> requirements.txt
    fi
    if ! grep -q "python-dotenv" requirements.txt; then
        echo "python-dotenv>=1.0.0" >> requirements.txt
    fi
else
    # Criar requirements.txt se não existir
    cat > requirements.txt << EOF
faiss-cpu>=1.10.0
langchain>=0.3.23
langchain-community>=0.3.21
langchain-core>=0.3.54
langchain-openai>=0.3.14
langchain-text-splitters>=0.3.8
openai>=1.75.0
pdfminer.six>=20250416
pymupdf>=1.25.5
python-dotenv>=1.0.0
streamlit>=1.44.1
tiktoken>=0.9.0
EOF
fi

# Adicionar arquivos ao git
echo -e "${GREEN}Adicionando arquivos ao git...${NC}"
git add knowledge_base.py file_manager.py app_multi_docs.py DEPLOYMENT_GUIDE_MULTI_DOCS.md packages.txt requirements.txt

# Commit das alterações
echo -e "${GREEN}Fazendo commit das alterações...${NC}"
git commit -m "Adiciona suporte para múltiplos documentos e base de conhecimento unificada"
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha ao fazer commit. Verifique se git está configurado corretamente.${NC}"
    cd ..
    rm -rf $TEMP_DIR
    exit 1
fi

# Instruções para push e deploy
echo ""
echo -e "${YELLOW}=== Próximos Passos ===${NC}"
echo -e "${GREEN}1. Envie a nova branch para o GitHub:${NC}"
echo "   git push -u origin $BRANCH_NAME"
echo ""
echo -e "${GREEN}2. Acesse o Streamlit Cloud (https://share.streamlit.io/) e configure:${NC}"
echo "   - Repositório: teckerconsultoria/rag-langchain-streamlit"
echo "   - Branch: $BRANCH_NAME"
echo "   - Arquivo principal: app_multi_docs.py"
echo "   - Em Advanced Settings, configure sua chave API OpenAI"
echo ""
echo -e "${GREEN}3. Clique em Deploy para atualizar a aplicação${NC}"
echo ""
echo -e "${YELLOW}Os arquivos estão prontos no diretório $TEMP_DIR${NC}"
echo -e "${YELLOW}Você pode navegar até lá e executar os comandos acima${NC}"

# Fim
echo ""
echo -e "${GREEN}Script concluído com sucesso!${NC}"
