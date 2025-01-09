const template = (strings, ...values) => {
    return strings.reduce((acc, str, index) => {
        return acc + str + (values[index] !== undefined ? values[index] : '');
    }, '');
}

const cssTemplate = (data) => template`
dialog[is=helpbot-dialog] {
    --primary-color: #3D5CAA;
    --background-color: #F0EEE5;
    --text-color: #4D4B3F;
    --text-white: #F0EEE5;
    --border-color: #aaa;
    --border-radius: 10px;
    --padding-gap: 1ch;

    /* 
    --brand: #0af;
    --brand: hsl(100 100% 50%);
    --brand-hue: 200;
    --brand-saturation: 100%;
    --brand-lightness: 50%;

    --brand-light: hsl(var(--brand-hue) var(--brand-saturation) var(--brand-lightness));
    --text1-light: hsl(var(--brand-hue) var(--brand-saturation) 10%);
    --text2-light: hsl(var(--brand-hue) 30% 30%);
    --surface1-light: hsl(var(--brand-hue) 25% 90%);
    --surface2-light: hsl(var(--brand-hue) 20% 99%);
    --surface3-light: hsl(var(--brand-hue) 20% 92%);
    --surface4-light: hsl(var(--brand-hue) 20% 85%);
    --surface-shadow-light: var(--brand-hue) 10% 20%;
    --shadow-strength-light: .02;

    --brand-dark: hsl(var(--brand-hue) calc(var(--brand-saturation) / 2) calc(var(--brand-lightness) / 1.5));
    --text1-dark: hsl(var(--brand-hue) 15% 85%);
    --text2-dark: hsl(var(--brand-hue) 5% 65%);
    --surface1-dark: hsl(var(--brand-hue) 10% 10%);
    --surface2-dark: hsl(var(--brand-hue) 10% 15%);
    --surface3-dark: hsl(var(--brand-hue) 5%  20%);
    --surface4-dark: hsl(var(--brand-hue) 5% 25%);
    --surface-shadow-dark: var(--brand-hue) 50% 3%;
    --shadow-strength-dark: .8;
    */
}

/*
dialog[is=helpbot-dialog]::backdrop {
    backdrop-filter: blur(6px);
}
html:has(dialog[open][is=helpbot-dialog]) {
    overflow: hidden;
}
*/

dialog[is=helpbot-dialog] {
    position: fixed;
    inset: 0;
    z-index: 1000;
    margin: auto;
    padding: 0;
    border: none;

    width: 480px;
    height: 640px;
    max-width: 100%;
    max-height: 80%;

    color: var(--text-color);
    background: var(--background-color);
    font-family: ui-sans-serif,-apple-system,system-ui,Segoe UI,Helvetica,Arial, sans-serif;
    font-size: 14px;
    border-radius: var(--border-radius);
    box-shadow2: rgba(0, 0, 0, 0.05) 0px 0.48px 2.41px -0.38px, rgba(0, 0, 0, 0.17) 0px 4px 20px -0.75px;

    box-shadow: 0px 0px 10px 1px rgba(0,0,0,0.71);
}

dialog[is=helpbot-dialog]:not([open]) {
    pointer-events: none;
    opacity: 0;
}

/*                                              main */
.helpbot-launcher{
    position: fixed;
    bottom: 32px;
    right: 32px;
    z-index: 1000;
    border: none;
    background: var(--background-color);
    padding: 4px;
    border-radius: 4px;
    box-shadow: 0px 0px 10px 1px rgba(0,0,0,0.71);
}

/*                                              main */
.hbform {
    height: 100%;
    display: grid;
    grid-template-rows: auto 1fr auto;
}

.hbform button {
    display: inline-block;
    cursor: pointer;
    touch-action: manipulation;
    background: transparent;
    color: inherit;
    padding: 5px 10px;
    border-radius: var(--border-radius);
    border: 1px solid var(--border-color);
}
.hbform button:hover {
    color: var(--primary-color);
    border-color: var(--primary-color);
}
.hbform header button {
    color: inherit;
    border-color: var(--primary-color);
}
.hbform header button:hover {
    color: inherit;
    border-color: var(--text-white);
}
.hbform svg {
    display: block;
    width: 16px;
    height: 16px;
    fill: currentColor;
}

/*                                              header */
.hbform > header {
    position: relative;
    display: flex;
    gap: var(--padding-gap);
    align-items: center;
    justify-content: space-between;
    padding-block: 10px;
    padding-inline: 10px;
    margin-bottom: var(--padding-gap);

    border-radius: var(--border-radius) var(--border-radius) 0 0;
    border: 1px solid var(--primary-color);
    background: var(--primary-color);
    color: var(--text-white);
}
.hbform > header h3{
    flex-grow: 1;
    margin: 0;
    font-size: 16px;
}
.hbform header .brand .avatar {
    background: var(--background-color);
    padding: 4px;
    border-radius: 4px;
}
.hbform > header .slogan{
    position: absolute;
    display: block;
    padding: 0 10px 2px 26px;
    bottom: -10px;
    right: -1px;
    font-size: 12px;
    font-weight: bold;
    background: var(--primary-color);
    border-radius: var(--border-radius);
}
.hbform > header .slogan a{
    color: inherit;
}

/*                                              footer */
.hbform footer {
    position: relative;
    display: flex;
    gap: var(--padding-gap);
    padding: var(--padding-gap);
}
.hbform footer > textarea {
    box-sizing: border-box;
    flex-grow: 1;
    resize: none;
    height: 60px;
    border: 1px solid var(--border-color);
    padding: var(--padding-gap);
    border-radius: var(--border-radius);
}
.hbform footer > textarea:focus {
    border-color: var(--primary-color);
    outline: none;
}
/*
.hbform footer button {
    border: none;
    padding: 0;
}
.hbform footer button svg {
    width: 24px;
    height: 24px;
    padding: var(--padding-gap);
    border-radius: var(--border-radius);
    border: 1px solid #666;
}
*/

/*                                              main/messages */
.hbform main {
    padding: var(--padding-gap);
    margin: var(--padding-gap);
    margin-bottom: 0;
    background-color: #fff;
    border-radius: var(--border-radius);
    border: 1px solid var(--border-color);
    overflow-y: auto;
}
.hbform main .message{
    clear: both;
    padding: 0.5em 1em;
    margin-bottom: 1em;
    border-radius: 5px;
}
.hbform main .message.role-user {
    float: right;
    background-color: #eee;
}
.hbform main .message.role-assistant {
    background-color: #F7FAFC;
}

.hbform main .message p,
.hbform main .message li,
.hbform main .message ul,
.hbform main .message ol {
    line-height: 1.2em;
    margin: 0.5em 0;
}
.hbform main .message > li {
    margin-left: 1em;
}

/*
.hbform .messages {
    display: block;
    overflow-y: auto;
    padding: var(--padding-gap);
    background-color: #fff;
    border-radius: var(--border-radius);
}
*/
/*                                              loader */
.loader {
    position: absolute;
    left: 12px;
    top: 20px;
}
.loader span {
    display: inline-block;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    animation-fill-mode: both;
    animation: bblFadInOut 2s infinite ease-in-out;

    color: var(--primary-color);
    font-size: 7px;
    text-indent: -9999em;
    transform: translateZ(0);
}
.loader span:nth-child(2n) {
    animation-delay: 0.20s;
}
.loader span:nth-child(3n) {
    animation-delay: 0.40s;
}

@keyframes bblFadInOut {
    0%, 80%, 100% { box-shadow: 0 2.5em 0 -10px }
    40% { box-shadow: 0 25px 0 0 }
}

`;

