document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            const token = data.token;

            localStorage.setItem("jwt", token);
            window.location.href = "/edit_document";
        } else {
            document.getElementById("error-message").textContent = "Invalid credentials.";
        }
    } catch (error) {
        console.error("Login error:", error);
        document.getElementById("error-message").textContent = "An error occurred during login.";
    }
});
