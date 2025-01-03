// Utility function to get cookie by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
    return ''
}

// Utility function to set a cookie
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = `${name}=${value || ""}${expires}; path=/`;
}

// function imageLogoSVG() {
//     const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
//     const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
//     svg.setAttribute("viewBox", "0 0 16 16");
//     path.setAttribute("d", "M7.996 0A8 8 0 0 0 0 8a8 8 0 0 0 6.93 7.93v-1.613a1.06 1.06 0 0 0-.717-1.008A5.6 5.6 0 0 1 2.4 7.865 5.58 5.58 0 0 1 8.054 2.4a5.6 5.6 0 0 1 5.535 5.81l-.002.046-.012.192-.005.061a5 5 0 0 1-.033.284l-.01.068c-.685 4.516-6.564 7.054-6.596 7.068A7.998 7.998 0 0 0 15.992 8 8 8 0 0 0 7.996.001Z");
//     svg.appendChild(path);
//     svg.style.width = '32px';
//     svg.style.height = '32px';
//     return svg;
// }

function markdownToHTML(markdown) {
    // Convert headers (supporting h1 to h6)
    let html = markdown.replace(/^### (.*$)/gim, '<h3>$1</h3>')
                       .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                       .replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Convert bold text (double asterisks or underscores)
    html = html.replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
               .replace(/__(.*)__/gim, '<strong>$1</strong>');

    // Convert italic text (single asterisks or underscores)
    html = html.replace(/\*(.*)\*/gim, '<em>$1</em>')
               .replace(/_(.*)_/gim, '<em>$1</em>');

    // Convert links [text](url)
    html = html.replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2">$1</a>');

    //Lists
    //   html = html.replace(/([^\n]+)(\-)([^\n]+)/g, '<ul><li>$3</li></ul>');

    return html;

    //   // Convert unordered lists
    //   html = html.replace(/^\s*-\s*(.*)/gim, '<li>$1</li>');

    //   // Convert ordered lists
    //   html = html.replace(/^\d+\.\s+(.*)/gim, '<li>$1</li>');

    //   // Convert new lines into <br> and paragraphs
    //   html = html.replace(/\n$/gim, '<br />')
    //              .replace(/\n/g, '</p><p>');

    //   return `<p>${html}</p>`;
}

// function helpBotModal(assistant_id) {

//     if (!window.helpBot) {
//         const helpBot = document.createElement('help-bot');
//         helpBot.style.position = 'absolute';
//         helpBot.style.bottom = '20px';
//         helpBot.style.right = '20px';
//         helpBot.style.zIndex = '1000';
//         helpBot.style.width = '400px';
//         helpBot.style.height = '500px';

//         document.body.appendChild(helpBot);
//         window.helpBot = helpBot;
//     }

//     // window.helpBot.setAttribute('assistant', assistant);
//     // window.helpBot.setAttribute('title', title);
//     window.helpBot.wsConnect(assistant_id);
//     window.helpBot.style.visibility = 'visible';

//     // close by Esc
//     window.addEventListener('keydown', (event) => {
//         if (event.key === 'Escape') {
//             window.helpBot.style.visibility = 'hidden';
//         }
//     });

//     // // close by outside click
//     // window.addEventListener('click', (event) => {
//     //     window.helpBot.style.visibility = 'hidden';
//     // });
//     // window.helpBot.addEventListener('click', (event) => {
//     //     event.stopPropagation();
//     // });
// }

// Define a class for the HelpBot component
class HelpBot extends HTMLElement {

    constructor() {
        super(); // Call the parent class constructor

        // Attach Shadow DOM to encapsulate styles and structure
        const shadow = this.attachShadow({mode: 'closed'});

        // Create an internal template for the component's HTML
        const template = document.createElement('template');
        template.innerHTML = `
        <style>
            :host {
                --primary-color: #F9A825;
                --secondary-color: #ff590c;
                --background-color: #f6f6f6;

                width: 64px;
                height: 64px;
                max-width: 90vw;
                max-height: 90vh;
                position: fixed;
                bottom: 2vh;
                right: 2vw;
                z-index: 1000;
                overflow: hidden;
                transition: all 0.3s;

                font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 13px;
                border-radius: 10px;
                box-shadow: rgba(0, 0, 0, 0.05) 0px 0.48px 2.41px -0.38px, rgba(0, 0, 0, 0.17) 0px 4px 20px -0.75px;
                background-color: var(--background-color);
                color: #333333;
            }
            #icon-logo {
                cursor: pointer;
                background-color: var(--primary-color);
                position: absolute;
                top: 0;
                left: 0;
                color: #fff;
                width: 48px;
                height: 48px;
                padding: 8px;
            }
            #icon-close {
                cursor: pointer;
                background-color: var(--primary-color);
                position: absolute;
                top: 0;
                right: 0;
                color: #fff;
                width: 24px;
                height: 24px;
                padding: 20px 16px 8px 8px;
            }
            :host(.maximized) {
                width: 480px;
                height: 640px;
            }
            header {
                line-height: 64px;
                white-space: nowrap;
                color: #fff;
                font-size: 16px;
                font-weight: bold;
                padding:0 48px 0 72px;
                background-color: var(--primary-color);
                border-radius: 10px 10px 0 0;
            }
            output {
                display: block;
                overflow-y: auto;
                height: 450px;
            }
            output .message {
                border-radius: 10px;
                padding: 4px;
                margin: 10px 8px;
            }
            output .message p {
                margin: 4px 0;
            }
            output .message.role-user {
                border-left: 5px solid var(--secondary-color);
                background-image: linear-gradient(to right, #eee, var(--background-color));
            }
            output .message.role-assistant {
                border-left: 5px solid var(--primary-color);
            }
            textarea {
                resize: none;
                height: 48px;
                box-sizing: border-box;
                width: 100%;
                padding: 10px;
                background-color: #fff;
                border: none;
                outline: none;
                font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 13px;
            }
            footer {
                display: block;
                margin-top: 5px;
            }
            footer #new_conversation {
                float: left;
                margin: 0 10px;
            }
            footer address {
                float: right;
                margin: 0 10px;
                font-style: normal;
            }
            footer a {
                color: var(--primary-color);
                text-decoration: none;
                font-weight: bold;
            }

            .progress {
                display: block;
                visibility: hidden;
                position: absolute;
                bottom: 40px;
                left: 10px;
                width: 200px;
                height: 32px;
                color: var(--primary-color);
                background-color: #fff;
            }
            .progress div {
                position: absolute;
                top: 10px;
                width: 15px;
                height: 15px;
                border-radius: 50%;
                background: currentColor;
                animation-timing-function: cubic-bezier(0, 1, 1, 0);
            }
            .progress div:nth-child(1) {
                left: 8px;
                animation: progress1 0.6s infinite;
            }
            .progress div:nth-child(2) {
                left: 8px;
                animation: progress2 0.6s infinite;
            }
            .progress div:nth-child(3) {
                left: 32px;
                animation: progress2 0.6s infinite;
            }
            .progress div:nth-child(4) {
                left: 56px;
                animation: progress3 0.6s infinite;
            }
            @keyframes progress1 {
                0% {transform: scale(0);}
                100% {transform: scale(1);}
            }
            @keyframes progress3 {
                0% {transform: scale(1);}
                100% {transform: scale(0);}
            }
            @keyframes progress2 {
                0% {transform: translate(0, 0);}
                100% {transform: translate(24px, 0);}
            }


        </style>

        <svg id="icon-close" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">
            <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/>
        </svg>
        <svg id="icon-logo" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-robot" viewBox="0 0 16 16">
            <path d="M6 12.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5M3 8.062C3 6.76 4.235 5.765 5.53 5.886a26.6 26.6 0 0 0 4.94 0C11.765 5.765 13 6.76 13 8.062v1.157a.93.93 0 0 1-.765.935c-.845.147-2.34.346-4.235.346s-3.39-.2-4.235-.346A.93.93 0 0 1 3 9.219zm4.542-.827a.25.25 0 0 0-.217.068l-.92.9a25 25 0 0 1-1.871-.183.25.25 0 0 0-.068.495c.55.076 1.232.149 2.02.193a.25.25 0 0 0 .189-.071l.754-.736.847 1.71a.25.25 0 0 0 .404.062l.932-.97a25 25 0 0 0 1.922-.188.25.25 0 0 0-.068-.495c-.538.074-1.207.145-1.98.189a.25.25 0 0 0-.166.076l-.754.785-.842-1.7a.25.25 0 0 0-.182-.135"/>
            <path d="M8.5 1.866a1 1 0 1 0-1 0V3h-2A4.5 4.5 0 0 0 1 7.5V8a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1a1 1 0 0 0 1-1V9a1 1 0 0 0-1-1v-.5A4.5 4.5 0 0 0 10.5 3h-2zM14 7.5V13a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V7.5A3.5 3.5 0 0 1 5.5 4h5A3.5 3.5 0 0 1 14 7.5"/>
        </svg>
        <header>HelpBot: loading...</header>
        <output></output>
        <div class="progress"><div></div><div></div><div></div><div></div></div>
        <textarea placeholder="Type a message..."></textarea>
        <footer>
            <a id="new_conversation" href="#">start new conversation</a>
            <address>Powered by <a href="https://ai.ioix.net" target="_blank">HelpBot</a></address>
        </footer>
        `;

        shadow.appendChild(template.content.cloneNode(true));

        this.icon_logo = shadow.querySelector('#icon-logo');
        this.icon_close = shadow.querySelector('#icon-close');

        this.header = shadow.querySelector('header');
        this.output = shadow.querySelector('output');
        this.progress = shadow.querySelector('.progress');
        this.textarea = shadow.querySelector('textarea');
        this.new_conversation = shadow.querySelector('#new_conversation');

        this.ws = null;
        this.wsUrl = '';

    }

    connectedCallback() {
        this.assistant_id = this.getAttribute('assistant');

        this.icon_logo.addEventListener('click', (event) => {
            this.classList.add('maximized');

            if (this.assistant_id && this.ws === null) {
                setTimeout(() => this.initAssistant(this.assistant_id));
            }
        });

        this.icon_close.addEventListener('click', (event) => {
            this.classList.remove('maximized');
        });

        this.new_conversation.addEventListener('click', (event) => {
            setCookie(this.assistant_id, '', 3);  // reset cookie value
            this.initAssistant(this.assistant_id);
        });

        this.textarea.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
                if (this.textarea.value) {
                    event.preventDefault(); // Prevent adding a new line
                    this.sendMessage(this.textarea.value);
                    this.textarea.value = ''; // Clear the textarea
                }
            }
        });

        const placeholder = this.getAttribute('placeholder');
        if (placeholder) {
            this.textarea.setAttribute('placeholder', placeholder);
        }

        if (this.assistant_id && this.classList.contains('maximized')) {
            setTimeout(() => this.initAssistant(this.assistant_id));
        }
    }

    initAssistant(assistant_id) {
        const thread_id = getCookie(assistant_id);
        const wsUrl = `wss://ai.ioix.net/ws/helpbot?assistant=${assistant_id}&thread=${thread_id}`;

        if (this.wsUrl == wsUrl) {
            return
        }

        if (this.ws) {
            this.ws.close();
        }

        this.ws = new WebSocket(wsUrl);
        this.wsUrl = wsUrl;

        console.info('WebSocket connected:', this.wsUrl);

        this.classList.add('maximized');

        //   this.ws.addEventListener('open', () => {
        //     // Check for existing thread ID in cookies
        //     if (this.threadId) {
        //       // Send existing thread ID to WebSocket
        //       this.ws.send(JSON.stringify({ threadId: this.threadId }));
        //     } else {
        //       // No thread ID, wait for it from the server
        //       this.ws.send(JSON.stringify({ message: 'request-new-thread' }));
        //     }
        //   });

        // Handle incoming messages
        this.ws.addEventListener('message', (event) => {
            const msg = JSON.parse(event.data);
            if (msg.object === 'assistant') {
                this.header.innerHTML = msg.name;
                this.output.innerHTML = '';

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

    // Display messages in the output element
    displayMessage(msg) {
        const messageElem = document.createElement('div');
        messageElem.classList.add('message');
        messageElem.classList.add(`role-${msg.role}`);
        messageElem.innerHTML = markdownToHTML(msg.content);
        this.output.appendChild(messageElem);
        this.output.scrollTop = this.output.scrollHeight; // Scroll to the latest message

        if (msg.role == 'assistant') {
            this.textarea.removeAttribute('disabled');
            this.progress.style.visibility = 'hidden';
        }

    }

    // Send messages via WebSocket
    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        } else {
            console.error('WebSocket is not connected.');
        }
        this.textarea.setAttribute('disabled', 'disabled');
        this.progress.style.visibility = 'visible';
    }

    // Called when the element is removed from the DOM
    disconnectedCallback() {
        if (this.ws) {
          this.ws.close(); // Close WebSocket connection
        }
    }
}

customElements.define('help-bot', HelpBot);

document.addEventListener("DOMContentLoaded", function() {
    let helpBot = document.body.querySelector('help-bot');

    if (!helpBot) {
        helpBot = document.createElement('help-bot');
        document.body.appendChild(helpBot);
    }
    window.helpBot = helpBot;

    console.log('DOMContentLoaded', window.helpBot);
});