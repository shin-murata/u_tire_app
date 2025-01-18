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
// フォーム操作
// ==============================

let formCount = 0; // フォーム数カウンター

// 新しいタイヤフォームを動的に追加する関数
// targetContainerId: フォームを追加するコンテナID, defaultValues: 初期値のオブジェクト
function addTireForm(targetContainerId, defaultValues = {}) {
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

    // 新しく生成されたセレクトボックスを取得してデバッグ
    const newUnevenWearSelect = document.getElementById(`uneven_wear-${formCount}`);
    console.log(`Generated select element: ${newUnevenWearSelect.outerHTML}`);

    // 挿入したフォームに値を設定
    const form = container.lastElementChild;
    form.querySelector(`[name="manufacturer[]"]`).value = defaultValues.manufacturer || '0';
    form.querySelector(`[name="manufacturing_year[]"]`).value = defaultValues.manufacturing_year || '0';
    form.querySelector(`[name="tread_depth[]"]`).value = defaultValues.tread_depth || '';
    form.querySelector(`[name="uneven_wear[]"]`).value = defaultValues.uneven_wear || '';
    form.querySelector(`[name="other_details[]"]`).value = defaultValues.other_details || '';

    // メーカーの選択肢を動的にロード
    const manufacturerSelect = document.querySelector(`#manufacturer-${formCount}`);
    if (manufacturerSelect) {
        console.log(`Manufacturer select element for formCount=${formCount}:`, manufacturerSelect);
        loadOptions(manufacturerSelect, '/api/manufacturers');
    } else {
        console.error(`Manufacturer select element for formCount=${formCount} not found.`);
    }
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
// 初期化処理
// ==============================

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOMContentLoaded event fired.");
    console.log("Page fully loaded. Checking initial select elements...");

    // Pythonから渡された無効データ
    const invalidEntries = JSON.parse('{{ invalid_entries | tojson | safe }}');
    console.log("Invalid entries received:", invalidEntries);

    // 無効データがある場合、フォームを生成して値を設定
    if (invalidEntries.length > 0) {
        invalidEntries.forEach(entry => {
            addTireForm('copied-list', {
                manufacturer: entry.manufacturer || '',
                manufacturing_year: entry.manufacturing_year || '',
                tread_depth: entry.tread_depth || '',
                uneven_wear: entry.uneven_wear || '',
                other_details: entry.other_details || '',
            });
        });
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

document.addEventListener('DOMContentLoaded', () => {
    restoreFormData(); // 保存データを復元

    // フォーム追加ボタンのイベント
    document.getElementById('copy-button').addEventListener('click', () => {
        addTireForm('copied-list');
    });

    // 入力イベントでフォームデータを保存
    const formContainer = document.getElementById('copied-list');
    formContainer.addEventListener('input', saveFormData);
});


// デバッグコードをここに追加
console.log(`Generated select element: ${document.getElementById(`uneven_wear-${formCount}`).outerHTML}`);
