class DataManager {
    constructor() {
        this.auth = new SupabaseAuth();
    }

    async postRequest(url, data, requireAuth = false) {
        const headers = requireAuth ? this.auth.getAuthHeaders() : {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCSRFToken()
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: JSON.stringify(data)
            });

            if (response.status === 401 && requireAuth) {
                // Try to refresh token
                const refreshed = await this.auth.refreshAccessToken();
                if (refreshed) {
                    // Retry request with new token
                    const retryHeaders = this.auth.getAuthHeaders();
                    const retryResponse = await fetch(url, {
                        method: 'POST',
                        headers: retryHeaders,
                        body: JSON.stringify(data)
                    });
                    return retryResponse.json();
                } else {
                    // Refresh failed, redirect to login
                    this.auth.clearSession();
                    window.location.href = '/rr/login/';
                    return { success: false, error: 'Authentication required' };
                }
            }

            return response.json();
        } catch (error) {
            console.error('Request error:', error);
            return { success: false, error: error.message };
        }
    }

    async getRequest(url, requireAuth = false) {
        const headers = requireAuth ? this.auth.getAuthHeaders() : {
            'Content-Type': 'application/json'
        };

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers
            });

            if (response.status === 401 && requireAuth) {
                const refreshed = await this.auth.refreshAccessToken();
                if (refreshed) {
                    const retryResponse = await fetch(url, {
                        method: 'GET',
                        headers: this.auth.getAuthHeaders()
                    });
                    return retryResponse.json();
                } else {
                    this.auth.clearSession();
                    window.location.href = '/rr/login/';
                    return { success: false, error: 'Authentication required' };
                }
            }

            return response.json();
        } catch (error) {
            console.error('Request error:', error);
            return { success: false, error: error.message };
        }
    }

    getCSRFToken() {
        let cookieValue = null;
        const name = 'csrftoken';
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}