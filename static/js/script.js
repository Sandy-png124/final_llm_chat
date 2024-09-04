document.getElementById('pdf-form').onsubmit = async function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    const response = await fetch('/process', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();
    alert(result.message);
}

document.getElementById('question-form').onsubmit = async function (e) {
    e.preventDefault();
    const question = document.getElementById('user-question').value;

    const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
    });

    const result = await response.json();
    document.getElementById('response').innerText = result.reply;
}

document.getElementById('question-form').onsubmit = async function (e) {
    e.preventDefault();
    const question = document.getElementById('user-question').value;

    // Append the user question at the top
    appendMessage('user-message', question);

    const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
    });

    const result = await response.json();

    // Append the bot reply at the top
    appendMessage('bot-message', result.reply);
    
    // Clear the input field
    document.getElementById('user-question').value = '';
}

function appendMessage(className, message) {
    const chatArea = document.getElementById('chat-area');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', className);
    messageDiv.innerText = message;
    
    // Insert the new message at the top
    chatArea.insertBefore(messageDiv, chatArea.firstChild);

    // Optional: Scroll to top to make sure the new message is visible
    chatArea.scrollTop = 0;
}

