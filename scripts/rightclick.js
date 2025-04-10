function setupContextMenu() {
    const rows = document.querySelectorAll(".tr.clickable");
    const contextMenu = document.getElementById("contextMenu");

    rows.forEach(row => {
        row.addEventListener("contextmenu", e => {
            e.preventDefault();
            contextMenu.style.top = `${e.pageY}px`;
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.style.display = "block";
        });
    });

    document.addEventListener("click", () => {
        contextMenu.style.display = "none";
    });

    // Add listeners to context menu items if needed
    document.getElementById("download").addEventListener("click", () => {
        console.log("Download clicked");
        // implement your download logic here
    });

    document.getElementById("rename").addEventListener("click", () => {
        console.log("Rename clicked");
        // implement rename logic
    });

    document.getElementById("delete").addEventListener("click", () => {
        console.log("Delete clicked");
        // implement delete logic
    });
}

// Initial load
document.addEventListener("DOMContentLoaded", () => {
    setupContextMenu();
});

// When HTMX updates #table-container
document.body.addEventListener("htmx:afterSwap", (e) => {
    if (e.target.id === "table-container") {
        setupContextMenu();
    }
});
