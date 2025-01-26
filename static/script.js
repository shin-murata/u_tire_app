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
// 通常時のフォーム生成ロジック
// ==============================

let formCount = 0; // フォーム数カウンター

// フォームを追加する関数
function addTireForm(targetContainerId) {
    console.log(`addTireForm called with targetContainerId: ${targetContainerId}`); // ログ追加
    console.log(`Stack trace:`, new Error().stack); // 呼び出し元を追跡
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
                <option value="" disabled selected>片減り</option>
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
    // デバッグ: 生成されたHTMLを確認
    console.log(`Generated HTML for tread_depth: ${document.getElementById(`tread_depth-${formCount}`).outerHTML}`);
    console.log(`Generated HTML for uneven_wear: ${document.getElementById(`uneven_wear-${formCount}`).outerHTML}`);

    // 遅延参照でエラーを防止
    setTimeout(() => {
        // 新しく生成されたセレクトボックスを取得してデバッグ
        const newUnevenWearSelect = document.getElementById(`uneven_wear-${formCount}`);
        console.log(`Generated select element: ${newUnevenWearSelect.outerHTML}`);

        // 新しいフォームのオプションをロード
        const manufacturerSelect = document.querySelector(`#manufacturer-${formCount}`);
        if (manufacturerSelect) {
            console.log(`Manufacturer select element for formCount=${formCount}:`, manufacturerSelect);
            loadOptions(manufacturerSelect, '/api/manufacturers');
        } else {
            console.error(`Manufacturer select element for formCount=${formCount} not found.`);
        }
    }, 0); // 非同期で直後に実行
}

