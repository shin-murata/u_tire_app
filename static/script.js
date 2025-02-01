// ==============================
// ユーティリティ関数
// ==============================

// 選択肢を動的に生成する関数
// values: 選択肢の値の配列, formatFn: 表示用に値をフォーマットする関数
function generateOptions(values, formatFn) {
    return values.map(value => `<option value="${value}">${formatFn(value)}</option>`).join('');
}

// 指定されたAPIから選択肢をロードする関数
// selectElement: 選択肢を挿入するセレクトボックス, apiUrl: データ取得先のURL
async function loadOptions(selectElement, apiUrl) {
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error(`Failed to fetch options from ${apiUrl}`);
        const { data } = await response.json();
        
        // 選択肢をリセット
        selectElement.innerHTML = ''; // 初期化

        // デフォルトの「選択してください」を追加
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

// 新しいタイヤフォームを動的に追加する関数
// targetContainerId: フォームを追加するコンテナID, defaultValues: 初期値のオブジェクト
function addTireForm(targetContainerId, defaultValues = {}) {
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

    // フォームをコンテナに追加
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

    // 既存のフォームをクリアして二重化を防ぐ
    container.innerHTML = '';

    // invalidEntries に基づいてフォームを再生成
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

        // フォーム再生成後に必要な初期化処理を実行
        setTimeout(() => {
            const manufacturerSelect = document.getElementById(`manufacturer-${formCount}`);
            if (manufacturerSelect) {
                loadOptions(manufacturerSelect, '/api/manufacturers');
            } else {
                console.error(`Manufacturer select element for formCount=${formCount} not found.`);
            }
        }, 0);


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

    // 条件を満たさない場合はスキップ
    if (!window.shouldInitializeForms) {
        console.log("Skipping form initialization due to condition.");
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
/// ==============================
// データ保存と復元: 検索フォームと選択タイヤの分離
// ==============================

// 検索フォームデータを保存
function saveFormData() {
    // すべてのコピーされたフォームを取得
    const forms = document.querySelectorAll('.copied-tire-form');
    const formData = Array.from(forms).map(form => {
        // 各フォーム内の入力データを収集
        const inputs = form.querySelectorAll('input, select');
        return Array.from(inputs).reduce((acc, input) => {
            acc[input.name] = input.value;
            return acc;
        }, {});
    });

    // データをsessionStorageに保存
    sessionStorage.setItem('tireFormData', JSON.stringify(formData));
    console.log('フォームデータを保存しました:', formData);
}

// 保存されたフォームデータを復元する
function restoreFormData() {
    const formData = JSON.parse(sessionStorage.getItem('tireFormData'));
    if (!formData) return; // 保存データがない場合は何もしない

    const container = document.getElementById('copied-list');
    formData.forEach(data => {
        addTireForm('copied-list'); // 新しいフォームを追加
        const form = container.lastElementChild; // 追加されたフォームを取得

        // 各入力フィールドに保存データを設定
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (data[input.name] !== undefined) {
                input.value = data[input.name];
            }
        });
    });
    console.log('フォームデータを復元しました:', formData);
}

// 選択タイヤデータを保存
function saveSelectedTires() {
    const selectedTires = Array.from(document.querySelectorAll('.copied-tire-form')).map(form => {
        return {
            manufacturer: form.querySelector(`[name="manufacturer[]"]`).value,
            manufacturing_year: form.querySelector(`[name="manufacturing_year[]"]`).value,
            tread_depth: form.querySelector(`[name="tread_depth[]"]`).value,
            uneven_wear: form.querySelector(`[name="uneven_wear[]"]`).value,
            other_details: form.querySelector(`[name="other_details[]"]`).value,
        };
    });
    sessionStorage.setItem('selectedTires', JSON.stringify(selectedTires));
    console.log('Selected tires saved:', selectedTires);
}

// 選択タイヤデータを復元
function restoreSelectedTires() {
    const selectedTires = JSON.parse(sessionStorage.getItem('selectedTires')) || [];
    const container = document.getElementById('copied-list');
    selectedTires.forEach(data => addTireForm('copied-list', data));
    console.log('Selected tires restored:', selectedTires);
}

// フォームリセット
function resetFormData() {
    sessionStorage.removeItem('tireFormData');
    console.log('Form data reset.');
}



// ==============================
// ページロード時の初期化処理
// ==============================

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOMContentLoaded event fired. Initializing forms...");
    console.log("Resetting formCount to 0.");
    formCount = 0; // フォームカウントをリセット

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

    // 共通データの再表示
    if (typeof invalidCommonData !== 'undefined' && invalidCommonData) {
        console.log("Repopulating common data...");

        // 共通データフィールドを取得
        const widthField = document.querySelector('select[name="width"]');
        const aspectRatioField = document.querySelector('select[name="aspect_ratio"]');
        const inchField = document.querySelector('select[name="inch"]');
        const plyRatingField = document.querySelector('select[name="ply_rating"]');

        // 値を反映
        if (widthField && invalidCommonData.width) {
            widthField.value = invalidCommonData.width;
        }
        if (aspectRatioField && invalidCommonData.aspect_ratio) {
            aspectRatioField.value = invalidCommonData.aspect_ratio;
        }
        if (inchField && invalidCommonData.inch) {
            inchField.value = invalidCommonData.inch;
        }
        if (plyRatingField && invalidCommonData.ply_rating) {
            plyRatingField.value = invalidCommonData.ply_rating;
        }

        console.log("Common data fields updated.");
    }
    
    // ページロード時に invalidEntries の有無を確認
    if (typeof invalidEntries !== 'undefined' && Array.isArray(invalidEntries) && invalidEntries.length > 0) {
        console.log("Invalid entries detected. Handling error forms...");

        // 無効データが1本の場合、テンプレートフォームにデータを反映
        if (invalidEntries.length === 1) {
            console.log("Single invalid entry detected. Assigning to template form...");
            const entry = invalidEntries[0];

            // テンプレートのフォームに値をセット
            document.querySelector('select[name="manufacturer"]').value = entry.manufacturer || "0";
            document.querySelector('select[name="manufacturing_year"]').value = entry.manufacturing_year || "0";
            document.querySelector('select[name="tread_depth"]').value = entry.tread_depth || "0";
            document.querySelector('select[name="uneven_wear"]').value = entry.uneven_wear || "";
            document.querySelector('input[name="other_details"]').value = entry.other_details || "";

            console.log("Template form populated with invalid entry.");
        } 
        // 無効データが複数本の場合
        else {
            console.log(`Multiple invalid entries detected (${invalidEntries.length}). Initializing error forms...`);

            // テンプレートフォームに最初のデータを反映
            const firstEntry = invalidEntries[0];
            document.querySelector('select[name="manufacturer"]').value = firstEntry.manufacturer || "0";
            document.querySelector('select[name="manufacturing_year"]').value = firstEntry.manufacturing_year || "0";
            document.querySelector('select[name="tread_depth"]').value = firstEntry.tread_depth || "0";
            document.querySelector('select[name="uneven_wear"]').value = firstEntry.uneven_wear || "";
            document.querySelector('input[name="other_details"]').value = firstEntry.other_details || "";

            console.log("Template form populated with the first invalid entry.");

            // 残りのデータを動的フォームで生成
            const remainingEntries = invalidEntries.slice(1);
            regenerateTireForm('copied-list', remainingEntries);
        }
    } 
    // 無効データがない場合は通常の初期化を実行
    else {
        console.log("No invalid entries detected. Initializing default forms...");
        initializeDefaultForms();
    }

    // コピー機能のイベントリスナーをセットアップ
    const copyButton = document.getElementById('copy-button');
    if (copyButton) {
        copyButton.addEventListener('click', () => {
            addTireForm('copied-list');
        });
    }

    // 動的ボタン用のイベント委譲
    const copiedListContainer = document.getElementById('copied-list');
    if (copiedListContainer) {
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
    } else {
        console.error("Copied list container not found!");
    }
});

// デバッグコードをここに追加
console.log(`Generated select element: ${document.getElementById(`uneven_wear-${formCount}`).outerHTML}`);
