document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const messagesWrapper = document.getElementById('messagesWrapper');
    const chatContainer = document.getElementById('chatContainer');
    const welcomeScreen = document.querySelector('.welcome-screen');

    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value.trim() !== '') {
            sendBtn.classList.add('active');
        } else {
            sendBtn.classList.remove('active');
        }
    });

    // Send message on Enter (but allow Shift+Enter for new line)
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    function sendMessage() {
        const text = messageInput.value.trim();
        if (text === '') return;

        // Hide welcome screen on first message
        if (welcomeScreen.style.display !== 'none') {
            welcomeScreen.style.display = 'none';
            messagesWrapper.style.display = 'flex';
        }

        // Add user message
        appendMessage('user', text);
        
        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        sendBtn.classList.remove('active');
        
        // Simulate AI thinking and responding
        showTypingIndicator();
        
        // Simulate a delay for the AI response
        setTimeout(() => {
            removeTypingIndicator();
            const aiResponses = [
                "I can certainly help you with that. The RAG architecture combines information retrieval with text generation.",
                "That's an interesting approach. Have you considered optimizing the vector embeddings for better recall?",
                "Based on the context provided, processing the documents in chunks before generating embeddings would yield better results.",
                "I've analyzed the query and found matching documents in the vector database. Here's a summary of the findings...",
                "The frontend UI is looking great! Connecting it to the FastAPI backend should be straightforward using the fetch API."
            ];
            const randomResponse = aiResponses[Math.floor(Math.random() * aiResponses.length)];
            appendMessage('ai', randomResponse);
        }, 1500);
    }

    function appendMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatarIcon = sender === 'user' ? 'Y' : '<i class="fa-solid fa-robot"></i>';
        const avatarClass = sender === 'user' ? 'avatar' : '';
        
        messageDiv.innerHTML = `
            <div class="message-avatar ${avatarClass}">
                ${avatarIcon}
            </div>
            <div class="message-content">
                <p>${escapeHTML(text)}</p>
            </div>
        `;
        
        messagesWrapper.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message typing-indicator-container';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        messagesWrapper.appendChild(typingDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function escapeHTML(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
});
