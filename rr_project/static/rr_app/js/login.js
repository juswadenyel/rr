document.addEventListener('DOMContentLoaded', () => {
    const submit = document.getElementById('btnSubmit');
    const i_email = document.getElementById('email');
    const i_password = document.getElementById('password');
    const errorMsg = document.getElementById('errorMsg');
    const forgotPass = document.getElementById('forgotPassword');
    const ErrorMessage = window.ErrorMessage;
    const dataManager = window.DataManager;
    ErrorMessage.setElement(errorMsg);

    submit.addEventListener('click', async () => {
        const em_pass = {
            email: i_email.value.trim(),
            password: i_password.value.trim()
        };

        try {
            const response = await window.DataManager.postRequest('/rr/login_user/', em_pass);
            if (response.success) {
                dataManager.auth.setSession(response.session, response.user);
                alert(response.message);
            } else {
                ErrorMessage.show(response.error || "Error logging in");
            }
        } catch (err) {
            ErrorMessage.show(err);
        }
    });

    forgotPass.addEventListener('click', () => {
        window.location.href = "/rr/forgot_password/";
    });

    [i_email, i_password].forEach(field => {
        field.addEventListener('input', () => {
            ErrorMessage.remove();
        });
    });
});
