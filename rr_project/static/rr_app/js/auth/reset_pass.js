document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        i_password: document.getElementById('password'),
        i_c_password: document.getElementById('c_password'),
        submit: document.getElementById('btn_submit'),
        inputs: []
    };
    elements.inputs = [elements.i_password, elements.i_c_password];

    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    const setupEventListeners = () => {
        FieldInputKeyListener.addKeyListener(elements.inputs, elements.submit);
        FieldInputKeyListener.removeErrorMsgOnInput(elements.inputs);
        elements.submit.addEventListener('click', handleReset);
    };

    const handleReset = () => {
        elements.submit.disabled = true;

        const password = elements.i_password.value.trim();
        const c_password = elements.i_c_password.value.trim();

        if (password !== c_password)
            return showError("Passwords do not match.");

        const validPassword = AuthFieldValidator.isValidPassword(password);
        if (!validPassword.success)
            return showError(validPassword.message);

        resetPassword({ password, token });
    };

    const resetPassword = async (payload) => {
        const response = await window.ApiCaller.postRequest('/rr/api/reset-password', payload);

        if (response.success) {
            window.MessageBox.showSuccess(response.message, () => {
                window.location.href = '/rr/sign-in';
            });
        } else {
            showError(response.message);
        }
    };

    const showError = (msg) => {
        window.ErrorMessage.show(msg);
        elements.submit.disabled = false;
    };

    setupEventListeners();
});
