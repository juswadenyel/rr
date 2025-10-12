class ErrorMessage {
    constructor() {

        this.error_element = document.getElementById('error_msg');
    }
    show(msg) {
        this.error_element.style.display = 'block';
        this.error_element.textContent = msg;
    }
    remove() {
        this.error_element.style.display = 'none';
    }
}

window.ErrorMessage = new ErrorMessage();