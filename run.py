import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Definir variáveis de ambiente para implantação
os.environ["STREAMLIT_SERVER_PORT"] = "8501"
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"

# Importar e executar a aplicação Streamlit
import app_deploy