// ==============================
// エラー時のフォーム再生成ロジック
// ==============================
// 未入力データに基づいてフォームを生成する関数
function regenerateTireForm(containerId, invalidEntries) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container with ID "${containerId}" not found.`);
        return;
    }

    if (!Array.isArray(invalidEntries) || invalidEntries.length === 0) {
        console.warn("Invalid entries are empty. Skipping regeneration.");
        return;
    }

    invalidEntries.forEach((entry) => {
        formCount++; // フォームカウンターをインクリメント

        // フォームHTMLを生成
        const formHTML = `
            <div class="copied-tire-form">
                <!-- グループ1: manufacturer, manufacturing_year -->
                <div class="form-group group-1 group-1-style">
                    <div class="input-wrap manufacturer-wrap">
                        <select name="manufacturer[]" id="manufacturer-${formCount}" class="form-control">
                            <option value="0" disabled ${!entry.manufacturer ? "selected" : ""}>メーカー</option>
                            {% for value, label in form.manufacturer.choices %}
                                <option value="{{ value }}" ${entry.manufacturer == "{{ value }}" ? "selected" : ""}>{{ label }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="input-wrap manufacturing-year-wrap">
                        <select name="manufacturing_year[]" id="manufacturing_year-${formCount}" class="form-control">
                            <option value="0" disabled ${!entry.manufacturing_year ? "selected" : ""}>製造年</option>
                            ${generateOptions(
                                [2022, 2023, 2024, 2025],
                                year => `<option value="${year}" ${entry.manufacturing_year == year ? "selected" : ""}>${year}年</option>`
                            )}
                        </select>
                    </div>
                </div>

                <!-- グループ2: tread_depth, uneven_wear, other_details -->
                <div class="form-group group-2 group-2-style">
                    <div class="input-wrap small-input" id="tread-depth">
                        <select name="tread_depth[]" id="tread_depth-${formCount}" class="form-control">
                            <option value="0" disabled ${!entry.tread_depth ? "selected" : ""}>残り溝</option>
                            ${generateOptions(
                                [10, 9, 8, 7, 6, 5, 4, 3],
                                depth => `<option value="${depth}" ${entry.tread_depth == depth ? "selected" : ""}>${depth} 分山</option>`
                            )}
                        </select>
                    </div>
                    <div class="input-wrap small-input" id="uneven-wear">
                        <select name="uneven_wear[]" id="uneven_wear-${formCount}" class="form-control">
                            <option value="" disabled ${entry.uneven_wear == null ? "selected" : ""}>片減り</option>
                            ${generateOptions(
                                [0, 1, 2, 3],
                                wear => `<option value="${wear}" ${entry.uneven_wear == wear ? "selected" : ""}>${wear}段階</option>`
                            )}
                        </select>
                    </div>
                    <div class="input-wrap large-input" id="other-details">
                        <input type="text" name="other_details[]" id="other_details-${formCount}" class="form-control"
                               value="${entry.other_details || ""}" placeholder="その他">
                    </div>
                    <button type="button" class="btn copy-btn-group-2">コピー</button>
                </div>
            </div>
        `;

        // コンテナに挿入
        container.insertAdjacentHTML("beforeend", formHTML);
    });
}
// ==============================
// 通常時の初期化
// ==============================

function initializeDefaultForms() {
    console.log("Initializing default forms...");
    // 初期の固定フォームや動的フォームをセットアップ
    const defaultContainer = document.getElementById('copied-list');
    if (!defaultContainer) {
        console.error("Default container not found!");
        return;
    }

   // DOM内に既存のフォームがあるか確認
   const existingForms = defaultContainer.querySelectorAll('.copied-tire-form');
   if (existingForms.length > 0) {
       console.log(`Found ${existingForms.length} existing form(s) in the template. Skipping default form generation.`);
       return; // 既存フォームがある場合、追加しない
   }

   // 初期フォームを1つ生成 (テンプレートにフォームがない場合のみ)
   addTireForm('copied-list');
   console.log("Default form initialized.");
   console.log('initializeDefaultForms invoked');
}

// ==============================
// エラー時の初期化
// ==============================

function initializeErrorForms(invalidEntries) {
    console.log("Initializing error forms...");

    const container = document.getElementById('copied-list');
    if (!container) {
        console.error("Error container not found!");
        return;
    }

    // invalidEntries が空の場合は処理を終了
    if (!Array.isArray(invalidEntries) || invalidEntries.length === 0) {
        console.warn("Invalid entries are empty. Skipping error form initialization.");
        return;
    }

    // エラー時に未入力データを基にフォームを再生成
    regenerateTireForm('copied-list', invalidEntries);
    console.log("Error forms initialized with invalid entries.");
}

// ==============================
// ページロード時の初期化処理
// ==============================

document.addEventListener('DOMContentLoaded', () => {
    console.log("Resetting formCount to 0.");
    formCount = 0; // ページロード時にリセット
    console.log("DOMContentLoaded event fired.");
    console.log("Page fully loaded. Checking initial select elements...");
    console.log("DOMContentLoaded event fired. Initializing forms...");

    // 初期化対象のコンテナを確認
    const copiedListContainer = document.getElementById('copied-list');
    console.log("Copied list container:", copiedListContainer);
    if (!copiedListContainer) {
        console.error("Copied list container not found!");
        return;
    }

    // 初期フォームのセレクトボックスを取得してログに出力
    const initialTreadDepth = document.getElementById('tread_depth-0');
    const initialUnevenWear = document.getElementById('uneven_wear-0');

    if (initialTreadDepth) {
        console.log(`Initial HTML for tread_depth: ${initialTreadDepth.outerHTML}`);
    } else {
        console.error("tread_depth select element not found!");
    }

    if (initialUnevenWear) {
        console.log(`Initial HTML for uneven_wear: ${initialUnevenWear.outerHTML}`);
    } else {
        console.error("uneven_wear select element not found!");
    }
    
    // ページロード時に invalidEntries の有無を確認
    if (typeof invalidEntries !== 'undefined' && Array.isArray(invalidEntries) && invalidEntries.length > 0) {
        console.log("Invalid entries detected. Initializing error forms...");
        console.log("Invalid entries data:", invalidEntries);
        initializeErrorForms(invalidEntries); // エラー時の初期化
    } else {
        console.log("No invalid entries detected. Initializing default forms...");
        initializeDefaultForms(); // 通常の初期化
    }

    // コピー機能のイベントリスナーをセットアップ
    const copyButton = document.getElementById('copy-button');
    if (copyButton) {
        copyButton.addEventListener('click', () => {
            addTireForm('copied-list');
        });
    }

    // 動的ボタン用のイベント委譲
    copiedListContainer.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('copy-btn-group-2')) {
            addTireForm('copied-list');

            // 動的フォームのAPI呼び出しを確実に実行
            const manufacturerSelect = document.querySelector(`#manufacturer-${formCount}`);
            if (manufacturerSelect) {
                loadOptions(manufacturerSelect, '/api/manufacturers');
            }
        }
    });
}); // ここで閉じる

// デバッグコードをここに追加
console.log(`Generated select element: ${document.getElementById(`uneven_wear-${formCount}`).outerHTML}`);
