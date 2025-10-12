document.addEventListener('DOMContentLoaded', () => {
    const i_email = document.getElementById('email');
    const boxes = document.querySelectorAll('.code-box');
    const submit = document.getElementById('btn_submit');
    const container = document.getElementById('verification');
    const resend = document.getElementById('resend_code');
    const resend_link = document.getElementById('resend_link');
    boxes.forEach((box, index) => {
        box.addEventListener('input', (e) => {
            if (box.value.length === 1 && index < boxes.length - 1) {
                boxes[index + 1].focus();
                window.ErrorMessage.remove();
            }
        });
        box.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && index > 0 && !box.value) {
                boxes[index - 1].focus();
            }
        });
        box.addEventListener('paste', (e) => {
            e.preventDefault();
            const paste = (e.clipboardData || window.clipboardData).getData('text').trim();

            if (!paste) return;
            const digits = paste.replace(/\D/g, '').split('');

            if (digits.length === 0) return;
            boxes.forEach((b, i) => {
                b.value = digits[i] || '';
            });
            const nextIndex = Math.min(digits.length, boxes.length - 1);
            boxes[nextIndex].focus();
        });

    });

    submit.addEventListener('click', async () => {
        submit.disabled = true;
        window.ErrorMessage.remove();
        const email = i_email.value.trim();
        const code = Array.from(boxes).map(b => b.value).join('');

        if (!email) return showError('Email required');
        if (!code && container.style.display !== 'none') return showError('Enter verification code');

        const valid_email = AuthFieldValidator.isValidEmail(email)
        if (!valid_email.success) {
            showError(valid_email.message);
            return;
        }

        if (container.style.display === 'none') {
            const response = await window.ApiCaller.postRequest('/rr/api/send-code-to-mail', { email });
            if (response.success) {
                window.MessageBox.showSuccess(response.message, () => {
                    container.style.display = 'block';
                    i_email.disabled = true;
                    window.MessageBox.hide();
                    startResendCooldown(30);
                    resend.style.display = 'block';
                    submit.disabled = false;
                });
            } else {
                showError(response.message);
            }
        } else {
            const response = await window.ApiCaller.postRequest('/rr/api/verify-code', { email, code });
            if (response.success) {
                const token = response.data;
                if (!token) return window.MessageBox.showError('No reset token returned', () => {
                    window.MessageBox.hide();
                });
                window.MessageBox.showSuccess(response.message, () => {
                    window.location.href = `/rr/reset-password?token=${encodeURIComponent(token)}`;
                });
            } else {
                showError(response.message);
            }
        }
    });
    resend_link.addEventListener('click', async () => {
        window.ErrorMessage.remove();
        const email = i_email.value.trim();
        if (!email) return window.ErrorMessage.show('Email is required.');

        const response = await window.ApiCaller.postRequest('/rr/api/send-code-to-mail', { email });
        if (response.success) {
            window.MessageBox.showSuccess('A new verification code has been sent.', () => {
                window.MessageBox.hide();
                startResendCooldown(30);
            });
        } else {
            showError(response.message);
        }
    });
    function startResendCooldown(seconds = 30) {
        let remaining = seconds;
        resend_link.classList.add('disabled');
        resend_link.textContent = `Resend code (${remaining}s)`;

        const timer = setInterval(() => {
            remaining--;
            if (remaining <= 0) {
                clearInterval(timer);
                resend_link.classList.remove('disabled');
                resend_link.textContent = 'Resend code';
            } else {
                resend_link.textContent = `Resend code (${remaining}s)`;
            }
        }, 1000);
    }
    function showError(msg) {
        window.ErrorMessage.show(msg);
        submit.disabled = false;
    }
});
