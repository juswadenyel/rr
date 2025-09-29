document.addEventListener('DOMContentLoaded', () => {
    const submit = document.getElementById('btnSubmit');
    const first_name = document.getElementById('firstName');
    const last_name = document.getElementById('lastName');
    const i_email = document.getElementById('email');
    const i_password = document.getElementById('password');
    const i_c_password = document.getElementById('cPassword');
    const user = {}
    const dataManager = window.DataManager;
    const error_msg = document.getElementById('errorMsg');
    const ErrorMessage = window.ErrorMessage;
    ErrorMessage.setElement(error_msg);

    submit.addEventListener('click', () => {
        user.first_name = first_name.value.trim();
        user.last_name = last_name.value.trim();
        const password = i_password.value.trim();
        const c_password = i_c_password.value.trim();
        const email = i_email.value.trim();

        user.email = email;
        user.password = password;
        user.c_password = c_password;
        dataManager.postRequest('/rr/register_user/', user).then(
            response => {
                if (response.success) {
                    alert(response.message)
                    window.location.href = "/rr/login/";
                } else {
                    ErrorMessage.show(response.error || 'Error creating user');
                }
            }
        );
    });

    i_email.addEventListener('input', () => {
        if (error_msg.textContent.includes("Email already exists")) {
            ErrorMessage.remove();
        }
    });
    [i_password, i_c_password].forEach(field => {
        field.addEventListener('input', () => {
            if (error_msg.textContent.includes("Passwords do not match")) {
                ErrorMessage.remove();
            }
        });
    });
});
