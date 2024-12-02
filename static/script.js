document.getElementById("copy-button").addEventListener("click", function () {
    const copiedList = document.getElementById("copied-list");
    const entry = document.createElement("div");
    entry.classList.add("copied-item");
    entry.innerHTML = `
        <p>Width: ${document.querySelector('[name="width"]').value}</p>
        <p>Aspect Ratio: ${document.querySelector('[name="aspect_ratio"]').value}</p>
        <p>Inch: ${document.querySelector('[name="inch"]').value}</p>
        <p>Ply Rating: ${document.querySelector('[name="ply_rating"]').value}</p>
    `;
    copiedList.appendChild(entry);
});
