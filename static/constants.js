// Константы приложения
export const API_ENDPOINTS = {
    PROCESS: '/api/process'
};

export const STEP_STATUS = {
    IN_PROGRESS: 'in_progress',
    COMPLETED: 'completed',
    FAILED: 'failed',
    WARNING: 'warning'
};

export const STATUS_ICONS = {
    [STEP_STATUS.COMPLETED]: '✅',
    [STEP_STATUS.FAILED]: '❌',
    [STEP_STATUS.WARNING]: '⚠️',
    [STEP_STATUS.IN_PROGRESS]: '⏳',
    default: '⏸️'
};

export const MESSAGES = {
    FILE_NOT_SELECTED: 'Файл не выбран',
    PROCESSING: 'Обработка...',
    START_PROCESSING: 'Начать обработку',
    NETWORK_ERROR: 'Ошибка сети: ',
    PROCESSING_ERROR: 'Произошла ошибка при обработке',
    SUCCESS_COMPLETED: 'Успешно завершено',
    PARTIAL_COMPLETED: 'Частично завершено'
};

export const SELECTORS = {
    FORM: '#uploadForm',
    PRODUCT_FILE_INPUT: '#product_file',
    CODES_FILE_INPUT: '#codes_file',
    PRODUCT_FILE_NAME: '#productFileName',
    CODES_FILE_NAME: '#codesFileName',
    SUBMIT_BUTTON: '#submitBtn',
    PROGRESS_SECTION: '#progressSection',
    RESULT_SECTION: '#resultSection',
    ERROR_SECTION: '#errorSection',
    PROGRESS_STEPS: '#progressSteps',
    PROGRESS_DETAILS: '#progressDetails',
    RESULT_CONTENT: '#resultContent',
    ERROR_CONTENT: '#errorContent',
    BTN_TEXT: '.btn-text',
    BTN_LOADER: '.btn-loader'
};
