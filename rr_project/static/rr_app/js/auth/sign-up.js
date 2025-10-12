document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        submit: document.getElementById('btn_submit'),
        i_f_name: document.getElementById('first_name'),
        i_l_name: document.getElementById('last_name'),
        i_email: document.getElementById('email'),
        i_password: document.getElementById('password'),
        i_c_password: document.getElementById('c_password'),
        inputs: []
    };

    elements.inputs = [
        elements.i_f_name,
        elements.i_l_name,
        elements.i_email,
        elements.i_password,
        elements.i_c_password
    ];

    const setupEventListeners = () => {
        FieldInputKeyListener.addKeyListener(elements.inputs, elements.submit);
        FieldInputKeyListener.removeErrorMsgOnInput(elements.inputs);

        elements.submit.addEventListener('click', async () => {
            elements.submit.disabled = true;

            const { f_name, l_name, email, password, c_password } = getValues();

            if (!AuthFieldValidator.requireAllFields(elements.inputs)) 
                return showError("Missing required fields.");

            const is_valid_email = AuthFieldValidator.isValidEmail(email);
            if (!is_valid_email.success)
                return showError(is_valid_email.message);

            if (password !== c_password)
                return showError("Passwords do not match.");

            const valid_password = AuthFieldValidator.isValidPassword(password);
            if (!valid_password.success)
                return showError(valid_password.message);

            await handleSignUp({ firstName: f_name, lastName: l_name, email, password, role: 'STUDENT' });
        });
    };

    const getValues = () => ({
        f_name: elements.i_f_name.value.trim(),
        l_name: elements.i_l_name.value.trim(),
        email: elements.i_email.value.trim(),
        password: elements.i_password.value.trim(),
        c_password: elements.i_c_password.value.trim()
    });

    const showError = (msg) => {
        window.ErrorMessage.show(msg);
        elements.submit.disabled = false;
    };

    const handleSignUp = async (userData) => {
        const response = await window.ApiCaller.postRequest('/rr/api/sign-up', userData);

        if (response.success) {
            window.MessageBox.showSuccess(response.message, () => {
                window.location.href = '/rr/sign-in';
                window.MessageBox.hide();
            });
        } else {
            showError(response.message);
        }
    };

    setupEventListeners();
});
