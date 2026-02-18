// Главный файл приложения
import { SELECTORS, MESSAGES } from './constants.js';
import { showElement, hideElement, setElementText, setElementHTML, clearElement } from './domUtils.js';
import { processFiles } from './apiService.js';
import { createStepElement, createResultHTML, createErrorHTML } from './uiComponents.js';

class App {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
    }
    
    initializeElements() {
        this.form = document.querySelector(SELECTORS.FORM);
        this.productFileInput = document.querySelector(SELECTORS.PRODUCT_FILE_INPUT);
        this.codesFileInput = document.querySelector(SELECTORS.CODES_FILE_INPUT);
        this.productFileName = document.querySelector(SELECTORS.PRODUCT_FILE_NAME);
        this.codesFileName = document.querySelector(SELECTORS.CODES_FILE_NAME);
        this.submitButton = document.querySelector(SELECTORS.SUBMIT_BUTTON);
        this.progressSection = document.querySelector(SELECTORS.PROGRESS_SECTION);
        this.resultSection = document.querySelector(SELECTORS.RESULT_SECTION);
        this.errorSection = document.querySelector(SELECTORS.ERROR_SECTION);
        this.progressSteps = document.querySelector(SELECTORS.PROGRESS_STEPS);
        this.resultContent = document.querySelector(SELECTORS.RESULT_CONTENT);
        this.errorContent = document.querySelector(SELECTORS.ERROR_CONTENT);
        this.btnText = this.submitButton?.querySelector(SELECTORS.BTN_TEXT);
        this.btnLoader = this.submitButton?.querySelector(SELECTORS.BTN_LOADER);
    }
    
    attachEventListeners() {
        if (this.productFileInput) {
            this.productFileInput.addEventListener('change', (e) => {
                this.handleFileChange(e, this.productFileName);
            });
        }
        
        if (this.codesFileInput) {
            this.codesFileInput.addEventListener('change', (e) => {
                this.handleFileChange(e, this.codesFileName);
            });
        }
        
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        }
    }
    
    handleFileChange(event, fileNameElement) {
        const fileName = event.target.files[0]?.name || MESSAGES.FILE_NOT_SELECTED;
        setElementText(fileNameElement, fileName);
    }
    
    async handleFormSubmit(event) {
        event.preventDefault();
        
        this.resetUI();
        this.setLoadingState(true);
        
        const formData = new FormData(this.form);
        
        try {
            const data = await processFiles(formData);
            
            if (data.success) {
                this.displayProgress(data.steps);
                this.displayResult(data);
            } else {
                this.displayError(data.error || MESSAGES.PROCESSING_ERROR, data.trace);
            }
        } catch (error) {
            this.displayError(MESSAGES.NETWORK_ERROR + error.message);
        } finally {
            this.setLoadingState(false);
        }
    }
    
    resetUI() {
        hideElement(this.resultSection);
        hideElement(this.errorSection);
        showElement(this.progressSection);
        clearElement(this.progressSteps);
    }
    
    setLoadingState(isLoading) {
        if (this.submitButton) {
            this.submitButton.disabled = isLoading;
        }
        
        if (this.btnText) {
            setElementText(this.btnText, isLoading ? MESSAGES.PROCESSING : MESSAGES.START_PROCESSING);
        }
        
        if (this.btnLoader) {
            this.btnLoader.style.display = isLoading ? 'inline' : 'none';
        }
    }
    
    displayProgress(steps) {
        clearElement(this.progressSteps);
        
        steps.forEach(step => {
            const stepElement = createStepElement(step);
            this.progressSteps.appendChild(stepElement);
        });
    }
    
    displayResult(data) {
        showElement(this.resultSection);
        const resultHTML = createResultHTML(data);
        setElementHTML(this.resultContent, resultHTML);
    }
    
    displayError(error, trace) {
        showElement(this.errorSection);
        const errorHTML = createErrorHTML(error, trace);
        setElementHTML(this.errorContent, errorHTML);
    }
}

// Инициализация приложения после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
