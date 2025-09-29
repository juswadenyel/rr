document.addEventListener('DOMContentLoaded', () => {
    const btnSubmit = document.getElementById('btnSubmit');
    const i_password = document.getElementById('password');
    const i_c_password = document.getElementById('c_password');
    const error_msg = document.getElementById('errorMsg');
    const dataManager = window.DataManager;
    const ErrorMessage = window.ErrorMessage;
    ErrorMessage.setElement(error_msg);

    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    const access_token = params.get('access_token');

    btnSubmit.addEventListener('click', async () => {
            const password = i_password.value.trim();
            const c_password = i_c_password.value.trim();
            try {
                const response = await dataManager.postRequest('/rr/reset_password/', { email, password, c_password, access_token });
                if (response.success) {
                    alert(response.message);
                    i_email.style.display = 'none';
                } else {
                    ErrorMessage.show(response.error || 'Failed to send reset email');
                }
            } catch (error) {
                ErrorMessage.show('Network error occurred');
                console.error('Password reset error:', error);
            }
        });
});
