// Funções para interatividade básica da interface estática

// Função para alternar entre as abas
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remover classe active de todos os botões e conteúdos
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Adicionar classe active ao botão clicado
            button.classList.add('active');
            
            // Mostrar o conteúdo correspondente
            const tabId = button.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
}

// Função para alternar a exibição dos itens do histórico
function toggleHistoryItem(element) {
    const historyItem = element.parentElement;
    historyItem.classList.toggle('active');
    
    // Alternar o ícone
    const toggleIcon = element.querySelector('.toggle-icon');
    if (historyItem.classList.contains('active')) {
        toggleIcon.style.transform = 'rotate(180deg)';
    } else {
        toggleIcon.style.transform = 'rotate(0deg)';
    }
}

// Função para simular o upload de arquivo
function setupFileUpload() {
    const fileInput = document.getElementById('file-upload');
    const fileName = document.querySelector('.file-name');
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
        } else {
            fileName.textContent = 'Nenhum arquivo selecionado';
        }
    });
}

// Função para simular o envio de consulta
function setupQuerySubmission() {
    const queryInput = document.getElementById('query-input');
    const queryButton = queryInput.nextElementSibling;
    
    queryButton.addEventListener('click', () => {
        if (queryInput.value.trim() !== '') {
            // Simular carregamento
            queryButton.textContent = 'Processando...';
            queryButton.disabled = true;
            
            // Restaurar após 1.5 segundos
            setTimeout(() => {
                queryButton.textContent = 'Enviar';
                queryButton.disabled = false;
                
                // Exibir mensagem de sucesso
                const responseArea = document.querySelector('.response-area');
                responseArea.scrollIntoView({ behavior: 'smooth' });
            }, 1500);
        }
    });
}

// Inicializar todas as funcionalidades quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupFileUpload();
    setupQuerySubmission();
    
    // Inicializar os itens do histórico
    const historyItems = document.querySelectorAll('.history-item');
    historyItems.forEach(item => {
        const header = item.querySelector('.history-header');
        header.addEventListener('click', () => {
            toggleHistoryItem(header);
        });
    });
});
