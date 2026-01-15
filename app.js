// ================================
// API Configuration
// ================================
const API_BASE_URL = 'http://localhost:8001';
const API_ENDPOINTS = {
    qa: `${API_BASE_URL}/qa`,
    health: `${API_BASE_URL}/health`,
    favorites: `${API_BASE_URL}/favorites`,
    chatHistory: `${API_BASE_URL}/chat-history`
};

// ================================
// Session ID (anonymous user)
// ================================
const SESSION_ID_KEY = 'quran_session_id';

let sessionId = localStorage.getItem(SESSION_ID_KEY);
if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_ID_KEY, sessionId);
}

// ================================
// DOM Elements
// ================================
const welcomeScreen = document.getElementById('welcome-screen');
const chatContainer = document.getElementById('chat-container');
const startButton = document.getElementById('start-button');
const messagesContainer = document.getElementById('messages-container');
const chatForm = document.getElementById('chat-form');
const questionInput = document.getElementById('question-input');
const submitButton = document.getElementById('submit-button');
const loadingOverlay = document.getElementById('loading-overlay');

// ================================
// State
// ================================
let isWaitingForResponse = false;

// ================================
// Initialize
// ================================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    checkAPIHealth();
    loadChatHistory();

    startButton.addEventListener('click', showChatInterface);
    chatForm.addEventListener('submit', handleSubmit);
    questionInput.addEventListener('input', handleInputChange);
    questionInput.addEventListener('keydown', handleKeyDown);

    questionInput.addEventListener('input', autoResizeTextarea);
}

// ================================
// API Health
// ================================
async function checkAPIHealth() {
    try {
        const response = await fetch(API_ENDPOINTS.health);
        if (!response.ok) {
            console.warn('API health check failed');
        }
    } catch (error) {
        console.warn('API not available:', error);
    }
}
async function loadChatHistory() {
    try {
        const response = await fetch(API_ENDPOINTS.chatHistory, {
            headers: {
                'X-Session-Id': sessionId
            }
        });

        if (!response.ok) return;

        const data = await response.json();

        if (!data.history || data.history.length === 0) return;

        // Show chat UI automatically if history exists
        welcomeScreen.classList.add('hidden');
        chatContainer.classList.remove('hidden');

        data.history.forEach(message => {
            addMessage(message.role, message.content);
        });

    } catch (error) {
        console.warn('Failed to load chat history:', error);
    }
}


// ================================
// UI Handlers
// ================================
function showChatInterface() {
    welcomeScreen.classList.add('hidden');
    chatContainer.classList.remove('hidden');
    questionInput.focus();
}

function handleInputChange() {
    const hasText = questionInput.value.trim().length > 0;
    submitButton.disabled = !hasText || isWaitingForResponse;
}

function autoResizeTextarea() {
    questionInput.style.height = 'auto';
    questionInput.style.height = Math.min(questionInput.scrollHeight, 150) + 'px';
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        if (!submitButton.disabled) {
            handleSubmit(event);
        }
    }
}

// ================================
// Submit Question
// ================================
async function handleSubmit(event) {
    event.preventDefault();

    const question = questionInput.value.trim();
    if (!question || isWaitingForResponse) return;

    addMessage('user', question);

    questionInput.value = '';
    questionInput.style.height = 'auto';
    handleInputChange();

    showLoading();
    isWaitingForResponse = true;
    submitButton.disabled = true;

    try {
        const response = await fetch(API_ENDPOINTS.qa, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-Id': sessionId
            },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        addMessage('assistant', data.answer, data.relevant_ayahs);

    } catch (error) {
        console.error('Error:', error);
        addErrorMessage(
            'Unable to connect to the server. Please ensure the backend is running.'
        );
    } finally {
        hideLoading();
        isWaitingForResponse = false;
        handleInputChange();
        questionInput.focus();
    }
}

// ================================
// Chat Rendering
// ================================
function addMessage(role, content, relevantAyahs = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const contentParagraph = document.createElement('p');
    contentParagraph.textContent = content;
    contentDiv.appendChild(contentParagraph);

    if (relevantAyahs && relevantAyahs.length > 0) {
        const ayahsDiv = document.createElement('div');
        ayahsDiv.className = 'relevant-ayahs';

        const title = document.createElement('div');
        title.className = 'relevant-ayahs-title';
        title.textContent = 'Relevant Verses';
        ayahsDiv.appendChild(title);

        relevantAyahs.forEach(ayah => {
            ayahsDiv.appendChild(createAyahItem(ayah));
        });

        contentDiv.appendChild(ayahsDiv);
    }

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function createAyahItem(ayah) {
    const ayahDiv = document.createElement('div');
    ayahDiv.className = 'ayah-item';

    const headerDiv = document.createElement('div');
    headerDiv.className = 'ayah-header';

    const reference = document.createElement('span');
    reference.className = 'ayah-reference';
    reference.textContent = `${ayah.surah_name} ${ayah.surah}:${ayah.ayah}`;

    const surahName = document.createElement('span');
    surahName.className = 'ayah-surah-name';
    surahName.textContent = `Surah ${ayah.surah_name}`;

    headerDiv.appendChild(reference);
    headerDiv.appendChild(surahName);

    const arabicDiv = document.createElement('div');
    arabicDiv.className = 'ayah-arabic';
    arabicDiv.textContent = ayah.arabic;

    const englishDiv = document.createElement('div');
    englishDiv.className = 'ayah-english';
    englishDiv.textContent = ayah.english;

    ayahDiv.appendChild(headerDiv);
    ayahDiv.appendChild(arabicDiv);
    ayahDiv.appendChild(englishDiv);

    return ayahDiv;
}

// ================================
// Errors & Loading
// ================================
function addErrorMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant-message';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content error-message';
    contentDiv.textContent = message;

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function scrollToBottom() {
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
}
