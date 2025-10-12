document.addEventListener('DOMContentLoaded', () => {
    const btnVerify = document.getElementById('btn_verify');
    const nameElement = document.getElementById('name');
    const emailElement = document.getElementById('email');
    const statusElement = document.getElementById('status');
    const statusContainer = document.getElementById('verification_status');
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token");
    let currentEmail = null;

    window.ApiCaller.postRequest('/rr/api/verify-status', { token: token }).then(response => {
        // Always update the display info if data exists
        const data = response.data || {};
        
        nameElement.textContent = data.name || 'N/A';
        emailElement.textContent = data.email || 'N/A';
        statusElement.textContent = `STATUS: ${String(data.state || 'UNKNOWN').toUpperCase()}`;
        currentEmail = data.email;

        // Reset status container classes
        statusContainer.className = 'status-badge';

        // Handle different states
        switch (data.state) {
            case 'Pending':
                statusContainer.classList.add('status-pending');
                btnVerify.disabled = false;
                console.log('State: Pending - Button enabled');
                break;

            case 'Expired':
                statusContainer.classList.add('status-expired');
                btnVerify.disabled = true;
                btnVerify.textContent = 'Token Expired';
                console.log('State: Expired - Button disabled');
                break;

            case 'Verified':
                statusContainer.classList.add('status-verified');
                btnVerify.disabled = true;
                btnVerify.textContent = 'Already Verified';
                console.log('State: Verified - Button disabled');
                break;

            default:
                statusContainer.classList.add('status-expired');
                btnVerify.disabled = true;
                btnVerify.textContent = 'Invalid Token';
                console.log('State: Unknown - Button disabled');
                break;
        }
    }).catch(error => {
        console.error("Network or server error:", error);
        window.MessageBox.showError("Unable to reach the server. Please try again later.", () => {
            window.MessageBox.hide();
        });
    });

    btnVerify.addEventListener('click', () => {
        if (!currentEmail) {
            window.MessageBox.showError("No email found to verify.", () => {
                window.MessageBox.hide();
            });
            return;
        }

        window.MessageBox.showConfirm('Are you sure you want to verify account registration?', () => {
            window.ApiCaller.postRequest('/rr/api/verify-account', { 
                email: currentEmail
            }).then(response => {
                if (response.success) {
                    window.MessageBox.showSuccess('Email has been verified. You can now login.', () => {
                        window.location.href = '/rr/sign-in';
                        window.MessageBox.hide();
                    });
                } else {
                    window.MessageBox.showError(response.message, () => {
                        window.MessageBox.hide();
                    });
                }
            }).catch(error => {
                console.error("Network or server error:", error);
                window.MessageBox.showError("Unable to reach the server. Please try again later.", () => {
                    window.MessageBox.hide();
                });
            });
        });
    });
});