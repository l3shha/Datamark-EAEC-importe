document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const productFileInput = document.getElementById('product_file');
    const codesFileInput = document.getElementById('codes_file');
    const productFileName = document.getElementById('productFileName');
    const codesFileName = document.getElementById('codesFileName');
    const submitBtn = document.getElementById('submitBtn');
    const progressSection = document.getElementById('progressSection');
    const resultSection = document.getElementById('resultSection');
    const errorSection = document.getElementById('errorSection');
    const progressSteps = document.getElementById('progressSteps');
    const progressDetails = document.getElementById('progressDetails');
    const resultContent = document.getElementById('resultContent');
    const errorContent = document.getElementById('errorContent');

    // Обновление имени файла при выборе
    productFileInput.addEventListener('change', function(e) {
        const fileName = e.target.files[0]?.name || 'Файл не выбран';
        productFileName.textContent = fileName;
    });

    codesFileInput.addEventListener('change', function(e) {
        const fileName = e.target.files[0]?.name || 'Файл не выбран';
        codesFileName.textContent = fileName;
    });

    // Обработка отправки формы
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Скрыть предыдущие результаты
        resultSection.style.display = 'none';
        errorSection.style.display = 'none';
        progressSection.style.display = 'block';
        progressSteps.innerHTML = '';
        progressDetails.innerHTML = '';

        // Блокировка кнопки
        submitBtn.disabled = true;
        submitBtn.querySelector('.btn-text').textContent = 'Обработка...';
        submitBtn.querySelector('.btn-loader').style.display = 'inline';

        const formData = new FormData(form);

        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                displayProgress(data.steps);
                displayResult(data);
            } else {
                displayError(data.error || 'Произошла ошибка при обработке', data.trace);
            }
        } catch (error) {
            displayError('Ошибка сети: ' + error.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').textContent = 'Начать обработку';
            submitBtn.querySelector('.btn-loader').style.display = 'none';
        }
    });

    function displayProgress(steps) {
        progressSteps.innerHTML = '';
        
        steps.forEach(step => {
            const stepElement = document.createElement('div');
            stepElement.className = `step ${step.status}`;
            
            const statusIcon = getStatusIcon(step.status);
            
            stepElement.innerHTML = `
                <div class="step-number">${step.step}</div>
                <div class="step-content">
                    <div class="step-name">${step.name}</div>
                    ${step.error ? `<div class="step-details" style="color: #f44336;">Ошибка: ${step.error}</div>` : ''}
                    ${step.order_id ? `<div class="step-details">ID заказа: ${step.order_id}</div>` : ''}
                    ${step.codes_count ? `<div class="step-details">Загружено кодов: ${step.codes_count}</div>` : ''}
                    ${step.reports ? `<div class="step-details">Отправлено отчетов: ${step.reports.length}</div>` : ''}
                </div>
                <div class="step-status">${statusIcon}</div>
            `;
            
            progressSteps.appendChild(stepElement);
        });
    }

    function getStatusIcon(status) {
        switch(status) {
            case 'completed':
                return '✅';
            case 'failed':
                return '❌';
            case 'warning':
                return '⚠️';
            case 'in_progress':
                return '⏳';
            default:
                return '⏸️';
        }
    }

    function displayResult(data) {
        resultSection.style.display = 'block';
        
        const statusBadge = data.final_status === 'completed' 
            ? '<span class="success-badge">Успешно завершено</span>'
            : '<span class="success-badge" style="background: #ff9800;">Частично завершено</span>';
        
        let html = statusBadge;
        
        html += `<div class="info-item">
            <span class="info-label">Товаров обработано:</span> ${data.products_count}
        </div>`;
        
        html += `<div class="info-item">
            <span class="info-label">Кодов загружено:</span> ${data.codes_count}
        </div>`;
        
        html += `<div class="info-item">
            <span class="info-label">GTIN:</span> ${data.gtins.join(', ')}
        </div>`;
        
        if (data.codes_to_order && Object.keys(data.codes_to_order).length > 0) {
            html += `<div class="info-item">
                <span class="info-label">Заказано кодов:</span><br>`;
            for (const [gtin, quantity] of Object.entries(data.codes_to_order)) {
                html += `GTIN ${gtin}: ${quantity} шт.<br>`;
            }
            html += `</div>`;
        }
        
        // Информация о последнем шаге с отчетами
        const reportStep = data.steps.find(s => s.reports);
        if (reportStep && reportStep.reports) {
            html += `<div class="info-item">
                <span class="info-label">Отчеты о вводе в оборот:</span><br>`;
            reportStep.reports.forEach(report => {
                html += `GTIN ${report.gtin}: ID отчета ${report.report_id} (${report.codes_count} кодов)<br>`;
            });
            html += `</div>`;
        }
        
        resultContent.innerHTML = html;
    }

    function displayError(error, trace) {
        errorSection.style.display = 'block';
        let errorHtml = `<div class="error-content">${escapeHtml(error)}</div>`;
        
        if (trace) {
            errorHtml += `<details style="margin-top: 15px;">
                <summary style="cursor: pointer; color: #666;">Подробности ошибки</summary>
                <pre style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 4px; overflow-x: auto;">${escapeHtml(trace)}</pre>
            </details>`;
        }
        
        errorContent.innerHTML = errorHtml;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
