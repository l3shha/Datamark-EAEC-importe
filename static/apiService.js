// Сервис для работы с API
import { API_ENDPOINTS } from './constants.js';

export const processFiles = async (formData) => {
    const response = await fetch(API_ENDPOINTS.PROCESS, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
};
