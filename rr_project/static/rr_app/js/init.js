document.addEventListener('DOMContentLoaded', () => {
    window.DataManager = new DataManager();
    window.error_msg = document.getElementById('errorMsg');
    window.ErrorMessage = new ErrorMessage(window.error_msg);
    window.MessageBox = new MessageBox();
});

class ErrorMessage {
    constructor(error_element) {
        this.error_element = error_element;
    }
    show(msg) {
        this.error_element.style.display = 'block';
        this.error_element.textContent = msg;
    }
    remove() {
        this.error_element.style.display = 'none';
    }
}

class MessageBox {
    constructor() {
        this.overlay = document.querySelector('.messagebox-overlay');
        this.container = document.querySelector('.messagebox');
        this.title = document.getElementById('msgbx_title');
        this.body = document.getElementById('msgbx_body');
        this.btn = document.getElementById('msgbx_btn');
        this.btn_primary = document.getElementById('msgbx_btn_primary');
        this.initEnter();
    }

    initEnter(){
        document.addEventListener('keydown', (e)=>{
            if(e.key == 'Enter'){
                this.hide();
            }
        });
    }

    setTitle(title) {
        this.title.textContent = title;
    }

    setBody(body) {
        this.body.textContent = body;
    }

    setBtn(text) {
        this.btn.textContent = text;
    }

    setBtnPrimary(text) {
        this.btn_primary.textContent = text;
    }

    show() {
        this.overlay.classList.add('show');
    }

    hide() {
        this.overlay.classList.remove('show');
    }

    setTheme(theme) {
        this.container.classList.remove('theme-error', 'theme-warning', 'theme-success', 'theme-info');

        if (theme) {
            this.container.classList.add(`theme-${theme}`);
        }
    }

    showError(message) {
        this.setTheme('error');
        this.setTitle('Error');
        this.setBody(message);
        this.setBtnPrimary('Close');
        this.btn.style.display = 'none';
        this.show();
    }

    showWarning(message) {
        this.setTheme('warning');
        this.setTitle('Warning');
        this.setBody(message);
        this.setBtnPrimary('OK');
        this.btn.style.display = 'none';
        this.show();
    }

    showSuccess(message, callback) {
        this.setTheme('success');
        this.setTitle('Success');
        this.setBody(message);
        this.setBtnPrimary('OK');
        this.btn.style.display = 'none';
        this.show();
        this.btn_primary.onclick = callback;
    }

    showInfo(message) {
        this.setTheme('info');
        this.setTitle('Info');
        this.setBody(message);
        this.setBtnPrimary('OK');
        this.btn.style.display = 'none';
        this.show();
    }

    showConfirm(message, cancelText = 'Cancel', confirmText = 'Confirm') {
        this.setTheme(null);
        this.setTitle(null);
        this.setBody(message);
        this.setBtn(cancelText);
        this.setBtnPrimary(confirmText);
        this.btn.style.display = 'inline-block';
        this.show();
    }
}