document.addEventListener("DOMContentLoaded", () => {
    const editor = document.getElementById("editor");
    const token = localStorage.getItem("jwt");

    if (!token) {
        window.location.href = "/login";
        return;
    }

    const wsProtocol = (window.location.protocol === "https:") ? "wss:" : "ws:";
    const ws = new WebSocket(`${wsProtocol}//${window.location.host}/edit_document?token=${token}`);

    ws.onopen = () => {
        console.log("WebSocket connected!");
    };

    ws.onmessage = (event) => {
        if (event.data.startsWith("REDIRECT:")) {
            window.location.href = event.data.split(":")[1];
            return;
        }
        editor.value = event.data;
    };

    ws.onclose = () => {
        console.log("WebSocket closed.");
        window.location.href = "/login";
    };

    editor.addEventListener("input", (event) => {
        const fullText = editor.value;

        let typedChar = "";

        try {
            typedChar = event.data;
            if (!typedChar) {
                if (event.inputType === "deleteContentBackward") {
                    typedChar = "BACKSPACE";
                } else if (event.inputType === "deleteContentForward") {
                    typedChar = "DELETE";
                } else if (event.inputType === "insertLineBreak") {
                    typedChar = "ENTER";
                } else {
                    typedChar = "UNIDENTIFIED";
                }
            }
        } catch (error) {
            console.error("Failed to identify typed char");
            typedChar = "UNIDENTIFIED"
        }

        const cursorPos = editor.selectionStart;
        const textUntilCursor = fullText.substring(0, cursorPos);
        const rows = textUntilCursor.split("\n");
        const row = rows.length;
        const col = rows[row - 1].length + 1;

        const payload = {
            text: fullText,
            char: typedChar,
            row,
            col
        };

        try {
            ws.send(JSON.stringify(payload));
        } catch (error) {
            console.error("Failed to send data:", error);
        }
    });
});
