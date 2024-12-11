function markdownToHtml(markdown) {
    let result = '';
    let pos = 0;
    let length = markdown.length;
    let buffer = '';
    let listStack = [];
    let prevIndent = 0;
    let inCodeBlock = false;
    let codeBlockLanguage = '';
    let inParagraph = false;

    while (pos <= length) {
        let char = markdown[pos] || '\n'; // Добавляем '\n' в конце для обработки последней строки
        buffer += char;

        if (char === '\n' || pos === length) {
            let line = buffer.replace(/\r?\n$/, '');
            buffer = '';

            // Определяем текущий отступ
            let indentMatch = line.match(/^(\s*)/);
            let indent = indentMatch ? indentMatch[1].length : 0;
            let content = line.trim();

            // Обработка пустых строк
            if (content === '') {
                // Закрываем параграф, если он открыт
                if (inParagraph) {
                    result += '</p>\n';
                    inParagraph = false;
                }
                pos++;
                continue;
            }

            // Обработка кода (блочного)
            if (content.startsWith('```')) {
                if (inCodeBlock) {
                    // Закрываем кодовый блок
                    result += '</code></pre>\n';
                    inCodeBlock = false;
                    codeBlockLanguage = '';
                } else {
                    // Открываем кодовый блок
                    codeBlockLanguage = content.slice(3).trim();
                    result += `<pre><code class="${codeBlockLanguage}">\n`;
                    inCodeBlock = true;
                }
                pos++;
                continue;
            }

            if (inCodeBlock) {
                // Внутри кодового блока добавляем текст как есть
                result += line + '\n';
                pos++;
                continue;
            }

            // Обработка заголовков
            let headingMatch = content.match(/^(#{1,6})\s+(.*)/);
            if (headingMatch) {
                let level = headingMatch[1].length;
                let headingText = headingMatch[2];
                headingText = processInlineElements(headingText);
                result += `<h${level}>${headingText}</h${level}>\n`;
                pos++;
                continue;
            }

            // Обработка горизонтальных линий
            if (/^(-{3,}|\*{3,}|_{3,})$/.test(content)) {
                result += '<hr>\n';
                pos++;
                continue;
            }

            // Обработка цитат
            if (content.startsWith('>')) {
                let quoteText = content.replace(/^>\s?/, '');
                quoteText = processInlineElements(quoteText);
                result += `<blockquote>${quoteText}</blockquote>\n`;
                pos++;
                continue;
            }

            // Обработка списков
            let listMatch = content.match(/^(\s*)([-*+]|\d+\.)\s+(.*)/);
            if (listMatch) {
                let currentIndent = listMatch[1].length;
                let marker = listMatch[2];
                let listItemText = listMatch[3];

                // Определяем тип списка
                let listType = /^\d+\.$/.test(marker) ? 'ol' : 'ul';

                // Управление вложенностью списков
                if (currentIndent > prevIndent) {
                    result += `<${listType}>\n`;
                    listStack.push({ type: listType, indent: currentIndent });
                } else if (currentIndent < prevIndent) {
                    while (listStack.length > 0 && currentIndent < prevIndent) {
                        let lastList = listStack.pop();
                        result += '</li>\n';
                        result += `</${lastList.type}>\n`;
                        prevIndent = lastList.indent - 2;
                    }
                } else {
                    if (result.endsWith('</li>\n')) {
                        result = result.slice(0, -6);
                        result += '</li>\n';
                    }
                }

                // Добавляем элемент списка
                listItemText = processInlineElements(listItemText);
                result += `<li>${listItemText}\n`;
                prevIndent = currentIndent;
                pos++;
                continue;
            } else {
                // Закрываем открытые списки
                while (listStack.length > 0) {
                    let lastList = listStack.pop();
                    result += '</li>\n';
                    result += `</${lastList.type}>\n`;
                }
                prevIndent = 0;
            }

            // Обработка параграфов
            content = processInlineElements(content);
            if (!inParagraph) {
                result += `<p>${content}`;
                inParagraph = true;
            } else {
                result += ' ' + content;
            }

            pos++;
            // Если следующая строка пустая, закрываем параграф
            if ((markdown[pos] || '').match(/^\s*$/)) {
                result += '</p>\n';
                inParagraph = false;
            }
        } else {
            pos++;
        }
    }

    // Закрываем открытые элементы
    if (inParagraph) {
        result += '</p>\n';
    }
    while (listStack.length > 0) {
        let lastList = listStack.pop();
        result += '</li>\n';
        result += `</${lastList.type}>\n`;
    }
    if (inCodeBlock) {
        result += '</code></pre>\n';
    }

    return result;
}

function processInlineElements(text) {
    // Экранирование специальных символов в HTML
    text = text.replace(/&/g, '&amp;');
    text = text.replace(/</g, '&lt;');
    text = text.replace(/>/g, '&gt;');

    // Изображения
    text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');
    // Ссылки
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
    // Жирный и курсивный текст
    text = text.replace(/(\*\*\*|___)(.+?)\1/g, '<strong><em>$2</em></strong>'); // Жирный курсив
    text = text.replace(/(\*\*|__)(.+?)\1/g, '<strong>$2</strong>'); // Жирный
    text = text.replace(/(\*|_)(.+?)\1/g, '<em>$2</em>'); // Курсив
    // Инлайновый код
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

    return text;
}