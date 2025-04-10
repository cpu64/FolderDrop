let selectedItemPath = null;

function setupContextMenu() {
    const rows = document.querySelectorAll(".tr.clickable");
    const contextMenu = document.getElementById("contextMenu");

    rows.forEach(row => {
        row.addEventListener("contextmenu", e => {
            e.preventDefault();
            selectedItemPath = row.getAttribute("data-path");

            contextMenu.style.top = `${e.pageY}px`;
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.style.display = "block";
        });
    });

    document.addEventListener("click", () => {
        contextMenu.style.display = "none";
    });

    document.getElementById("delete").addEventListener("click", async () => {
        console.log(`Are you sure you want to delete "${selectedItemPath}"?`);
        if (!selectedItemPath) return;

        const confirmed = confirm(`Are you sure you want to delete "${selectedItemPath}"?`);
        if (!confirmed) return;

        try {
            if (selectedItemPath.startsWith("/")) {
                selectedItemPath = selectedItemPath.slice(1);
            }
            
            const response = await fetch(`/delete/${selectedItemPath}`, {method: "DELETE"});

            if (response.ok) {
                const row = document.querySelector(`.tr.clickable[data-path="${CSS.escape(selectedItemPath)}"]`);
                row?.remove();
                console.log(`"${selectedItemPath}" deleted successfully.`);
            } else {
                console.error("Failed to delete");
            }
        } catch (error) {
            console.error("Error:", error);
        }

        contextMenu.style.display = "none";
        selectedItemPath = null;
    });
}

document.body.addEventListener("htmx:afterSwap", (e) => {
    if (e.target.id === "table-container") {
        setupContextMenu();
    }
});
