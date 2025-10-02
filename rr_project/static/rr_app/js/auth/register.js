document.addEventListener('DOMContentLoaded', () => {
    const submit = document.getElementById('btnSubmit');
    const first_name = document.getElementById('firstName');
    const last_name = document.getElementById('lastName');
    const i_email = document.getElementById('email');
    const i_password = document.getElementById('password');
    const i_c_password = document.getElementById('cPassword');
    const user = {}

    submit.addEventListener('click', () => {
        user.first_name = first_name.value.trim();
        user.last_name = last_name.value.trim();
        const password = i_password.value.trim();
        const c_password = i_c_password.value.trim();
        const email = i_email.value.trim();

        user.email = email;
        user.password = password;
        user.c_password = c_password;
        window.DataManager.postRequest('/rr/register_user/', user).then(
            response => {
                if (response.success) {
                    submit.disabled = true;
                    window.MessageBox.showSuccess(response.message, ()=> {
                        window.location.href = "/rr/login/";
                    });
                } else {
                    window.ErrorMessage.show(response.error || 'Error creating user');
                    submit.disabled = false;
                }
            }
        );
    });

    const inputs = [i_email, i_password, i_c_password];
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
            window.window.ErrorMessage.remove();
        });
    });
});
