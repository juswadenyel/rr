document.addEventListener('DOMContentLoaded', () => {
    const i_email = document.getElementById('email');
    const submit = document.getElementById('btnSubmit');

    submit.addEventListener('click', async () => {
            const email = i_email.value.trim();

            try {
                const response = await window.DataManager.postRequest('/rr/fpass_request/', { email });

                if (response.success) {
                    submit.disabled = true;
                    window.MessageBox.showSuccess(response.message, ()=>{
                        window.location.href = "/rr/login/";
                    });
                } else {
                    window.ErrorMessage.show(response.error || 'Failed to send reset email');
                    submit.disabled = false;
                }
            } catch (error) {
                window.ErrorMessage.show('Network error occurred');
                console.error('Password reset error:', error);
            }
    });
    i_email.addEventListener('input', ()=>{
        window.ErrorMessage.remove();
    });
    i_email.addEventListener('keydown', (e)=>{
        if(e.key == 'Enter'){
            submit.click();
        }
    })
});
