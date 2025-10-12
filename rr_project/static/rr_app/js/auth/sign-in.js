document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        submit: document.getElementById('btn_submit'),
        i_email: document.getElementById('email'),
        i_password: document.getElementById('password'),
        inputs: []
    }
    elements.inputs = [elements.i_email, elements.i_password];
    const setupEventListeners = () => {
        FieldInputKeyListener.addKeyListener(elements.inputs, elements.submit);
        FieldInputKeyListener.removeErrorMsgOnInput(elements.inputs);
        elements.submit.addEventListener('click', async () => {
            const { email, password } = getValues();
            elements.submit.disabled = true;
            if (!AuthFieldValidator.requireAllFields(elements.inputs)) return showError("Missing required fields.");
            const is_valid_email = AuthFieldValidator.isValidEmail(email);
            if (!is_valid_email.success) return showError(is_valid_email.message);
            await handleSignIn({email, password});
        });
    }

    const getValues = () => {
        return { email: elements.i_email.value.trim(), password: elements.i_password.value.trim() };
    }

    const handleSignIn = async (em_pass) => {
        const response = await window.ApiCaller.postRequest('/rr/api/sign-in', em_pass);
        console.log(response);
        if (response.success) {
            window.ApiCaller.auth.setSession(response.data.session, response.data.user);
            window.MessageBox.showSuccess(response.message, () => {
                window.location.href = "/rr/dashboard";
                window.MessageBox.hide();
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
