function addTireForm(targetContainerId, group1Class, group2Class) {
    // コピー先のコンテナを取得
    const container = document.querySelector(`#${targetContainerId}`);
    if (!container) {
        console.error(`Container with ID '${targetContainerId}' not found.`);
        return;
    }

    // 新しいフォーム全体を包むコンテナを作成
    const formContainer = document.createElement("div");
    formContainer.className = "copied-tire-form";
    
    // グループ1を生成
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

    // グループ2を生成
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

    // グループ1とグループ2を新しいフォームコンテナに追加
    formContainer.appendChild(group1);
    formContainer.appendChild(group2);


    // 親要素に新しいフォームを追加
    container.appendChild(formContainer);
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

// 親要素にイベントリスナーを設定
function setupEventDelegation(targetContainerId, group1Class, group2Class) {
    const container = document.getElementById(targetContainerId);
    if (!container) {
        console.error(`Container with ID '${targetContainerId}' not found.`);
        return;
    }

    container.addEventListener("click", (event) => {
        // クリックされた要素がコピー用ボタンか確認
        if (event.target && event.target.classList.contains("copy-btn-group-2")) {
            addTireForm(targetContainerId, group1Class, group2Class);
        }
    });
}

// 実行: ページ読み込み時にイベントリスナーを登録
document.addEventListener("DOMContentLoaded", () => {
    // 元のコピーボタン用イベントリスナー
    setupAddTireFormListener("copy-button", "copied-list", "group-1 group-1-style", "group-2 group-2-style");
    
    // 新しいフォーム用のイベント委任を追加
    setupEventDelegation("copied-list", "group-1 group-1-style", "group-2 group-2-style");
});
