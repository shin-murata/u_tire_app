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
                    <label for="manufacturer-${formCount}">メーカー:</label>
                    <select name="manufacturer[]" id="manufacturer-${formCount}" class="form-control"></select>
                </div>
                <div class="input-wrap manufacturing-year-wrap">
                    <label for="manufacturing_year-${formCount}">製造年:</label>
                    <input type="text" name="manufacturing_year[]" id="manufacturing_year-${formCount}" class="form-control">
                </div>
        </div>

        <!-- グループ2: tread_depth, uneven_wear, other_details -->
        <div class="form-group group-2 group-2-style">
            <div class="input-wrap small-input" id="tread-depth">
                <label for="tread_depth-${formCount}">残り溝:</label>
                <input type="number" name="tread_depth[]" id="tread_depth-${formCount}" class="form-control">
            </div>
            <div class="input-wrap small-input" id="uneven-wear">
                <label for="uneven_wear-${formCount}">片減り:</label>
                <input type="text" name="uneven_wear[]" id="uneven_wear-${formCount}" class="form-control">
            </div>
            <div class="input-wrap large-input" id="other-details">
                <label for="other_details-${formCount}">その他:</label>
                <input type="text" name="other_details[]" id="other_details-${formCount}" class="form-control">
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
    if (typeof filters === "undefined") {
        console.error("Filters data is not available!");
        return;
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
        filterValue.innerHTML = '<option value="">選択してください</option>';
        const selectedColumn = filterColumn.value;

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
});
