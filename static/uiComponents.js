// UI компоненты для отображения прогресса и результатов
import { STEP_STATUS, STATUS_ICONS, MESSAGES } from './constants.js';
import { createElement, escapeHtml } from './domUtils.js';

export const createStepElement = (step) => {
    const stepElement = createElement('div', `step ${step.status}`);
    
    const statusIcon = getStatusIcon(step.status);
    
    const stepDetails = buildStepDetails(step);
    
    stepElement.innerHTML = `
        <div class="step-number">${step.step}</div>
        <div class="step-content">
            <div class="step-name">${escapeHtml(step.name)}</div>
            ${stepDetails}
        </div>
        <div class="step-status">${statusIcon}</div>
    `;
    
    return stepElement;
};

const getStatusIcon = (status) => {
    return STATUS_ICONS[status] || STATUS_ICONS.default;
};

const buildStepDetails = (step) => {
    const details = [];
    
    if (step.error) {
        details.push(`<div class="step-details" style="color: #f44336;">Ошибка: ${escapeHtml(step.error)}</div>`);
    }
    
    if (step.order_id) {
        details.push(`<div class="step-details">ID заказа: ${escapeHtml(step.order_id)}</div>`);
    }
    
    if (step.codes_count) {
        details.push(`<div class="step-details">Загружено кодов: ${step.codes_count}</div>`);
    }
    
    if (step.reports && step.reports.length > 0) {
        details.push(`<div class="step-details">Отправлено отчетов: ${step.reports.length}</div>`);
    }
    
    return details.join('');
};

export const createResultHTML = (data) => {
    const statusBadge = data.final_status === 'completed' 
        ? `<span class="success-badge">${MESSAGES.SUCCESS_COMPLETED}</span>`
        : `<span class="success-badge" style="background: #ff9800;">${MESSAGES.PARTIAL_COMPLETED}</span>`;
    
    const infoItems = [
        createInfoItem('Товаров обработано:', data.products_count),
        createInfoItem('Кодов загружено:', data.codes_count),
        createInfoItem('GTIN:', data.gtins.join(', '))
    ];
    
    if (data.codes_to_order && Object.keys(data.codes_to_order).length > 0) {
        const codesOrdered = Object.entries(data.codes_to_order)
            .map(([gtin, quantity]) => `GTIN ${gtin}: ${quantity} шт.`)
            .join('<br>');
        infoItems.push(createInfoItem('Заказано кодов:', codesOrdered, true));
    }
    
    const reportStep = data.steps.find(step => step.reports);
    if (reportStep && reportStep.reports) {
        const reportsInfo = reportStep.reports
            .map(report => `GTIN ${report.gtin}: ID отчета ${report.report_id} (${report.codes_count} кодов)`)
            .join('<br>');
        infoItems.push(createInfoItem('Отчеты о вводе в оборот:', reportsInfo, true));
    }
    
    return statusBadge + infoItems.join('');
};

const createInfoItem = (label, value, isMultiline = false) => {
    const valueTag = isMultiline ? value : escapeHtml(String(value));
    return `
        <div class="info-item">
            <span class="info-label">${escapeHtml(label)}</span> ${valueTag}
        </div>
    `;
};

export const createErrorHTML = (error, trace) => {
    let errorHtml = `<div class="error-content">${escapeHtml(error)}</div>`;
    
    if (trace) {
        errorHtml += `
            <details style="margin-top: 15px;">
                <summary style="cursor: pointer; color: #666;">Подробности ошибки</summary>
                <pre style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 4px; overflow-x: auto;">${escapeHtml(trace)}</pre>
            </details>
        `;
    }
    
    return errorHtml;
};
