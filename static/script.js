let isWaitingForResponse = false;
let timeoutId;

document.getElementById('message').addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !isWaitingForResponse) {
        sendMessage();
    }
});

document.getElementById('message').addEventListener('input', function() {
    if (isWaitingForResponse) {
        this.value = this.value.slice(0, -1);  // Remove last character if waiting for response
    }
});

function sendMessage() {
    if (isWaitingForResponse) return;  // Don't proceed if waiting for response
    
    const message = document.getElementById('message').value;
    if (message) {
        isWaitingForResponse = true;  // Set flag to true, indicating wait for response
        appendMessage('You', message);
        showTypingIndicator();
        
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept-Language': navigator.language
            },
            body: JSON.stringify({ message: message })
        })
        .then(res => res.json())
        .then(data => {
            removeTypingIndicator();
            if (data.response) {
                appendMessage('Wayne A.I.', data.response);
            } else if (data.error) {
                appendMessage('Wayne A.I.', data.error);
            }
            scrollToBottom();
            document.getElementById('message').value = ''; // Clear input after sending
        })
        .catch(error => {
            console.error('Error:', error);
            removeTypingIndicator();
            appendMessage('Wayne A.I.', 'An error occurred while processing your message.');
            scrollToBottom();
        })
        .finally(() => {
            isWaitingForResponse = false;  // Reset the flag after response is received or error occurs
        });
    }
}

function appendMessage(sender, message) {
    const chat = document.getElementById('chat');
    const messageElement = document.createElement('p');
    messageElement.textContent = `${sender}: ${message}`;
    chat.appendChild(messageElement);
}

function scrollToBottom() {
    const chatWindow = document.getElementById('chat');
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTypingIndicator() {
    const chat = document.getElementById('chat');
    const indicator = document.createElement('p');
    indicator.id = 'typing-indicator';
    indicator.textContent = 'Wayne A.I. is typing...';
    chat.appendChild(indicator);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Initial greeting - Changed to POST
fetch('/greet', {
    method: 'POST',
    headers: { 'Accept-Language': navigator.language }
})
.then(res => res.json())
.then(data => {
    appendMessage('Wayne A.I.', data.greeting);
    scrollToBottom();
});