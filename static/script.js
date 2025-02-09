async function sendMessage() {
    const userInput = document.getElementById("userInput");
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message to chat
    const messagesDiv = document.getElementById("messages");
    const userMessageDiv = document.createElement("div");
    userMessageDiv.className = "message user";
    userMessageDiv.textContent = message;
    messagesDiv.appendChild(userMessageDiv);

    // Clear input
    userInput.value = "";

    // Send message to backend
    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });
        const data = await response.json();

        if (response.ok) {
            const botMessageDiv = document.createElement("div");
            botMessageDiv.className = "message bot";
            botMessageDiv.textContent = data.response;
            messagesDiv.appendChild(botMessageDiv);
        } else {
            throw new Error(data.error || "Unknown error");
        }
    } catch (error) {
        alert("Error: " + error.message);
    }
}
