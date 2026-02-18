// Утилиты для работы с DOM
export const escapeHtml = (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

export const createElement = (tag, className, content) => {
    const element = document.createElement(tag);
    if (className) {
        element.className = className;
    }
    if (content) {
        element.innerHTML = content;
    }
    return element;
};

export const showElement = (element) => {
    if (element) {
        element.style.display = 'block';
    }
};

export const hideElement = (element) => {
    if (element) {
        element.style.display = 'none';
    }
};

export const setElementText = (element, text) => {
    if (element) {
        element.textContent = text;
    }
};

export const setElementHTML = (element, html) => {
    if (element) {
        element.innerHTML = html;
    }
};

export const clearElement = (element) => {
    if (element) {
        element.innerHTML = '';
    }
};
