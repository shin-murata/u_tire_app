function addTireForm(targetContainerId, group1Class, group2Class) {
    // コピー先のコンテナを取得
    const container = document.querySelector(`#${targetContainerId}`);
    if (!container) {
        console.error(`Container with ID '${targetContainerId}' not found.`);
        return;
    }

    // 新しいフォームをまとめて作成
    const newForm = document.createElement("div");
    newForm.className = "copied-tire-form"; // 新しいフォームを包むクラス
    newForm.innerHTML = `
        <!-- グループ1: manufacturer, manufacturing_year -->
        <div class="form-group ${group1Class}">
            <div class="input-wrap manufacturer-wrap">
                <label for="manufacturer">メーカー:</label>
                <input type="text" name="manufacturer[]" class="form-control">
            </div>
            <div class="input-wrap manufacturing-year-wrap">
                <label for="manufacturing_year">製造年:</label>
                <input type="text" name="manufacturing_year[]" class="form-control">
            </div>
        </div>
        <!-- グループ2: tread_depth, uneven_wear, other_details -->
        <div class="form-group ${group2Class}">
            <div class="input-wrap small-input">
                <label for="tread_depth">トレッド深さ:</label>
                <input type="number" name="tread_depth[]" class="form-control">
            </div>
            <div class="input-wrap small-input">
                <label for="uneven_wear">摩耗状況:</label>
                <input type="text" name="uneven_wear[]" class="form-control">
            </div>
            <div class="input-wrap large-input">
                <label for="other_details">詳細:</label>
                <input type="text" name="other_details[]" class="form-control">
            </div>
        </div>
        `;
    
        // 新しいフォームをコンテナ（グループ2の外側）に追加
        container.appendChild(newForm);
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