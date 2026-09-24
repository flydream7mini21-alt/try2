function generatePassword() {
    const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()";
    let pass = "";
    for (let i = 0; i < 12; i++) {
        pass += chars[Math.floor(Math.random() * chars.length)];
    }
    document.getElementById("passwordField").value = pass;
}

function togglePassword() {
    const field = document.getElementById("passwordField");
    field.type = field.type === "password" ? "text" : "password";
}