const htmlTemplate = (data) => template`
<form method="dialog" class="hbform">
    <header>
        <div class="brand">
            <div class="avatar">
                <img src="/_/img/helpbot-avatar.svg" width="32">
            </div>
            <div class="slogan">
                Powered by <a href="https://ai.ioix.net" target="_blank">HelpBot</a>
            </div>
        </div>

        <h3>...</h3>

        <button type="reset" class="new-thread-button" title="New Chat">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" class="bi bi-plus-lg" viewBox="0 0 16 16">
                <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
                <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
            </svg>
        </button>

        <button class="close-button">
            <svg id="icon-close" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
                <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/>
            </svg>
        </button>
    </header>
    <main class="messages">
    </main>
    <footer>
        <textarea placeholder="Send a message to HelpBot" disabled></textarea>

        <div style="display: inline-flex; align-self: center;">
            <div class="loader">
                <span></span>
                <span></span>
                <span></span>
            </div>

            <button type="reset" class="send-button" title="Send Message">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
                    <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576zm6.787-8.201L1.591 6.602l4.339 2.76z"/>
                </svg>
            </button>
        </div>
    </footer>
</form>
`;

// Utility function to get cookie by name
const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
    return ''
}

// Utility function to set a cookie
const setCookie = (name, value, days) => {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = `${name}=${value || ""}${expires}; path=/`;
}

