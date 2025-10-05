document.addEventListener('DOMContentLoaded', () => {
    const submit = document.getElementById('btnSubmit');
    const i_password = document.getElementById('password');
    const i_c_password = document.getElementById('cPassword');
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    const access_token = params.get('access_token');

    submit.addEventListener('click', async () => {
        submit.disabled = true;
            const password = i_password.value.trim();
            const c_password = i_c_password.value.trim();
            try {
                const response = await window.DataManager.postRequest('/rr/reset-password-req/', { password, c_password, access_token });
                if (response.success) {
                    submit.disabled = true;
                    window.MessageBox.showSuccess(response.message, ()=> {
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

    const inputs = [i_password, i_c_password];
    inputs.forEach((field, index) => {
        field.addEventListener('keydown', (e)=>{
            if(e.key == 'Enter'){
                e.preventDefault();
                const next = inputs[index + 1];
                if(next){
                    next.focus();
                }else{
                    submit.click();
                }
            }
        });
        field.addEventListener('input', ()=>{
            window.ErrorMessage.remove();
        });
    })
});
