function addTireForm(targetContainerId, group1Class, group2Class) {
    // コピー先のコンテナを取得
    const container = document.querySelector(`#${targetContainerId}`);
    if (!container) {
        console.error(`Container with ID '${targetContainerId}' not found.`);
        return;
    }

    // 元のフォームグループを作成
    const group1 = document.createElement("div");
    group1.className = `form-group ${group1Class}`;
    group1.innerHTML = `
        <div class="input-wrap manufacturer-wrap">
            <label for="manufacturer">メーカー:</label>
            <input type="text" name="manufacturer[]" class="form-control">
        </div>
        <div class="input-wrap manufacturing-year-wrap">
            <label for="manufacturing_year">製造年:</label>
            <input type="text" name="manufacturing_year[]" class="form-control">
        </div>
    `;

    const group2 = document.createElement("div");
    group2.className = `form-group ${group2Class}`;
    group2.innerHTML = `
        <div class="input-wrap small-input" id="tread-depth">
            <label for="tread_depth">トレッド深さ:</label>
            <input type="number" name="tread_depth[]" class="form-control">
        </div>
        <div class="input-wrap small-input" id="uneven-wear">
            <label for="uneven_wear">摩耗状況:</label>
            <input type="text" name="uneven_wear[]" class="form-control">
        </div>
        <div class="input-wrap large-input" id="other-details">
            <label for="other_details">詳細:</label>
            <input type="text" name="other_details[]" class="form-control">
        </div>
    `;

    // 新しいフォームグループをコンテナに追加
    container.appendChild(group1);
    container.appendChild(group2);
}

// コピーボタン用のイベントリスナーを設定
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

// 実行: ページ読み込み時にイベントリスナーを登録
document.addEventListener("DOMContentLoaded", () => {
    setupAddTireFormListener("copy-button", "copied-list", "group-1 group-1-style", "group-2 group-2-style");
});
