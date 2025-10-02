class SupabaseAuth {
    constructor() {
        this.accessToken = localStorage.getItem('supabase_access_token');
        this.refreshToken = localStorage.getItem('supabase_refresh_token');
        this.user = JSON.parse(localStorage.getItem('supabase_user') || 'null');
        this.tokenExpiry = localStorage.getItem('supabase_token_expiry');
        
        // Auto-refresh token before expiry
        this.startTokenRefreshTimer();
    }

    setSession(session, user) {
        this.accessToken = session.access_token;
        this.refreshToken = session.refresh_token;
        this.user = user;
        this.tokenExpiry = session.expires_at;
        
        // Store in localStorage
        localStorage.setItem('supabase_access_token', this.accessToken);
        localStorage.setItem('supabase_refresh_token', this.refreshToken);
        localStorage.setItem('supabase_user', JSON.stringify(user));
        localStorage.setItem('supabase_token_expiry', this.tokenExpiry);
        
        this.startTokenRefreshTimer();
    }

    clearSession() {
        this.accessToken = null;
        this.refreshToken = null;
        this.user = null;
        this.tokenExpiry = null;
        
        localStorage.removeItem('supabase_access_token');
        localStorage.removeItem('supabase_refresh_token');
        localStorage.removeItem('supabase_user');
        localStorage.removeItem('supabase_token_expiry');
        
        this.stopTokenRefreshTimer();
    }

    getAuthHeaders() {
        if (!this.accessToken) return {};
        return {
            'Authorization': `Bearer ${this.accessToken}`,
            'Content-Type': 'application/json'
        };
    }

    async refreshAccessToken() {
        if (!this.refreshToken) return false;
        
        try {
            const response = await fetch('/rr/refresh_token/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: this.refreshToken })
            });
            
            const data = await response.json();
            if (data.success && data.session) {
                this.accessToken = data.session.access_token;
                this.refreshToken = data.session.refresh_token;
                this.tokenExpiry = data.session.expires_at;
                
                localStorage.setItem('supabase_access_token', this.accessToken);
                localStorage.setItem('supabase_refresh_token', this.refreshToken);
                localStorage.setItem('supabase_token_expiry', this.tokenExpiry);
                
                this.startTokenRefreshTimer();
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }
        
        return false;
    }

    startTokenRefreshTimer() {
        this.stopTokenRefreshTimer();
        
        if (!this.tokenExpiry) return;
        
        const expiryTime = new Date(this.tokenExpiry * 1000);
        const now = new Date();
        const timeUntilExpiry = expiryTime.getTime() - now.getTime();
        
        // Refresh 5 minutes before expiry
        const refreshTime = Math.max(timeUntilExpiry - 5 * 60 * 1000, 60000); // Min 1 minute
        
        this.refreshTimer = setTimeout(async () => {
            const refreshed = await this.refreshAccessToken();
            if (!refreshed) {
                // Refresh failed, redirect to login
                this.clearSession();
                window.location.href = '/rr/login/';
            }
        }, refreshTime);
    }

    stopTokenRefreshTimer() {
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    isAuthenticated() {
        return !!this.accessToken && !!this.user;
    }

    async signOut() {
        try {
            await fetch('/rr/logout/', {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.clearSession();
        }
    }
}