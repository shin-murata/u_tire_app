// ==============================
// ユーティリティ関数
// ==============================

// 選択肢を動的に生成する関数
function generateOptions(values, formatFn) {
    return values.map(value => `<option value="${value}">${formatFn(value)}</option>`).join('');
}

// ==============================
// フォーム操作
// ==============================

let formCount = 0; // フォーム数カウンター

async function loadOptions(selectElement, apiUrl) {
    try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error(`Failed to fetch options from ${apiUrl}`);
        const { data } = await response.json();
        
        // 選択肢をリセット
        selectElement.innerHTML = ''; // 初期化
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.name || item.value;
            selectElement.appendChild(option);
        });
    } catch (error) {
    console.error(`Error loading options for ${selectElement.name}:`, error);
    }
}

// 初期化: 共通フォームのロード
function initializeForm(selectors) {
    selectors.forEach(({ selector, api }) => {
        const element = document.querySelector(selector);
        if (element) {
            loadOptions(element, api);
        }
    });
}

// フォームを追加する関数
function addTireForm(targetContainerId) {
    const container = document.querySelector(`#${targetContainerId}`);
    if (!container) {
        console.error(`Container with ID '${targetContainerId}' not found.`);
        return;
    }

    formCount++; // フォームカウントをインクリメント

    // 個別データフォームを生成
    const formHTML = `
        <div class="copied-tire-form">
            <!-- グループ1: manufacturer, manufacturing_year -->
            <div class="form-group group-1 group-1-style">
                <div class="input-wrap manufacturer-wrap">
                    <select name="manufacturer[]" id="manufacturer-${formCount}" class="form-control">
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

    container.insertAdjacentHTML("beforeend", formHTML);

    // 新しいフォームのオプションをロード
    const manufacturerSelect = document.querySelector(`#manufacturer-${formCount}`);
    loadOptions(manufacturerSelect, '/api/manufacturers');
}

document.addEventListener('DOMContentLoaded', () => {
    const copiedListContainer = document.getElementById('copied-list');

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

// ==========================================
// フィルタープルダウン更新のスクリプト
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    console.log("Filters:", typeof filters, filters);

    if (typeof filters === "undefined") {
        console.error("Filters data is not available!");
        console.log("Filters value:", filters);
        console.error("Filters data is not defined! Please ensure it is properly set.");
        var filters = {}; // 仮のデータを設定
    }

    const filterColumn = document.getElementById("filter_column");
    const filterValue = document.getElementById("filter_value");

    if (!filterColumn || !filterValue) {
        console.error("Filter elements are not available in the DOM!");
        return;
    }

    // 初期ロード時にフィルターデータを更新
    updateFilterValuesFromFilters();

    // フィルターカラム変更時にフィルターデータを更新
    filterColumn.addEventListener("change", () => {
        const selectedColumn = filterColumn.value;
        if (filters[selectedColumn]) {
            updateFilterValuesFromFilters();
        } else {
            updateFilterValuesFromAPI(selectedColumn);
        }
    });

    // filters 変数を利用してプルダウンを更新
    function updateFilterValuesFromFilters() {
        console.log("Before updateFilterValuesFromFilters:", filterValue.innerHTML);
        filterValue.innerHTML = '<option value="">選択してください</option>';
        const selectedColumn = filterColumn.value;
        console.log("After reset innerHTML:", filterValue.innerHTML);

        if (filters[selectedColumn]) {
            const blankOption = document.createElement("option");
            blankOption.value = "NULL";
            blankOption.textContent = "空欄";
            filterValue.appendChild(blankOption);

            filters[selectedColumn].forEach(value => {
                const option = document.createElement("option");
                option.value = value || "NULL";
                option.textContent = value || "空欄";
                filterValue.appendChild(option);
            });
            console.log("After appending options:", filterValue.innerHTML);
        }
    }

    // API から値を取得してプルダウンを更新
    function updateFilterValuesFromAPI(columnName) {
        filterValue.innerHTML = '<option value="">選択してください</option>';
        if (!columnName) return;

        fetch(`/api/unique_values/${columnName}`)
            .then(response => response.json())
            .then(data => {
                data.data.forEach(value => {
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = value;
                    filterValue.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching filter values:', error));
    }

    // メーカー関連の初期化
    (async () => {
        try {
            const response = await fetch('/api/manufacturers'); // エンドポイントからデータを取得
            const result = await response.json(); // データをJSONとしてパース
            const manufacturers = result.data; // 'data'キーからリストを取得
            const formCount = 1;

            const manufacturerSelect = document.getElementById(`manufacturer-${formCount}`);
            if (manufacturerSelect) {

                console.log("Before appending defaultOption:", manufacturerSelect.innerHTML);
                // 初期値の設定
                const defaultOption = document.createElement('option');
                defaultOption.value = 0;
                defaultOption.textContent = "メーカー";
                defaultOption.disabled = true; // 選択不可に設定
                defaultOption.selected = true; // 初期選択状態に設定
                manufacturerSelect.appendChild(defaultOption);

                console.log("After appending defaultOption:", manufacturerSelect.innerHTML);

                // 動的に選択肢を追加
                manufacturers.forEach(manufacturer => {
                    const option = document.createElement('option');
                    option.value = manufacturer.id;
                    option.textContent = manufacturer.name;
                    manufacturerSelect.appendChild(option);
                });

                console.log("After appending manufacturers:", manufacturerSelect.innerHTML);

                // 初期選択を明示的に設定（冗長チェック）
                manufacturerSelect.value = "0";
                // デバッグ: 最終HTMLの確認
                console.log(manufacturerSelect.innerHTML);
            }
        } catch (error) {
            console.error('Error fetching manufacturers:', error);
        }
    })();
});
