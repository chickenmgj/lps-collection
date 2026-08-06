function getSavedLpsData() {
    const saved = localStorage.getItem("lpsData");

    if (saved) {
        return JSON.parse(saved);
    }

    localStorage.setItem("lpsData", JSON.stringify(lpsData));
    return lpsData;
}

function saveLpsData(data) {
    localStorage.setItem("lpsData", JSON.stringify(data));
}

function updateLpsItem(id, changes) {
    const data = getSavedLpsData();

    const updatedData = data.map(item => {
        if (item.id === id) {
            return {
                ...item,
                ...changes
            };
        }

        return item;
    });

    saveLpsData(updatedData);
}