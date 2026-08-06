function activateAdminButtons() {
    const collectionButtons = document.querySelectorAll(".btn-collection");
    const priorityButtons = document.querySelectorAll(".btn-priority");
    const favoriteButtons = document.querySelectorAll(".btn-favorite");
    const tradeButtons = document.querySelectorAll(".btn-trade");

    collectionButtons.forEach(button => {
        button.addEventListener("click", () => {
            const card = button.closest(".lps-card");
            const id = card.dataset.id;

            updateLpsItem(id, { status: "owned" });
            renderCards("wishlist");
        });
    });

    priorityButtons.forEach(button => {
        button.addEventListener("click", () => {
            const card = button.closest(".lps-card");
            const id = card.dataset.id;

            const data = getSavedLpsData();
            const item = data.find(pet => pet.id === id);

            updateLpsItem(id, { priority: !item.priority });
            renderCards("wishlist");
        });
    });

    favoriteButtons.forEach(button => {
        button.addEventListener("click", () => {
            const card = button.closest(".lps-card");
            const id = card.dataset.id;

            const data = getSavedLpsData();
            const item = data.find(pet => pet.id === id);

            updateLpsItem(id, { favorite: !item.favorite });
            renderCards("wishlist");
        });
    });

    tradeButtons.forEach(button => {
        button.addEventListener("click", () => {
            const card = button.closest(".lps-card");
            const id = card.dataset.id;

            const data = getSavedLpsData();
            const item = data.find(pet => pet.id === id);

            updateLpsItem(id, { trade: !item.trade });
            renderCards("wishlist");
        });
    });
}

function enableAdminMode() {
    const password = prompt("Enter admin password:");

    if (password === "lpsadmin") {
        document.body.classList.add("admin-mode");
        localStorage.setItem("adminMode", "true");
        alert("Admin mode activated!");
    } else {
        alert("Wrong password.");
    }
}

function checkAdminMode() {
    const isAdmin = localStorage.getItem("adminMode");

    if (isAdmin === "true") {
        document.body.classList.add("admin-mode");
    }
}