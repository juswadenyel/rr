class Auth {
    constructor() {
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        this.tokenExpiry = localStorage.getItem('token_expiry');
        window.MessageBox.setTheme('light');
        if(!this.isAuthenticated()) return;
        this.validateSession();
        this.startTokenRefreshTimer();
    }

    isAuthenticated() {
        return this.accessToken != null && this.user != null;
    }

    setSession(session, user) {
        this.accessToken = session.accessToken;
        this.refreshToken = session.refreshToken;
        this.user = user;
        this.tokenExpiry = session.expiresAt;

        // Store in localStorage
        localStorage.setItem('access_token', this.accessToken);
        localStorage.setItem('refresh_token', this.refreshToken);
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('token_expiry', this.tokenExpiry);

        this.startTokenRefreshTimer();
    }

    clearSession() {
        this.accessToken = null;
        this.refreshToken = null;
        this.user = null;
        this.tokenExpiry = null;

        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        localStorage.removeItem('token_expiry');

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
            const response = await fetch('/rr/api/refresh-token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: this.refreshToken })
            });

            const responseData = await response.json();
            console.log(responseData);
            console.log("old access token: " + this.accessToken);
            if (response.ok && responseData.data) {
                
            console.log("new access token: " + this.accessToken);
                this.accessToken = responseData.data.accessToken;
                this.refreshToken = responseData.data.refreshToken;
                this.tokenExpiry = responseData.data.expiresAt;

                localStorage.setItem('access_token', this.accessToken);
                localStorage.setItem('refresh_token', this.refreshToken);
                localStorage.setItem('token_expiry', this.tokenExpiry);

                this.startTokenRefreshTimer();
                return true;
            }
        } catch (error) {
            console.log('Token refresh failed:', error);
        }

        return false;
    }

    startTokenRefreshTimer() {
        this.stopTokenRefreshTimer();
        if (!this.tokenExpiry) return;

        // Parse ISO LocalDateTime from backend
        const expiryTime = new Date(this.tokenExpiry);
        const now = new Date();
        const timeUntilExpiry = expiryTime.getTime() - now.getTime();

        // Refresh 5 minutes before expiry
        const refreshTime = Math.max(timeUntilExpiry - 5 * 60 * 1000, 60000);
        console.log("expiry time: " + expiryTime);
        console.log("Refresh time: " + refreshTime);
        this.refreshTimer = setTimeout(async () => {
            console.log("🔄 Timer triggered — attempting token refresh...");
            const refreshed = await this.refreshAccessToken();
            if (!refreshed) {
                await this.signOut();
            }
        }, refreshTime);
    }

    stopTokenRefreshTimer() {
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    async validateSession() {
        console.log("access token: " + this.accessToken);
        try {
            const response = await fetch('/rr/api/validate-session', {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            if(!response.ok){
                this.clearSession(); 
                window.location.href = '/rr/sign-in';
            }else{
                console.log(await response.json());
            }
        } catch (error) {
            this.clearSession();
            window.location.href = '/rr/sign-in';
        }
    }


    async signOut(callback) {
        console.log(this.getAuthHeaders());
        try {
            const response = await fetch('/rr/api/sign-out', {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            if (response.ok || response.status === 401){
                window.location.href = '/rr/sign-in';
                callback?.();
            }
        } catch (error) {
            console.error('Logout error:', error);
            window.location.href = '/rr/sign-in'
        } finally {
            this.clearSession();
        }
    }
}