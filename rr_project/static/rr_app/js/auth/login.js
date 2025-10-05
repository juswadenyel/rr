document.addEventListener('DOMContentLoaded', () => {
    const submit = document.getElementById('btnSubmit');
    const i_email = document.getElementById('email');
    const i_password = document.getElementById('password');
    const forgotPass = document.getElementById('forgotPassword');
    const dataManager = window.DataManager;

    submit.addEventListener('click', async () => {
        submit.disabled = true;
        const em_pass = {
            email: i_email.value.trim(),
            password: i_password.value.trim()
        };

        try {
            const response = await window.DataManager.postRequest('/rr/login_user/', em_pass);
            if (response.success) {
                dataManager.auth.setSession(response.session, response.user);
                window.MessageBox.showSuccess(response.message, ()=> {
                    // logic to dashboard
                    // fow now, just close the Messagebox
                    window.MessageBox.hide();
                });
            } else {
                window.ErrorMessage.show(response.error || "Error logging in");
                submit.disabled = false;
            }
        } catch (err) {
            window.ErrorMessage.show(err);
        }
    });

    forgotPass.addEventListener('click', () => {
        window.location.href = "/rr/forgot_password/";
    });

    const inputs = [i_email, i_password];

    inputs.forEach((field, index) => {
        field.addEventListener('keydown', (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                const next = inputs[index + 1];
                if (next) {
                    next.focus();
                } else {
                    submit.click();
                }
            }
        });
        field.addEventListener('input', () => {
            window.ErrorMessage.remove();
        });
    });
});
