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
        let listMatch = /^(\s*)((?:[-\*\+]|\d+\.)\s+)(.*)/.exec(line);
        if (listMatch) {
            let indent = listMatch[1].length;
            let listMarker = listMatch[2].trim();
            let listType = /^\d+\.$/.test(listMarker) ? 'ol' : 'ul';
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
                let indentDiff = (indent - prevIndent) / 2;
                for (let j = 0; j < indentDiff; j++) {
                    result += `<${listType}><li>`;
                    listStack.push({ type: listType, hasOpenLi: true });
                }
            } else if (indent < prevIndent) {
                let indentDiff = (prevIndent - indent) / 2;
                for (let j = 0; j < indentDiff; j++) {
                    let lastList = listStack.pop();
                    if (lastList.hasOpenLi) {
                        result += '</li>';
                    }
                    result += `</${lastList.type}>`;
                }
                result += '</li><li>';
                listStack[listStack.length - 1].hasOpenLi = true;
            } else {
                // Закрываем предыдущий <li>, если он открыт
                if (listStack.length > 0 && listStack[listStack.length - 1].hasOpenLi) {
                    result += '</li><li>';
                } else {
                    result += '<li>';
                    if (listStack.length > 0) {
                        listStack[listStack.length - 1].hasOpenLi = true;
                    }
                }
            }
            result += content;
            prevIndent = indent;
            continue;
        } else {
            // Закрываем открытые списки перед обработкой обычного текста
            while (listStack.length > 0) {
                let lastList = listStack.pop();
                if (lastList.hasOpenLi) {
                    result += '</li>';
                }
                result += `</${lastList.type}>`;
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
        if (lastList.hasOpenLi) {
            result += '</li>';
        }
        result += `</${lastList.type}>`;
    }

    return result;
}