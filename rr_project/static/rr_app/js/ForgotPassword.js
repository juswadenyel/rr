document.addEventListener('DOMContentLoaded', () => {
    const i_email = document.getElementById('email');
    const btnSubmit = document.getElementById('btnSubmit');
    const error_msg = document.getElementById('errorMsg');
    const dataManager = window.DataManager;
    const ErrorMessage = window.ErrorMessage;
    ErrorMessage.setElement(error_msg);

    btnSubmit.addEventListener('click', async () => {
            const email = i_email.value.trim();

            try {
                const response = await dataManager.postRequest('/rr/fpass_request/', { email });

                if (response.success) {
                    alert(response.message);
                } else {
                    ErrorMessage.show(response.error || 'Failed to send reset email');
                }
            } catch (error) {
                ErrorMessage.show('Network error occurred');
                console.error('Password reset error:', error);
            }
        });
});