function markdownToHtml(markdown) {
    // Функция для экранирования специальных символов HTML
    function escapeHtml(text) {
        return text.replace(/&/g, '&amp;')
                   .replace(/</g, '&lt;')
                   .replace(/>/g, '&gt;');
    }

    // Разбиваем текст на строки
    let lines = markdown.split('\n');
    let result = '';
    let listStack = [];
    let prevIndent = 0;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];

        // Пропускаем пустые строки
        if (/^\s*$/.test(line)) {
            continue;
        }

        // Обработка заголовков
        if (/^######\s+(.*)/.test(line)) {
            line = line.replace(/^######\s+(.*)/, '<h6>$1</h6>');
            result += line;
            continue;
        } else if (/^#####\s+(.*)/.test(line)) {
            line = line.replace(/^#####\s+(.*)/, '<h5>$1</h5>');
            result += line;
            continue;
        } else if (/^####\s+(.*)/.test(line)) {
            line = line.replace(/^####\s+(.*)/, '<h4>$1</h4>');
            result += line;
            continue;
        } else if (/^###\s+(.*)/.test(line)) {
            line = line.replace(/^###\s+(.*)/, '<h3>$1</h3>');
            result += line;
            continue;
        } else if (/^##\s+(.*)/.test(line)) {
            line = line.replace(/^##\s+(.*)/, '<h2>$1</h2>');
            result += line;
            continue;
        } else if (/^#\s+(.*)/.test(line)) {
            line = line.replace(/^#\s+(.*)/, '<h1>$1</h1>');
            result += line;
            continue;
        }

        // Обработка цитат
        if (/^>\s+(.*)/.test(line)) {
            line = line.replace(/^>\s+(.*)/, '<blockquote>$1</blockquote>');
            result += line;
            continue;
        }

        // Обработка горизонтальных линий
        if (/^---$/.test(line)) {
            result += '<hr>';
            continue;
        }

        // Обработка элементов списка
        let listMatch = /^(\s*)([-\*\+]|\d+\.)\s+(.*)/.exec(line);
        if (listMatch) {
            let indent = listMatch[1].length;
            let listType = isNaN(parseInt(listMatch[2])) ? 'ul' : 'ol';
            let content = listMatch[3];

            // Жирный и курсив
            content = content.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
            content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
            // Инлайновый код
            content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
            // Ссылки
            content = content.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
            // Изображения
            content = content.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');

            if (indent > prevIndent) {
                result += `<${listType}>`.repeat((indent - prevIndent) / 2);
                listStack.push(listType);
            } else if (indent < prevIndent) {
                let diff = (prevIndent - indent) / 2;
                for (let j = 0; j < diff; j++) {
                    let lastList = listStack.pop();
                    result += `</li></${lastList}>`;
                }
                result += '</li>';
            } else {
                result += '</li>';
            }
            result += `<li>${content}`;
            prevIndent = indent;
            continue;
        } else {
            // Закрываем открытые списки перед обработкой обычного текста
            while (listStack.length > 0) {
                let lastList = listStack.pop();
                result += `</li></${lastList}>`;
            }
            prevIndent = 0;
        }

        // Обработка параграфов
        if (!/^<\/?(h\d|ul|ol|li|blockquote|pre|code|img|a|strong|em|hr)/.test(line)) {
            line = `<p>${line}</p>`;
        }
        // Жирный и курсив
        line = line.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
        line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        line = line.replace(/\*(.*?)\*/g, '<em>$1</em>');
        // Инлайновый код
        line = line.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Ссылки
        line = line.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
        // Изображения
        line = line.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');

        result += line;
    }

    // Закрываем все открытые списки
    while (listStack.length > 0) {
        let lastList = listStack.pop();
        result += `</li></${lastList}>`;
    }

    return result;
}

class HelpBotDialogElement extends HTMLDialogElement {
    static observedAttributes = ['open'];

    constructor() {
        super();

        const styleSheet = document.createElement('style');
        styleSheet.textContent = cssTemplate(this);
        document.head.appendChild(styleSheet);

        this.insertAdjacentHTML("afterbegin", htmlTemplate(this));

        // this.addEventListener("click", (event) => {
        //     console.log(event);
        // });

        this.header_title = this.querySelector('header h3');
        this.textarea = this.querySelector('textarea');
        this.loader = this.querySelector('.loader');
        this.messages = this.querySelector('.messages');
        this.send_button = this.querySelector('.send-button');
        this.new_thread_button = this.querySelector('.new-thread-button');

        this.ws = null;
        this.wsUrl = '';
    }
    connectedCallback() {
        this.wsUrlPrefix = this.getAttribute('websocket-url');
        if (!this.wsUrlPrefix) this.wsUrlPrefix = 'wss://ai.ioix.net/ws/helpbot';

        this.assistant_id = this.getAttribute('assistant');

        const placeholder = this.getAttribute('placeholder');
        if (placeholder) {
            this.textarea.setAttribute('placeholder', placeholder);
        }

        this.textarea.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                if (this.textarea.value) {
                    event.preventDefault(); // Prevent adding a new line
                    this.sendMessage(this.textarea.value);
                    this.textarea.value = ''; // Clear the textarea
                }
            }
        });

        this.send_button.addEventListener('click', (event) => {
            if (this.textarea.value) {
                this.sendMessage(this.textarea.value);
                this.textarea.value = ''; // Clear the textarea
            }
        });

        this.new_thread_button.addEventListener('click', (event) => {
            setCookie(this.assistant_id, '', 3);  // reset cookie value
            this.initAssistant(this.assistant_id);
        });
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name == 'open' && this.open) {
            if (this.assistant_id) {
                setTimeout(() => this.initAssistant(this.assistant_id));
            }
        }
    }

    initAssistant(assistant_id) {
        const thread_id = getCookie(assistant_id);
        const wsUrl = `${this.wsUrlPrefix}?assistant=${assistant_id}&thread=${thread_id}`;

        if (this.wsUrl == wsUrl) {
            return
        }

        this.assistant_id = assistant_id;

        if (this.ws) {
            this.ws.close();
        }

        this.ws = new WebSocket(wsUrl);
        this.wsUrl = wsUrl;

        // Handle incoming messages
        this.ws.addEventListener('message', (event) => {
            const msg = JSON.parse(event.data);
            if (msg.object === 'assistant') {
                this.header_title.innerHTML = msg.name;
                this.messages.innerHTML = '';

                this.textarea.removeAttribute('disabled');
                this.loader.style.visibility = 'hidden';

            } else if (msg.object === 'thread') {
                setCookie(assistant_id, msg.id, 3);

            } else {
                this.displayMessage(msg);
            }
        });

        this.ws.addEventListener('error', (error) => {
            console.error('WebSocket error:', error);
        });
    }

    displayMessage(msg) {
        const messageElem = document.createElement('div');
        messageElem.classList.add('message');
        messageElem.classList.add(`role-${msg.role}`);
        if (msg.role == 'user') {
            messageElem.innerHTML = `<p>${msg.content}</p>`;
        } else {
            let content = msg.content.replace(/【[^】]+】/g, '');
            messageElem.innerHTML = markdownToHtml(content);
        }
        this.messages.appendChild(messageElem);
        this.messages.scrollTop = this.messages.scrollHeight; // Scroll to the latest message

        if (msg.role == 'assistant') {
            this.textarea.removeAttribute('disabled');
            this.loader.style.visibility = 'hidden';
        }

    }

    // Send messages via WebSocket
    sendMessage(msg) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(msg);
        } else {
            console.error('WebSocket is not connected.');
        }
        this.textarea.setAttribute('disabled', 'disabled');
        this.loader.style.visibility = 'visible';
    }

    // Called when the element is removed from the DOM
    disconnectedCallback() {
        if (this.ws) {
          this.ws.close(); // Close WebSocket connection
        }
    }

}

customElements.define("helpbot-dialog", HelpBotDialogElement, {extends: "dialog"});