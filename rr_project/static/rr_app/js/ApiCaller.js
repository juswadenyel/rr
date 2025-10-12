class ApiCaller {
    constructor() {
        this.auth = new Auth();
        console.log("Api called instantiated");
    }
    async postRequest(url, data, requireAuth = false, loadingText = 'Processing...') {
        window.LoadingOverlay.show(loadingText);

        const headers = requireAuth ? this.auth.getAuthHeaders() : {
            'Content-Type': 'application/json'
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data)
            })

            const jsonData = await response.json();

            if (response.ok) {
                return jsonData;
            } else {
                return {
                    success: false,
                    message: jsonData.message || 'An error occurred',
                    ...jsonData
                };
            }

        } catch (e) {
            return { success: false, message: e.message }
        } finally {
            window.LoadingOverlay.hide();
        }
    }

    async getRequest(url, requireAuth = false, loadingText = 'Loading...') {
        window.LoadingOverlay.show(loadingText);
        const headers = requireAuth ? this.auth.getAuthHeaders() : {
            'Content-Type': 'application/json'
        };

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: headers,
            })
            return await response.json();
        } catch (e) {
            return { success: false, message: e.message };
        } finally {
            window.LoadingOverlay.hide();
        }
    }
}

window.ApiCaller = new ApiCaller();