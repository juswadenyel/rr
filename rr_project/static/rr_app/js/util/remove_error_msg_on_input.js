
function removeErrorMsgOnInput(inputs) {
    inputs.forEach((field) => {
        field.addEventListener('input', ()=>{
            document.querySelector('.form-errors').classList.remove('show');
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    // Target all form input types, including selects
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], select');
    
    // Only call the function if there are inputs to avoid errors
    if (inputs.length > 0) {
        removeErrorMsgOnInput(inputs);
    }
});
