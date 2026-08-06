document.addEventListener("DOMContentLoaded", () => {
    checkAdminMode();

    const page = document.body.dataset.page;

    switch (page) {
        case "wishlist":
            renderCards("wishlist");
            break;

        case "collection":
            renderCards("owned");
            break;

        case "trade":
            renderTradeCards();
            break;
    }
});