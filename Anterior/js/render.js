function createLpsCard(item) {
    const card = document.createElement("div");
    card.classList.add("lps-card");
    card.dataset.id = item.id;

    card.innerHTML = `
        <div class="priority-badge ${item.priority ? "" : "hidden"}">⭐ PRIORITY</div>
        <div class="favorite-badge ${item.favorite ? "" : "hidden"}">❤️</div>

        <img src="${item.image}" alt="${item.name}">

        <h3 class="lps-name">${item.name}</h3>

        <p class="lps-meta">
            ${item.generation} · ${item.category} · ${item.year}
        </p>

        <span class="status-badge">${item.status}</span>

        <div class="admin-buttons">
            <button class="btn-collection">✔ Add to Collection</button>
            <button class="btn-priority">⭐ Priority</button>
            <button class="btn-favorite">❤️ Favorite</button>
            <button class="btn-trade">🔄 Trade</button>
        </div>
    `;

    return card;
}

function renderCards(filterStatus) {
    const container = document.getElementById("cards-container");

    if (!container) return;

    container.innerHTML = "";

    const savedData = getSavedLpsData();

    const filteredItems = savedData.filter(item => item.status === filterStatus);

    filteredItems.forEach(item => {
        const card = createLpsCard(item);
        container.appendChild(card);
    });

    activateAdminButtons();
}

function renderTradeCards() {
    const container = document.getElementById("cards-container");

    if (!container) return;

    container.innerHTML = "";

    const savedData = getSavedLpsData();

    const tradeItems = savedData.filter(item => item.trade === true);

    const counter = document.getElementById("trade-count");

    if (counter) {
        counter.textContent = `${tradeItems.length} items`;
    }

    tradeItems.forEach(item => {
        const card = createLpsCard(item);
        container.appendChild(card);
    });

    activateAdminButtons();
}

