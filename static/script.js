// ==============================
// ユーティリティ関数
// ==============================

// 選択肢を動的に生成する関数
function generateOptions(values, formatFn) {
    return values.map(value => `<option value="${value}">${formatFn(value)}</option>`).join('');
}

// 選択肢を動的にロードする関数
async function loadOptions(selectElement, apiUrl) {
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error(`Failed to fetch options from ${apiUrl}`);
        const { data } = await response.json();
        
        // 選択肢をリセット
        selectElement.innerHTML = ''; // 初期化

        // デフォルトオプションを追加
        const defaultOption = document.createElement('option');
        defaultOption.value = 0;
        defaultOption.textContent = "メーカー";
        defaultOption.disabled = true; // 選択不可に設定
        defaultOption.selected = true; // 初期選択状態に設定
        selectElement.appendChild(defaultOption);

        // APIから取得した選択肢を追加
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.name || item.value;
            selectElement.appendChild(option);
        });

        console.log(`Options loaded for ${selectElement.id}:`, selectElement.innerHTML);
    } catch (error) {
        console.error(`Error loading options for ${selectElement.name || selectElement.id}:`, error);
    }
}

// ==============================
// フォーム操作
// ==============================

let formCount = 0; // フォーム数カウンター

// フォームを追加する関数
function addTireForm(targetContainerId) {
    console.log(`addTireForm called with targetContainerId: ${targetContainerId}`); // ログ追加
    const container = document.querySelector(`#${targetContainerId}`);
    if (!container) {
        console.error(`Container with ID '${targetContainerId}' not found.`);
        return;
    }
    console.log("Container found:", container); // ログ追加
    formCount++; // フォームカウントをインクリメント
    console.log("Form count incremented. Current formCount:", formCount); // ログ追加

    // 個別データフォームを生成
    const formHTML = `
        <div class="copied-tire-form">
            <!-- グループ1: manufacturer, manufacturing_year -->
            <div class="form-group group-1 group-1-style">
                <div class="input-wrap manufacturer-wrap">
                    <select name="manufacturer[]" id="manufacturer-${formCount}" class="form-control">
                        <option value="0" disabled selected>メーカー</option>
                        {% for value, label in form.manufacturer.choices %}
                            <option value="{{ value }}">{{ label }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="input-wrap manufacturing-year-wrap">
                <select name="manufacturing_year[]" id="manufacturing_year-${formCount}" class="form-control">
                    <option value="0" disabled selected>製造年</option>
                    ${generateOptions([2022, 2023, 2024, 2025], year => `${year}年`)}
                </select>
            </div>
        </div>

        <!-- グループ2: tread_depth, uneven_wear, other_details -->
        <div class="form-group group-2 group-2-style">
            <div class="input-wrap small-input" id="tread-depth">
                <select name="tread_depth[]" id="tread_depth-${formCount}" class="form-control">
                <option value="0" disabled selected>残り溝</option>
                    ${generateOptions([10, 9, 8, 7, 6, 5, 4, 3], depth => `${depth} 分山`)} <!-- 降順 -->
                </select>
            </div>
            <div class="input-wrap small-input" id="uneven-wear">
                <select name="uneven_wear[]" id="uneven_wear-${formCount}" class="form-control">
                <option value="0" disabled selected>片減り</option>
                    ${generateOptions([0, 1, 2, 3], wear => `${wear}段階`)}
                </select>
            </div>
            <div class="input-wrap large-input" id="other-details">
                <input type="text" name="other_details[]" id="other_details-${formCount}" class="form-control" placeholder="その他">
            </div>
            <button type="button" class="btn copy-btn-group-2">コピー</button>
        </div>
    </div>
    `;

    // フォームを挿入
    container.insertAdjacentHTML("beforeend", formHTML);
    console.log("HTML after inserting form:", container.innerHTML);

    // 新しいフォームのオプションをロード
    const manufacturerSelect = document.querySelector(`#manufacturer-${formCount}`);
    if (manufacturerSelect) {
        console.log(`Manufacturer select element for formCount=${formCount}:`, manufacturerSelect);
        loadOptions(manufacturerSelect, '/api/manufacturers');
    } else {
        console.error(`Manufacturer select element for formCount=${formCount} not found.`);
    }
}

// ==============================
// 初期化処理
// ==============================

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOMContentLoaded event fired.");
    
    const copiedListContainer = document.getElementById('copied-list');
    console.log("Copied list container:", copiedListContainer);

    // 初期化：コピー元ボタンのリスナー
    document.getElementById('copy-button').addEventListener('click', () => {
        addTireForm('copied-list');
    });

    // 動的ボタン用のイベント委譲
    copiedListContainer.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('copy-btn-group-2')) {
            addTireForm('copied-list');
        }
    });
}); // ここで閉じる

