/**
 * api.js
 * 중앙 집중식 API 호출 유틸리티
 */

const API_BASE_URL = '/api';

const api = {
    // GET 요청 헬퍼
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'API 요청 실패');
            }
            return data;
        } catch (error) {
            console.error(`GET ${endpoint} Error:`, error);
            throw error;
        }
    },

    // POST 요청 헬퍼
    async post(endpoint, body) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'API 요청 실패');
            }
            return data;
        } catch (error) {
            console.error(`POST ${endpoint} Error:`, error);
            throw error;
        }
    },

    // PUT 요청 헬퍼
    async put(endpoint, body) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || 'API 요청 실패');
            }
            return data;
        } catch (error) {
            console.error(`PUT ${endpoint} Error:`, error);
            throw error;
        }
    },

    // DELETE 요청 헬퍼
    async delete(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'DELETE'
            });
            // DELETE는 보통 204 No Content를 반환하므로 json 파싱을 시도하지 않거나 조건부로 처리합니다.
            if (!response.ok) {
                const data = await response.json().catch(() => ({}));
                throw new Error(data.error || 'API 요청 실패');
            }
            return true;
        } catch (error) {
            console.error(`DELETE ${endpoint} Error:`, error);
            throw error;
        }
    },

    // 파일 업로드 (FormData) 요청 헬퍼
    async upload(endpoint, formData, method = 'POST') {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: method,
                body: formData // FormData는 Content-Type 헤더를 브라우저가 자동 설정해야 함
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || '파일 업로드 실패');
            }
            return data;
        } catch (error) {
            console.error(`UPLOAD ${endpoint} Error:`, error);
            throw error;
        }
    }
};

window.api = api;
