import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
    baseURL: '/api',
    headers: { 'Content-Type': 'application/json' },
})

// Request interceptor — attach JWT
api.interceptors.request.use((config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Response interceptor — handle 401
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true
            try {
                const refreshToken = useAuthStore.getState().refreshToken
                if (refreshToken) {
                    const { data } = await axios.post('/api/auth/refresh', {
                        refresh_token: refreshToken,
                    })
                    useAuthStore.getState().setTokens(data.access_token, data.refresh_token)
                    originalRequest.headers.Authorization = `Bearer ${data.access_token}`
                    return api(originalRequest)
                }
            } catch {
                useAuthStore.getState().logout()
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

// ============== Auth ==============
export const authAPI = {
    signup: (data) => api.post('/auth/signup', data),
    login: (data) => api.post('/auth/login', data),
    me: () => api.get('/auth/me'),
    refresh: (token) => api.post('/auth/refresh', { refresh_token: token }),
    logout: (token) => api.post('/auth/logout', { refresh_token: token }),
}

// ============== Campaigns ==============
export const campaignAPI = {
    list: (params) => api.get('/campaigns', { params }),
    get: (id) => api.get(`/campaigns/${id}`),
    create: (data) => api.post('/campaigns', data),
    update: (id, data) => api.put(`/campaigns/${id}`, data),
    delete: (id) => api.delete(`/campaigns/${id}`),
    generateOutreach: (id) => api.post(`/campaigns/${id}/generate-outreach`),
    regenerateEmails: (id) => api.post(`/campaigns/${id}/email/regenerate`),
    uploadCSV: (id, file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post(`/campaigns/${id}/upload-csv`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },
    sendTest: (id, email) => api.post(`/campaigns/${id}/test-email`, { to_email: email }),
}

// ============== Companies ==============
export const companyAPI = {
    list: (params) => api.get('/company', { params }),
    get: (id) => api.get(`/company/${id}`),
    create: (data) => api.post('/company', data),
    update: (id, data) => api.put(`/company/${id}`, data),
}

// ============== Emails ==============
export const emailAPI = {
    listByCampaign: (campaignId) => api.get(`/campaigns/${campaignId}/emails`),
    get: (id) => api.get(`/emails/${id}`),
    update: (id, data) => api.put(`/emails/${id}`, data),
    send: (campaignId, data) => api.post(`/campaigns/${campaignId}/emails/send`, data),
    sendTest: (id, data) => api.post(`/emails/${id}/test`, data),
}

// ============== Analytics ==============
export const analyticsAPI = {
    campaigns: () => api.get('/analytics/campaigns'),
    sponsors: () => api.get('/analytics/sponsors'),
    eventStats: () => api.get('/analytics/events/stats'),
}

// ============== Sponsors ==============
export const sponsorAPI = {
    list: (params) => api.get('/sponsors', { params }),
    get: (id) => api.get(`/sponsors/${id}`),
}

// ============== Insights ==============
export const insightAPI = {
    list: () => api.get('/insights'),
    getReport: (id) => api.get(`/insights/${id}/report`),
    collectData: () => api.post('/insights/collect-data'),
}

export default api
