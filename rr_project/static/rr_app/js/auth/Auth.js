class Auth {
    constructor() {
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        this.tokenExpiry = localStorage.getItem('token_expiry');
        window.MessageBox.setTheme('light');
        
        if (!this.isAuthenticated()) return;
        
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
        if (!this.refreshToken) {
            console.log('No refresh token available');
            return false;
        }

        try {
            console.log('Attempting to refresh access token...');
            console.log('Old access token:', this.accessToken?.substring(0, 20) + '...');
            
            const response = await fetch('/rr/api/refresh-token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: this.refreshToken })
            });

            const responseData = await response.json();
            
            if (responseData.success && responseData.data) {
                console.log('Token refreshed successfully');
                console.log('New access token:', responseData.data.accessToken?.substring(0, 20) + '...');
                
                this.accessToken = responseData.data.accessToken;
                this.refreshToken = responseData.data.refreshToken;
                this.tokenExpiry = responseData.data.expiresAt;

                localStorage.setItem('access_token', this.accessToken);
                localStorage.setItem('refresh_token', this.refreshToken);
                localStorage.setItem('token_expiry', this.tokenExpiry);

                this.startTokenRefreshTimer();
                return true;
            } else {
                console.log('Token refresh failed:', responseData.message);
                return false;
            }
        } catch (error) {
            console.log('Token refresh error:', error);
            return false;
        }
    }

    startTokenRefreshTimer() {
        this.stopTokenRefreshTimer();
        
        if (!this.tokenExpiry) {
            console.log('No token expiry set, cannot start refresh timer');
            return;
        }

        try {
            const expiryTime = new Date(this.tokenExpiry);
            const now = new Date();
            
            if (isNaN(expiryTime.getTime())) {
                console.error('Invalid token expiry format:', this.tokenExpiry);
                return;
            }
            
            const timeUntilExpiry = expiryTime.getTime() - now.getTime();
            
            if (timeUntilExpiry <= 0) {
                console.log('Token already expired, signing out...');
                this.signOut();
                return;
            }

            const refreshTime = Math.max(timeUntilExpiry - 5 * 60 * 1000, 60000);
            
            console.log('Token refresh scheduled:');
            console.log('  - Current time:', now.toLocaleString());
            console.log('  - Expiry time:', expiryTime.toLocaleString());
            console.log('  - Time until expiry:', Math.round(timeUntilExpiry / 1000 / 60), 'minutes');
            console.log('  - Will refresh in:', Math.round(refreshTime / 1000 / 60), 'minutes');
            
            this.refreshTimer = setTimeout(async () => {
                console.log("Timer triggered — attempting token refresh...");
                const refreshed = await this.refreshAccessToken();
                if (!refreshed) {
                    console.log('Refresh failed, signing out...');
                    await this.signOut();
                }
            }, refreshTime);
        } catch (error) {
            console.error('Error starting refresh timer:', error);
        }
    }

    stopTokenRefreshTimer() {
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
            console.log('Token refresh timer stopped');
        }
    }

    async validateSession() {
        if (!this.accessToken) {
            console.log('No access token, cannot validate session');
            return;
        }

        console.log("there is a session");
        console.log("Validating session...");
        console.log("Access token:", this.accessToken?.substring(0, 20) + '...');
        
        try {
            const response = await fetch('/rr/api/validate-session', {
                method: 'GET',
                headers: this.getAuthHeaders()
            });

            const data = await response.json();
            
            if (response.ok && data.success) {
                console.log('Session is valid:', data.message);
            } else {
                console.log('Session invalid:', data.message);
                this.clearSession(); 
                // window.location.href = '/rr/sign-in';
            }
        } catch (error) {
            console.error('Session validation error:', error);
            this.clearSession();
            // window.location.href = '/rr/sign-in';
        }
    }

    async signOut(callback) {
        console.log('Signing out...');
        console.log('Auth headers:', this.getAuthHeaders());
        
        try {
            const response = await fetch('/rr/api/sign-out', {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (response.ok || response.status === 401) {
                console.log('Sign out successful');
                this.clearSession();
                callback?.();
                window.location.href = '/rr/sign-in';
            } else {
                console.log('Sign out request failed, but clearing session anyway');
                this.clearSession();
                window.location.href = '/rr/sign-in';
            }
        } catch (error) {
            console.error('Logout error:', error);
            this.clearSession();
            window.location.href = '/rr/sign-in';
        }
    }
}