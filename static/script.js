async function loadOptions(selectElement, apiUrl) {
    const response = await fetch(apiUrl);
    const data = await response.json();
    selectElement.innerHTML = ''; // 初期化
    data.data.forEach(item => {
        const option = document.createElement('option');
        option.value = item.id;
        option.textContent = item.name || item.value;
        selectElement.appendChild(option);
    });
}

function initializeForm(selectors) {
    selectors.forEach(({ selector, api }) => {
        const element = document.querySelector(selector);
        if (element) {
            loadOptions(element, api);
        }
    });
}

function addTireForm(targetContainerId, group1Class, group2Class) {
    const container = document.querySelector(`#${targetContainerId}`);
    if (!container) {
        console.error(`Container with ID '${targetContainerId}' not found.`);
        return;
    }

    const formContainer = document.createElement("div");
    formContainer.className = "copied-tire-form";

    const group1 = document.createElement("div");
    group1.className = `form-group ${group1Class}`;
    group1.innerHTML = `
        <div class="input-wrap manufacturer-wrap">
            <label for="manufacturer">メーカー:</label>
            <select name="manufacturer[]" class="form-control"></select>
        </div>
        <div class="input-wrap manufacturing-year-wrap">
            <label for="manufacturing_year">製造年:</label>
            <input type="text" name="manufacturing_year[]" class="form-control">
        </div>
    `;

    const group2 = document.createElement("div");
    group2.className = `form-group ${group2Class}`;
    group2.innerHTML = `
        <div class="input-wrap small-input">
            <label for="tread_depth">残り溝:</label>
            <input type="number" name="tread_depth[]" class="form-control">
        </div>
        <div class="input-wrap small-input">
            <label for="uneven_wear">片減り:</label>
            <input type="text" name="uneven_wear[]" class="form-control">
        </div>
        <div class="input-wrap large-input">
            <label for="other_details">その他:</label>
            <input type="text" name="other_details[]" class="form-control">
        </div>
        <button type="button" class="btn copy-btn-group-2">コピー</button>
    `;

    formContainer.appendChild(group1);
    formContainer.appendChild(group2);
    container.appendChild(formContainer);

    // 新しい選択肢を動的にロード
    loadOptions(group1.querySelector('select[name="manufacturer[]"]'), '/api/manufacturers');
}

function setupAddTireFormListener(buttonId, targetContainerId, group1Class, group2Class) {
    const button = document.getElementById(buttonId);
    if (!button) {
        console.error(`Button with ID '${buttonId}' not found.`);
        return;
    }

    button.addEventListener("click", () => {
        addTireForm(targetContainerId, group1Class, group2Class);
    });
}

// イベント委譲を追加
function setupEventDelegation(targetContainerId, group1Class, group2Class) {
    const container = document.getElementById(targetContainerId);
    if (!container) {
        console.error(`Container with ID '${targetContainerId}' not found.`);
        return;
    }

    container.addEventListener("click", (event) => {
        if (event.target && event.target.classList.contains("copy-btn-group-2")) {
            console.log("Copy button clicked!"); // 動作確認用ログ
            addTireForm(targetContainerId, group1Class, group2Class);
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    // APIから選択肢をロード
    initializeForm([
        { selector: 'select[name="manufacturer[]"]', api: '/api/manufacturers' },
        { selector: 'select[name="ply_rating"]', api: '/api/ply_ratings' },
    ]);

    // 元のコピーボタン用イベントリスナー
    setupAddTireFormListener(
        "copy-button",
        "copied-list",
        "group-1 group-1-style",
        "group-2 group-2-style"
    );

    // 新しく追加されたフォーム用のイベント委譲を復元
    setupEventDelegation("copied-list", "group-1 group-1-style", "group-2 group-2-style");
});
