class FieldInputKeyListener{
    static addKeyListener(inputs, submit){
        inputs.forEach((field, index) => {
            field.addEventListener('keydown', (e) => {
                const isEnter = e.key === 'Enter';
                const isArrowDown = e.key === 'ArrowDown';

                if (isEnter || isArrowDown) {
                    e.preventDefault();
                    const next = inputs[index + 1];
                
                    if (next) {
                        next.focus();
                    } else if (isEnter) {
                        submit.click();
                    }
                }

                if(e.key === 'ArrowUp'){
                    e.preventDefault();
                    const prev = inputs[index - 1];
                    if(prev){
                        prev.focus();
                    }
                }
            });
        });
    }
    static removeErrorMsgOnInput(inputs){
        inputs.forEach((field) => {
            field.addEventListener('input', ()=>{
                window.ErrorMessage.remove();
            });
        });
    }
}
