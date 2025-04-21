FROM python:3.10-slim

WORKDIR /app

# Copiar arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-dotenv

# Copiar o restante dos arquivos da aplicação
COPY . .

# Criar diretório para índices FAISS
RUN mkdir -p faiss_index

# Expor a porta que o Streamlit usa
EXPOSE 8501

# Comando para iniciar a aplicação
CMD ["streamlit", "run", "app_deploy.py", "--server.port=8501", "--server.address=0.0.0.0"]
