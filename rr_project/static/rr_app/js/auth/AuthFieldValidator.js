class AuthFieldValidator {
    static isValidEmail(email) {
        const eduRe = /^[a-zA-Z]+\.[a-zA-Z]+@cit\.edu$/;
        const generalRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!generalRe.test(email)) {
            return {
                success: false,
                message: "Invalid email format."
            };
        }

        // if (!eduRe.test(email)) {
        //     return {
        //         success: false,
        //         message: "Please use your educational email."
        //     };
        // }

        return {
            success: true,
            message: "Email is valid."
        };
    }

    static requireAllFields(inputs){
        let isValid = true;
        inputs.forEach((input) =>{
            if(!input){
                isValid = false;
            }
        });
        return isValid;
    }

    static isValidSchoolId(id) {
        const regex = /^\d{2}-\d{4}-\d{3}$/;
        return regex.test(id);
    }

    static isValidPassword(password) {
        if (password.length < 6) {
            return { success: false, message: "Password is too short. It must be at least 6 characters long." };
        }
        return { success: true, message: "Valid password" };
    }
}
