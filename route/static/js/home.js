$(document).ready(function () {
    let masterKeyList = window.master_key || [];
    let usedKeys = [];

    //キーイベント系
    //enterで送信しない
    $(document).on("keydown", "input", function (e) {
        // Enterキー押下時
        if (e.key === "Enter") {
            e.preventDefault();  // フォーム送信を防止
        }
    });

    let isDragging = false;
    let selectedInputs = new Set();
    let lastTypedValue = "";
    let isSyncing = false; // ← 再帰イベント防止フラグ

    // セル選択処理
    $(document).on("mousedown", ".input_room", function (e) {
        e.preventDefault();
        isDragging = true;
        clearSelection();
        addSelection(this);
        $(this).focus();
    });

    $(document).on("mouseover", ".input_room", function () {
        if (isDragging) {
            addSelection(this);
        }
    });

    $(document).on("mouseup", function () {
        isDragging = false;
    });

    // 選択追加
    function addSelection(input) {
        selectedInputs.add(input);
        $(input).addClass("selected");
    }

    // 選択解除
    function clearSelection() {
        selectedInputs.forEach(input => $(input).removeClass("selected"));
        selectedInputs.clear();
    }

    // 入力された値を保存（手入力のときのみ）
    $(document).on("input", ".input_room", function () {
        if (isSyncing) return; // 他セル同期中ならスキップ
        if (!selectedInputs.has(this)) return;

        lastTypedValue = $(this).val();

        // 他の選択セルに反映
        isSyncing = true;
        selectedInputs.forEach(input => {
            if (input !== this) {
                $(input).val(lastTypedValue);
            }
        });
        isSyncing = false;
    });
    // ESCキーで選択解除
    $(document).on("keydown", function (e) {
        if (e.key === "Escape") {
            clearSelection();
        }
    });

    //エンターの処理
    $(document).on("keydown", ".bottom_table input", function (e) {
        if (e.key !== "Enter") return;

        e.preventDefault();

        const $currentInput = $(this);
        const $currentTd = $currentInput.closest("td");
        const colIndex = $currentTd.index();
        const $currentTr = $currentInput.closest("tr");
        const $tableBody = $currentTr.closest("tbody");

        const $rows = $tableBody.find("tr");
        const currentRowIndex = $rows.index($currentTr);
        const $nextRow = $rows.eq(currentRowIndex + 1);

        if ($nextRow.length > 0) {
            const $nextInput = $nextRow.find("td").eq(colIndex).find("input");
            if ($nextInput.length > 0) {
                $nextInput.focus();
            }
        }
    });

    //部屋情報表のtab・enter移動
    $(document).on("keydown", ".input_room", function (e) {
        const inputs = $(".input_room");
        const index = inputs.index(this);

        // Enterキーで次の行の同じ列へ
        if (e.key === "Enter") {
            e.preventDefault();
            const currentTd = $(this).closest("td");
            const currentTr = $(this).closest("tr");
            const colIndex = currentTr.find("td").index(currentTd);

            const nextTr = currentTr.next("tr");
            if (nextTr.length) {
                const nextInput = nextTr.find("td").eq(colIndex).find(".input_room");
                if (nextInput.length) {
                    nextInput.focus();
                }
            }
        }
        // Tabキーで通常の右移動だが、最終列なら次行の先頭へ（オプション）
        if (e.key === "Tab" && !e.shiftKey) {
            const isLast = index === inputs.length - 1;
            if (!isLast) {
                setTimeout(() => {
                    inputs.eq(index + 1).focus();
                }, 0);
            }
        }
    });
    //ハウスさん表のtab・enter移動
    $(document).on("keydown", "#house_table_body input", function (e) {
        const inputs = $("#house_table_body input:visible");
        const index = inputs.index(this);

        if (e.key === "Enter") {
            e.preventDefault();

            // 現在のinputのセル、列インデックスを取得
            const currentTd = $(this).closest("td");
            const currentTr = $(this).closest("tr");
            const colIndex = currentTr.find("td").index(currentTd);

            // 次の行を取得
            const nextTr = currentTr.next("tr");
            if (nextTr.length) {
                const nextInput = nextTr.find("td").eq(colIndex).find("input");
                if (nextInput.length) {
                    nextInput.focus();
                }
            }
        }

        // オプション：最後の input 以外で Tab で右へ
        if (e.key === "Tab" && !e.shiftKey) {
            const isLast = index === inputs.length - 1;
            if (!isLast) {
                setTimeout(() => {
                    inputs.eq(index + 1).focus();
                }, 0);
            }
        }
    });
    $(document).on("keydown", "#clean_method_body input", function (e) {
        const $currentInput = $(this);
        const $currentTd = $currentInput.closest("td");
        const $currentTr = $currentTd.closest("tr");
        const $allRows = $("#clean_method_body tr");
        const currentCol = $currentTd.index();
        const currentRowIndex = $allRows.index($currentTr);

        const $inputsInRow = $currentTr.find("input");

        if (e.key === "Tab" && !e.shiftKey) {
            // 行内で右のセルに移動（列末なら通常のタブ動作）
            const indexInRow = $inputsInRow.index(this);
            if (indexInRow < $inputsInRow.length - 1) {
                e.preventDefault();
                $inputsInRow.eq(indexInRow + 1).focus();
            }
        }

        if (e.key === "Enter") {
            e.preventDefault();

            const $nextTr = $currentTr.next("tr");

            // 次の行があれば、同じ列の次行のセルに移動
            if ($nextTr.length > 0) {
                const $nextInput = $nextTr.find("td").eq(currentCol).find("input").eq(0);
                if ($nextInput.length > 0) {
                    $nextInput.focus();
                    return;
                }
            }

            // ↓↓↓ 最後の行だった場合：同じグループの次の列の先頭へ ↓↓↓

            const isEco = $currentTd.hasClass("td_eco");
            const isDuvet = $currentTd.hasClass("td_duvet");

            if (isEco || isDuvet) {
                // 同じ tr を使って、同じグループ内の次の列へ
                const $inputsInGroup = isEco ? $currentTr.find(".input_eco") :
                    isDuvet ? $currentTr.find(".input_duvet") : $();

                const indexInGroup = $inputsInGroup.index(this);
                if (indexInGroup !== -1 && indexInGroup < $inputsInGroup.length - 1) {
                    const $firstInputInNextCol = $allRows.eq(0)
                        .find(isEco ? ".input_eco" : ".input_duvet")
                        .eq(indexInGroup + 1);

                    if ($firstInputInNextCol.length > 0) {
                        $firstInputInNextCol.focus();
                    }
                }
            }
        }
    });

    //エコ・アメ・デュべのカウント更新
    updateCounts(); 
    $(document).on('input', '.input_eco, .input_amenity, .input_duvet', function () {
        updateCounts(); // 入力変更時
    });

    //連泊部屋数のカウント更新
    updateMultipleNightCount();
    $(document).on('input', '.input_multiple_night_room', function () {
        updateMultipleNightCount(); // 入力変更時
    });

    //ハウスさん表の番号が入力された際の処理
    $(document).on("input", ".input_no, .input_name", function () {
        checkAndAddRow();
        updateHouseCount();
        updateHouseFloorAssignments();
        updateNoneStyling();
    });
    //部屋情報表が入力された際の処理
    $(document).on("input", ".input_room", function () {
        updateHouseCount();
        updateHouseFloorAssignments();
        updateMutedRooms();
        updateNoneStyling();
        updateRoomStats();
    });
    //ハウスさん表の番号が変更された際の処理
    $(document).on("change", ".input_no", function (e) {
        const result = checkDuplicateNo($(this));
        if (result === false) {
            e.preventDefault();
        }
    });
    //エコ・アメ・デュべ表のエコ・デュべが入力された時の処理
    $(document).on("input", ".input_amenity,.input_eco, .input_duvet", function () {
        highlightRooms();
    });
    //エコ・アメ・デュべ表のエコ・アメ・デュべが入力された時の処理
    $(document).on("input", ".input_eco, .input_amenity, .input_duvet", function () {
        checkAndAddCleanMethodRow();
    });
    //備考表の部屋番号・備考が入力された時の処理
    $(document).on("input", ".input_remark_room, .input_remark", function () {
        checkAndAddRemarkRow();
    });
    //スポット清掃表の部屋番号・スポット清掃内容が入力された時の処理
    $(document).on("input", ".input_spot_number, .input_spot", function () {
        checkAndAddSpotRow();
    });
    //ハウスさん表の名前が入力された時の処理
    $(document).on("input", ".input_name", function () {
        checkAndAddRow();
        updateHouseCount();
        updateHouseFloorAssignments();
        updateNoneStyling();
        updateResultTableColumns();
    });
    //
    $(document).on("input", ".input_name, .input_no, .input_bath", function () {
        updateResultTableColumns();
    });
    $(document).on("input", ".input_name, .input_no, .input_bath, .input_room, .input_eco", function () {
        updateResultTableColumns();
        updateAssignedRoomRows();
    });

    $(document).on("input", ".input_name, .input_no, .input_bath, .input_room, .input_eco, .room_type_time, #bath_time", function () {
        updateResultTableColumns();
        updateAssignedRoomRows();
        updateEndTimeRow();
    });

    $(document).on("input", ".input_no, .input_name, .input_room", function () {
        syncHiddenHouseFields();
    });
    $(document).on("input", ".room_change_original, .room_change_destination", function () {
        checkAndAddRoomChangeRow();
    });
    $(document).on("input", ".outin_room", function () {
        checkAndAddOutInRow(this);
    });
    $(document).on("input", ".multiple_night_clean_room", function () {
        checkAndAddMultipleNightCleanRow(this);
        updateOthersWithMultipleNightCleans();
    });
    // 初期値を保存して、既に入力済みのセルで不要に行が追加されるのを防ぐ
    $(".outin_room").each(function () {
        $(this).data('prev', $(this).val().trim());
    });
    $(document).on("input", ".must_clean_room, .must_clean_reason", function () {
        checkAndAddMustCleanRow();
    });

    //連絡事項欄
    $(document).on("input", ".input_contact_number, .input_contact", function () {
        checkAndAddContactRow();
    });



    updateHouseCount();
    updateHouseFloorAssignments();
    updateMutedRooms();
    updateNoneStyling();
    highlightRooms();
    updateEndTimeRow();
    updateRoomStats();
    updateResultTableColumns();
    updateAssignedRoomRows();
    

    if (window.method === "POST") {
        updateResultTableColumns();
        updateAssignedRoomRows();
        updateEndTimeRow();
        // JSONファイルから読み込まれていない場合のみ自動更新
        if (window.json_loaded_flag === 0) {
            updateHouseKeys();
            updateDdCells();
        }
    }


    //タイトル行の「キー」をクリックした時の処理
    $("#key_header").on("click", function () {
        updateHouseKeys();
    });

    //タイトル行の「DD」をクリックした時の処理
    $("#dd_header").on("click", function () {
        updateDdCells();
    });


    //表移動
    function setupNavigation(inputClass, tdClass) {
        $(document).on("keydown", inputClass, function (e) {
            const $current = $(this);
            const $td = $current.closest(tdClass);
            const $tr = $current.closest("tr");
            const $inputs = $td.find(inputClass);
            const index = $inputs.index(this);

            // Enterキー: 次の行の同じ列の同じ位置へ
            if (e.key === "Enter") {
                e.preventDefault();
                const $nextTr = $tr.next("tr");
                if ($nextTr.length > 0) {
                    const $nextTd = $nextTr.find(tdClass);
                    const $nextInputs = $nextTd.find(inputClass);
                    if ($nextInputs.length > index) {
                        $nextInputs.eq(index).focus();
                    }
                }
            }

            // Tabキー: 同じ列の中で移動し、最後なら次の行へ
            if (e.key === "Tab" && !e.shiftKey) {
                e.preventDefault();
                if (index < $inputs.length - 1) {
                    $inputs.eq(index + 1).focus();
                } else {
                    const $nextTr = $tr.next("tr");
                    if ($nextTr.length > 0) {
                        const $nextTd = $nextTr.find(tdClass);
                        const $nextInputs = $nextTd.find(inputClass);
                        if ($nextInputs.length > 0) {
                            $nextInputs.eq(0).focus();
                        }
                    }
                }
            }
        });
    }

    // エコ・アメ・デュべに対して適用
    setupNavigation(".input_eco", ".td_eco");
    setupNavigation(".input_amenity", "td:nth-child(2)");
    setupNavigation(".input_duvet", ".td_duvet");

    //エコ・アメ・デュべのカウント更新
    function updateCounts() {
        const ecoCount = $('.input_eco').filter(function () {
            return $(this).val().trim() !== '';
        }).length;

        const amenityCount = $('.input_amenity').filter(function () {
            return $(this).val().trim() !== '';
        }).length;

        const duvetCount = $('.input_duvet').filter(function () {
            return $(this).val().trim() !== '';
        }).length;

        $('#eco-count').text(`(${ecoCount})`);
        $('#amenity-count').text(`(${amenityCount})`);
        $('#duvet-count').text(`(${duvetCount})`);
    }

    //連泊部屋数
    function updateMultipleNightCount() {
        let count = 0;

        $('.input_multiple_night_room').each(function () {
            if ($(this).val().trim() !== '') {
                count++;
            }
        });

        $('#multiple-count').text(`(${count})`);
    }

    //ハウスさん表の行追加
    function checkAndAddRow() {
        let allNameFilled = true;
        let allNoFilled = true;

        $(".input_name").each(function () {
            if ($(this).val().trim() === "") {
                allNameFilled = false;
            }
        });

        $(".input_no").each(function () {
            if ($(this).val().trim() === "") {
                allNoFilled = false;
            }
        });

        let lastRow = $(".tr_house").last();
        let lastNo = lastRow.find(".input_no").val().trim();
        let lastName = lastRow.find(".input_name").val().trim();
        let lastEmpty = (lastNo === "" && lastName === "");

        if ((allNameFilled || allNoFilled) && !lastEmpty) {
            let rowCount = $(".tr_house").length + 1;
            let valueAttr = rowCount <= 10 ? `value="${rowCount}"` : "";

            let newRow = `
                <tr class="tr_house">
                    <td class="td_no">
                        <input type="number" name="no_${rowCount}" id="no_${rowCount}" class="input_no" ${valueAttr} min="1">
                    </td>
                    <td class="td_name">
                        <input type="text" name="name_${rowCount}" id="name_${rowCount}" class="input_name">
                    </td>
                     <td>
                        <p class="count_cell" id="count_${rowCount}">0</p>
                    </td>
                    <td>
                        <p class="floor_cell" id="floor_${rowCount}"></p>
                    </td>
                    <td>
                        <input type="text" name="key_${rowCount}" id="key_${rowCount}" class="key_cell" value="">
                    </td>
                    <td>
                        <input type="text" name="dd_${rowCount}" id="dd_${rowCount}" class="dd_cell" value="">
                    </td>
                    <td class="td_eng">
                        <input type="checkbox" name="eng_${rowCount}" id="eng_${rowCount}" class="eng_cell" value="on">
                    </td>
                </tr>
            `;

            $("#house_table_body").append(newRow);
        }
    }

    //マスターキーの更新
    function updateHouseKeys() {
        const { availableKeysByFloor, fallbackOrder } = buildMasterKeyConfig();
        const usedKeysByFloor = {};
        const rowDataList = [];

        // === 1. 初期割り当て（CSVで渡されたキー順に） ===
        $(".tr_house").each(function () {
            const $row = $(this);
            const floorsText = $row.find(".floor_cell").text().trim();

            if (!floorsText) {
                $row.find(".key_cell").val("");
                rowDataList.push({ $row, floors: [], keys: [] });
                return;
            }

            const floors = floorsText.split(',').map(f => f.trim());
            const keys = [];

            floors.forEach(floor => {
                if (!usedKeysByFloor[floor]) usedKeysByFloor[floor] = new Set();

                const keyPriority = availableKeysByFloor[floor] || fallbackOrder;
                const assignedKey = keyPriority.find(k => !usedKeysByFloor[floor].has(k));

                if (assignedKey) {
                    usedKeysByFloor[floor].add(assignedKey);
                    keys.push(`${floor}${assignedKey}`);
                } else {
                    keys.push(`${floor}N`);
                }
            });

            rowDataList.push({ $row, floors, keys });
        });

        // === 2. キー交換による同一清掃者内のキー重複の解消 ===
        resolveDuplicateKeys(rowDataList);

        // === 3. 表に反映 ===
        rowDataList.forEach(({ $row, keys }) => {
            $row.find(".key_cell").val(keys.join(","));
        });
    }

    function buildMasterKeyConfig() {
        const availableKeysByFloor = {};
        const globalPriority = [];

        masterKeyList.forEach(item => {
            const rawValue = Array.isArray(item) ? (item[1] || item[0]) : (item || "");
            const parsed = parseKeyParts(String(rawValue).trim());
            if (!parsed) return;

            const { floor, key } = parsed;
            if (!availableKeysByFloor[floor]) availableKeysByFloor[floor] = [];
            if (!availableKeysByFloor[floor].includes(key)) {
                availableKeysByFloor[floor].push(key);
            }
            if (!globalPriority.includes(key)) {
                globalPriority.push(key);
            }
        });

        const fallbackOrder = globalPriority.length ? globalPriority : ["A", "B", "C"];
        return { availableKeysByFloor, fallbackOrder };
    }

    function parseKeyParts(keyStr) {
        const match = String(keyStr || "").trim().match(/^(\d+)([A-Za-z]+)$/);
        if (!match) return null;
        return { floor: match[1], key: match[2] };
    }

    function resolveDuplicateKeys(rowDataList) {
        for (let i = 0; i < rowDataList.length; i++) {
            const data = rowDataList[i];
            const keyCounts = {}; // 例: {A: 2, B: 1}

            data.keys.forEach(k => {
                const parsed = parseKeyParts(k);
                if (!parsed || parsed.key === "N") return;
                keyCounts[parsed.key] = (keyCounts[parsed.key] || 0) + 1;
            });

            for (const [key, count] of Object.entries(keyCounts)) {
                if (count <= 1) continue; // 重複していないキーは無視

                // 重複キーがあるので、交換候補を探す
                for (let j = 0; j < rowDataList.length; j++) {
                    if (i === j) continue;

                    const other = rowDataList[j];

                    // i と j の間で交換できるか（同じ floor を担当しているか）
                    for (let fi = 0; fi < data.keys.length; fi++) {
                        const parsedI = parseKeyParts(data.keys[fi]);
                        if (!parsedI || parsedI.key === "N") continue;

                        for (let fj = 0; fj < other.keys.length; fj++) {
                            const parsedJ = parseKeyParts(other.keys[fj]);
                            if (!parsedJ || parsedJ.key === "N") continue;

                            // 同じ階でキーが違うなら、交換を試みる
                            if (parsedI.floor === parsedJ.floor && parsedI.key !== parsedJ.key) {
                                // 交換して、両者にとって重複が減るか？
                                const keysI = data.keys.map(x => parseKeyParts(x)?.key).filter(Boolean);
                                const keysJ = other.keys.map(x => parseKeyParts(x)?.key).filter(Boolean);

                                // 仮に交換してみる
                                const tempI = [...keysI];
                                const tempJ = [...keysJ];
                                tempI[fi] = parsedJ.key;
                                tempJ[fj] = parsedI.key;

                                // 重複カウント再評価
                                const isDupI = new Set(tempI).size < tempI.length;
                                const isDupJ = new Set(tempJ).size < tempJ.length;

                                if (!isDupI && !isDupJ) {
                                    // 実際に交換
                                    const keyStrI = `${parsedI.floor}${parsedI.key}`;
                                    const keyStrJ = `${parsedJ.floor}${parsedJ.key}`;
                                    data.keys[fi] = keyStrJ;
                                    other.keys[fj] = keyStrI;
                                }
                            }
                        }
                    }
                }
            }
        }
    }


    
    //担当階を更新
    function updateHouseFloorAssignments() {
        const roomAssignments = {};

        $(".input_room").each(function () {
            const roomNumber = $(this).closest("td").data("room");
            const no = $(this).val().trim();

            if (roomNumber && no !== "") {
                roomAssignments[roomNumber] = no;
            }
        });

        $(".tr_house").each(function () {
            const $row = $(this);
            const no = $row.find(".input_no").val().trim();

            if (no === "") {
                $row.find(".floor_cell").text("");
                return;
            }

            const floors = [];

            for (const [room, assignedNo] of Object.entries(roomAssignments)) {
                if (assignedNo === no) {
                    const floor = Math.floor(parseInt(room, 10) / 100);
                    if (!floors.includes(floor)) {
                        floors.push(floor);
                    }
                }
            }

            if (floors.length > 0) {
                floors.sort((a, b) => a - b);
                const firstLine = floors.slice(0, 2).join(",");
                const secondLine = floors.slice(2).join(",");
                if (secondLine) {
                    $row.find(".floor_cell").html(firstLine + "<br>" + secondLine);
                } else {
                    $row.find(".floor_cell").text(firstLine);
                }
            } else {
                $row.find(".floor_cell").text("");
            }
        });

        if (method === "GET") {
            {
                updateHouseKeys();
                updateDdCells();
            }
        }
    }

    //ハウスさん表でNone表示の時の処理
    function updateNoneStyling() {
        $(".count_cell, .floor_cell").each(function () {
            const isInput = $(this).is("input");
            const value = isInput ? $(this).val().trim() : $(this).text().trim();

            if (value === "") {
                $(this).addClass("non-bold");
            } else {
                $(this).removeClass("non-bold");
            }
        });

    }

    //担当部屋数カウント
    function updateHouseCount() {
        let roomValues = [];
        $(".input_room").each(function () {
            const val = $(this).val().trim();
            if (val !== "") {
                roomValues.push(val);
            }
        });

        $(".tr_house").each(function () {
            const $row = $(this);
            const noVal = $row.find(".input_no").val().trim();
            let count = 0;

            if (noVal !== "") {
                count = roomValues.filter(room => room === noVal).length;
            }

            $row.find(".count_cell").text(count);
        });
    }

    //清掃不要の場合の処理
    function updateMutedRooms() {
        $(".input_room").each(function () {
            const $input = $(this);
            const value = $input.val().trim();
            const $cell = $input.closest("td");

            if (value === "0") {
                $cell.addClass("room-muted");
            } else {
                $cell.removeClass("room-muted");
            }
        });
    }

    //エコ・デュべの時の処理
    function highlightRooms() {
        $('[data-room]').css('background-color', '');

        let ameRooms = new Set();
        let ecoRooms = new Set();

        $('.input_eco').each(function () {
            let roomNumber = $(this).val().trim();
            if (roomNumber !== '') {
                ecoRooms.add(roomNumber);
                $('[data-room="' + roomNumber + '"]').css('background-color', 'yellow');
            }
        });

        // $('.input_duvet').each(function () {
        //     let roomNumber = $(this).val().trim();
        //     if (roomNumber !== '' && !ecoRooms.has(roomNumber)) {
        //         $('[data-room="' + roomNumber + '"]').css('background-color', 'lightblue');
        //     }
        // });

        $('.input_amenity').each(function () {
            const roomNumber = $(this).val().trim();
            if (roomNumber !== '') {
                ameRooms.add(roomNumber);
                $('[data-room="' + roomNumber + '"]').css('background-color', 'rgb(255, 203, 135)');
            }
        });
    }

    //ハウスさん表で番号重複を管理
    function checkDuplicateNo(currentInput) {
        const currentVal = currentInput.val().trim();
        if (currentVal === "") return;

        let isDuplicate = false;

        $(".input_no").each(function () {
            const val = $(this).val().trim();
            if (val === "") return;

            if (val === currentVal && this !== currentInput[0]) {
                isDuplicate = true;
                return false;
            }
        });

        if (isDuplicate) {
            alert("このNoはすでに使われています。別の番号を入力してください。");
            currentInput.val("").focus();
            return false;
        }
    }

    //エコ・アメ・デュべ表で行追加
    function checkAndAddCleanMethodRow() {
        let allEcoFilled = true;
        let allAmenityFilled = true;
        let allDuvetFilled = true;

        $(".input_eco").each(function () {
            if ($(this).val().trim() === "") {
                allEcoFilled = false;
            }
        });

        $(".input_amenity").each(function () {
            if ($(this).val().trim() === "") {
                allAmenityFilled = false;
            }
        });

        $(".input_duvet").each(function () {
            if ($(this).val().trim() === "") {
                allDuvetFilled = false;
            }
        });

        let lastRow = $(".tr_clean_method").last();
        let lastEmpty = lastRow.find("input").filter(function () {
            return $(this).val().trim() !== "";
        }).length === 0;

        if ((allEcoFilled || allAmenityFilled || allDuvetFilled) && !lastEmpty) {
            let newRow = `
                <tr class="tr_clean_method">
                    <td class="td_eco">
                        <input type="text" name="eco_room" class="input_eco">
                        <input type="text" name="eco_room" class="input_eco">
                        <input type="text" name="eco_room" class="input_eco">
                    </td>
                    <td>
                        <input type="text" name="amenity" class="input_amenity">
                    </td>
                    <td class="td_duvet">
                        <input type="text" name="duvet" class="input_duvet">
                        <input type="text" name="duvet" class="input_duvet">
                    </td>
                </tr>
            `;

            $("#clean_method_body").append(newRow);
        }
    }

    //備考表の行追加
    function checkAndAddRemarkRow() {
        let allRoomsFilled = true;
        let allRemarksFilled = true;

        $(".input_remark_room").each(function () {
            if ($(this).val().trim() === "") {
                allRoomsFilled = false;
            }
        });

        $(".input_remark").each(function () {
            if ($(this).val().trim() === "") {
                allRemarksFilled = false;
            }
        });

        let lastRow = $(".input_remark_room").last().val().trim() === "" &&
            $(".input_remark").last().val().trim() === "";

        if ((allRoomsFilled || allRemarksFilled) && !lastRow) {
            let rowCount = $(".input_remark").length + 1;

            let newRow = `
                <tr>
                    <td>
                        <input type="text" name="remark_room_${rowCount}" id="remark_room_${rowCount}" class="input_remark_room">
                    </td>
                    <td>
                        <input type="text" name="remark_${rowCount}" id="remark_${rowCount}" class="input_remark">
                    </td>
                </tr>
            `;

            $("#remark_table_body").append(newRow);
        }
    }

    //スポット清掃表の行追加
    function checkAndAddSpotRow() {
        let allRoomsFilled = true;
        let allSpotsFilled = true;

        $(".input_spot_number").each(function () {
            if ($(this).val().trim() === "") {
                allRoomsFilled = false;
            }
        });

        $(".input_spot").each(function () {
            if ($(this).val().trim() === "") {
                allSpotsFilled = false;
            }
        });

        let lastRow = $(".input_spot_number").last().val().trim() === "" &&
            $(".input_spot").last().val().trim() === "";

        if ((allRoomsFilled || allRemarksFilled) && !lastRow) {
            let rowCount = $(".input_spot").length + 1;

            let newRow = `
                <tr>
                    <td>
                        <input type="text" name="spot_number_${rowCount}" id="spot_number_${rowCount}" class="input_spot_number">
                    </td>
                    <td>
                        <input type="text" name="spot_${rowCount}" id="spot_${rowCount}" class="input_spot"></textarea>
                    </td>
                </tr>
            `;

            $("#spot_table_body").append(newRow);
        }
    }

    //清掃指示表の番号行・氏名行と大浴場清掃を管理
    function updateResultTableColumns() {
        const headerRowNo = $("#result_table_header_no");
        const headerRowName = $("#result_table_header_name");
        const bathRow = $("#bath_row");

        // 初期化
        headerRowNo.empty().append("<th></th>");
        headerRowName.empty().append("<th></th>");
        bathRow.empty().append("<td><strong>大浴場清掃</strong></td>");

        const bathAssignedNos = [];
        $(".input_bath").each(function () {
            const val = $(this).val().trim();
            if (val !== "" && val !== "0") {
                bathAssignedNos.push(val);
            }
        });

        const assignedNos = new Set();
        $(".input_room").each(function () {
            const val = $(this).val().trim();
            if (val !== "" && val !== "0") {
                assignedNos.add(val);
            }
        });

        // No → Name 辞書作成（.td_no の .input_no から取得）
        const noToName = {};
        $(".tr_house").each(function () {
            const no = $(this).find(".td_no .input_no").val().trim();
            const name = $(this).find(".td_name .input_name").val().trim();
            if (no) noToName[no] = name || "None";
        });

        const sortedNos = [...assignedNos].sort((a, b) => parseInt(a) - parseInt(b));

        // 列幅を計算（均等幅）
        const columnCount = sortedNos.length;
        const columnWidth = columnCount > 0 ? `${Math.floor(90 / columnCount)}%` : 'auto';

        sortedNos.forEach(no => {
            const name = noToName[no] || "None";
            const isNone = (name === "None");
            
            // 番号行：太字で左詰め、均等幅
            headerRowNo.append(`<th style="font-weight: bold; text-align: left; width: ${columnWidth};">${no}</th>`);
            
            // 名前行：Noneの場合はグレー・イタリック表示、均等幅
            if (isNone) {
                headerRowName.append(`<th style="color: #999; font-style: italic; width: ${columnWidth};">${name}</th>`);
            } else {
                headerRowName.append(`<th style="width: ${columnWidth};">${name}</th>`);
            }
            
            bathRow.append(bathAssignedNos.includes(no) ? "<td>〇</td>" : "<td></td>");
        });

        // テーブルのレイアウトを固定
        $(".fourth_line table").css("table-layout", "fixed");
    }
        //清掃指示表で担当部屋・エコ部屋を管理
        function updateAssignedRoomRows() {
            $(".room_cell_row").remove();

            // タイプコードにTを含む部屋を赤色表示用セットに格納
            const _roomsByType = window.rooms_by_type || {};
            const redRooms = new Set();
            for (const [code, list] of Object.entries(_roomsByType)) {
                if (code.includes('T')) {
                    list.forEach(r => redRooms.add(r));
                }
            }

            const assignedNos = new Set();
            $(".input_room").each(function () {
                const val = $(this).val().trim();
                if (val !== "" && val !== "0") assignedNos.add(val);
            });

            // 🔽 Noを昇順に並べ替え
            const nos = [...assignedNos].sort((a, b) => parseInt(a) - parseInt(b));

            const roomAssignments = [];
            $(".input_room").each(function () {
                const room = $(this).closest("td").data("room");
                const no = $(this).val().trim();
                if (room && no !== "" && no !== "0") {
                    roomAssignments.push({ room: String(room), no });
                }
            });

            const ecoRooms = new Set();
            const amenityRooms = new Set();

            $(".input_eco").each(function () {
                const val = $(this).val().trim();
                if (val !== "") ecoRooms.add(val);
            });

            $(".input_amenity").each(function () {
                const val = $(this).val().trim();
                if (val !== "") amenityRooms.add(val);
            });

            const roomMap = {};
            nos.forEach(no => roomMap[no] = { normal: [], eco: [] });

            roomAssignments.forEach(({ room, no }) => {
                if (!roomMap[no]) return;
                if (ecoRooms.has(room)) {
                    roomMap[no].eco.push({ room, type: 'eco' });
                } else if (amenityRooms.has(room)) {
                    roomMap[no].eco.push({ room, type: 'amenity' });
                } else {
                    roomMap[no].normal.push(room);
                }
            });

            Object.values(roomMap).forEach(roomLists => {
                roomLists.normal.sort((a, b) => parseInt(a) - parseInt(b));
                roomLists.eco.sort((a, b) => parseInt(a) - parseInt(b));
            });

            const $body = $("#result_table_body");

            // 通常部屋
            const maxNormal = Math.max(...Object.values(roomMap).map(r => r.normal.length), 0);
            if (maxNormal > 0) {
                const labelRow = $("<tr class='room_cell_row'></tr>").append("<td><strong>担当部屋</strong></td>");
                nos.forEach(no => {
                    const val = roomMap[no].normal[0] || "";
                    const redStyle = redRooms.has(val) ? 'style="color: red;"' : '';
                    labelRow.append(`<td ${redStyle}>${val}</td>`);

                });
                $body.append(labelRow);

                for (let i = 1; i < maxNormal; i++) {
                    const row = $("<tr class='room_cell_row'></tr>").append("<td></td>");
                    nos.forEach(no => {
                        const val = roomMap[no].normal[i] || "";
                        const redStyle = redRooms.has(val) ? 'style="color: red;"' : '';
                        row.append(`<td ${redStyle}>${val}</td>`);

                    });
                    $body.append(row);
                }
            }

            // エコ部屋
            const maxEco = Math.max(...Object.values(roomMap).map(r => r.eco.length), 0);
            if (maxEco > 0) {
                const labelRow = $("<tr class='room_cell_row'></tr>").append("<td><strong>エコ部屋</strong></td>");
                nos.forEach(no => {
                    const obj = roomMap[no].eco[0];
                    if (obj) {
                        const bgColor = obj.type === 'eco' ? 'yellow' : 'rgb(255, 203, 135)';
                        const redStyle = redRooms.has(obj.room) ? 'color: red;' : '';
                        labelRow.append(`<td style="background-color: ${bgColor}; ${redStyle}">${obj.room}</td>`);
                    } else {
                        labelRow.append("<td></td>");
                    }
                });
                $body.append(labelRow);

                for (let i = 1; i < maxEco; i++) {
                    const row = $("<tr class='room_cell_row'></tr>").append("<td></td>");
                    nos.forEach(no => {
                        const obj = roomMap[no].eco[i];
                        if (obj) {
                            const bgColor = obj.type === 'eco' ? 'yellow' : 'rgb(255, 203, 135)';
                            const redStyle = redRooms.has(obj.room) ? 'color: red;' : '';
                            row.append(`<td style="background-color: ${bgColor}; ${redStyle}">${obj.room}</td>`);
                        } else {
                            row.append("<td></td>");
                        }
                    });
                    $body.append(row);
                }
            }

        }

    //清掃指示表で終了予定時刻を管理
    function updateEndTimeRow() {
        $("#end_time_row").remove();

        // 動的にルームタイプSetと時間を構築
        const roomsByType = window.rooms_by_type || {};
        const roomTypeSets = {};
        for (const [code, list] of Object.entries(roomsByType)) {
            roomTypeSets[code] = new Set(list);
        }
        const typeTimes = {};
        $(".room_type_time").each(function () {
            typeTimes[$(this).data("type-code")] = parseInt($(this).val()) || 0;
        });

        const bathTime = parseInt($("#bath_time").val()) || 0;
        const ecoTime = 5;

        // レガシーhidden同期
        if (typeTimes["S"] !== undefined) { $("#single_time").val(typeTimes["S"]); }
        if (typeTimes["T"] !== undefined) { $("#twin_time").val(typeTimes["T"]); }

        const bathNos = [];
        $(".input_bath").each(function () {
            const val = $(this).val().trim();
            if (val !== "" && val !== "0") {
                bathNos.push(val);
            }
        });

        const assignments = [];
        $(".input_room").each(function () {
            const no = $(this).val().trim();
            const room = $(this).closest("td").data("room");
            if (no !== "" && no !== "0" && room) {
                assignments.push({ room: String(room), no });
            }
        });

        const ecoRooms = new Set();
        $(".input_eco").each(function () {
            const val = $(this).val().trim();
            if (val !== "") {
                ecoRooms.add(val);
            }
        });
        $(".input_amenity").each(function () {
            const val = $(this).val().trim();
            if (val !== "") {
                ecoRooms.add(val);
            }
        });

        const assignedNos = [...new Set(assignments.map(a => a.no))].sort((a, b) => parseInt(a) - parseInt(b));

        const $row = $("<tr id='end_time_row'><td><strong>終了予定</strong></td></tr>");
        assignedNos.forEach(no => {
            const assignedRooms = assignments.filter(a => a.no === no).map(a => a.room);
            let ecoCount = 0;
            const typeCounts = {};

            assignedRooms.forEach(room => {
                if (ecoRooms.has(room)) {
                    ecoCount++;
                } else {
                    let matched = false;
                    for (const [code, roomSet] of Object.entries(roomTypeSets)) {
                        if (roomSet.has(room)) {
                            typeCounts[code] = (typeCounts[code] || 0) + 1;
                            matched = true;
                            break;
                        }
                    }
                }
            });

            const hasBath = bathNos.includes(no);
            let totalMin = ecoCount * ecoTime + (hasBath ? bathTime : 0);
            for (const [code, count] of Object.entries(typeCounts)) {
                totalMin += count * (typeTimes[code] || 0);
            }

            const base = new Date();
            base.setHours(9);
            base.setMinutes(30 + totalMin);
            const hh = base.getHours().toString().padStart(2, "0");
            const mm = base.getMinutes().toString().padStart(2, "0");

            $row.append(`<td>${hh}:${mm}</td>`);
        });

        $("#bath_row").before($row);
    }


    //全体清掃部屋・清掃指示部屋数の管理
    function updateRoomStats() {
        let allCleanCountMinus = 0;
        let instructionCount = 0;
        let roomCount = 0

        $(".input_room").each(function () {
            const val = $(this).val().trim();
            roomCount++;
            // 0以外なら全体清掃にカウント
            if (val == "0") {
                allCleanCountMinus++;
            }

            // 空欄と0以外が入力されている場合、指示清掃にカウント
            if (val !== "" && val !== "0") {
                instructionCount++;
            }
        });
        allCleanCount = roomCount - allCleanCountMinus;
        $(".all_clean_rooms_num").text(allCleanCount);
        $(".instruction_rooms_num").text(instructionCount);

        const result = (allCleanCount === instructionCount) ? "OK" : "NG";
        $(".judge").text(result);
    }

    //ルームチェンジ表の行追加
    function checkAndAddRoomChangeRow() {
        let allRoomsFilled = true;
        let allRemarksFilled = true;

        $(".room_change_original").each(function () {
            if ($(this).val().trim() === "") {
                allRoomsFilled = false;
            }
        });

        $(".room_change_destination").each(function () {
            if ($(this).val().trim() === "") {
                allRemarksFilled = false;
            }
        });

        let lastRow = $(".room_change_original").last().val().trim() === "" &&
            $(".room_change_destination").last().val().trim() === "";

        if ((allRoomsFilled || allRemarksFilled) && !lastRow) {
            let rowCount = $(".room_change_original").length + 1;

            let newRow = `
                <tr>
                    <td>
                        <input type="text" name="room_change_original" id="room_change_original_${rowCount}" class="room_change_original">
                    </td>
                    <td>
                        <input type="text" name="room_change_destination" id="room_change_destination_${rowCount}" class="room_change_destination">
                    </td>
                </tr>
            `;

            $("#room_change_table_body").append(newRow);
        }
    }

    //アウト/イン表の行追加
    function checkAndAddOutInRow(currentElem) {
        let allRoomsFilled = true;

        $(".outin_room").each(function () {
            if ($(this).val().trim() === "") {
                allRoomsFilled = false;
            }
        });

        const $current = $(currentElem);
        const prevVal = $current.data('prev') || "";
        const currVal = $current.val().trim();

        // 全セルが埋まっており、かつこの要素が空→非空に変化した場合のみ追加
        if (allRoomsFilled && currVal !== "" && prevVal === "") {
            let rowCount = $(".outin_room").length + 1;

            let newRow = `
                <tr>
                    <td>
                        <input type="text" name="outin" id="outin_${rowCount}" class="outin_room">
                    </td>
                </tr>
            `;

            $("#outin_table_body").append(newRow);
        }

        // 次回判定のために現在値を保存
        $current.data('prev', currVal);
    }
    //連泊新規清掃表の行追加
    function checkAndAddMultipleNightCleanRow(currentElem) {
        let allRoomsFilled = true;

        $(".multiple_night_clean_room").each(function () {
            if ($(this).val().trim() === "") {
                allRoomsFilled = false;
            }
        });

        const $current = $(currentElem);
        const prevVal = $current.data('prev') || "";
        const currVal = $current.val().trim();

        // 全セルが埋まっており、かつこの要素が空→非空に変化した場合のみ追加
        if (allRoomsFilled && currVal !== "" && prevVal === "") {
            let rowCount = $(".multiple_night_clean_room").length + 1;

            let newRow = `
                <tr>
                    <td>
                        <input type="text" name="multiple_night_clean" id="multiple_night_clean_${rowCount}" class="multiple_night_clean_room">
                    </td>
                </tr>
            `;

            $("#multiple_night_clean_table_body").append(newRow);
        }

        // 次回判定のために現在値を保存
        $current.data('prev', currVal);
    }

    //連泊新規清掃の部屋番号をその他備考欄に反映
    function updateOthersWithMultipleNightCleans() {
        const roomNumbers = [];

        $(".multiple_night_clean_room").each(function () {
            const val = $(this).val().trim();
            if (val !== "") {
                roomNumbers.push(val);
            }
        });

        const $othersTextarea = $('textarea[name="others"]');
        const currentText = $othersTextarea.val();

        // 既存の連泊新規清掃に関する行を削除（#で始まり「新規清掃」で終わる行）
        const lines = currentText.split('\n');
        const filteredLines = lines.filter(line => {
            const trimmed = line.trim();
            return !(trimmed.startsWith('#') && trimmed.endsWith('新規清掃'));
        });

        // 新しい連泊新規清掃の行を生成
        const newCleanLines = roomNumbers.map(room => `#${room} 新規清掃`);

        // 既存のテキスト（連泊新規清掃以外）と新しい連泊新規清掃を結合
        const combinedLines = [...filteredLines, ...newCleanLines];

        // 空行を除去してから結合
        const finalText = combinedLines.filter(line => line.trim() !== '').join('\n');

        $othersTextarea.val(finalText);
    }

    //要清掃表の行追加
    function checkAndAddMustCleanRow() {
        let allRoomsFilled = true;
        let allRemarksFilled = true;

        $(".must_clean_room").each(function () {
            if ($(this).val().trim() === "") {
                allRoomsFilled = false;
            }
        });

        $(".must_clean_reason").each(function () {
            if ($(this).val().trim() === "") {
                allRemarksFilled = false;
            }
        });

        let lastRow = $(".must_clean_room").last().val().trim() === "" &&
            $(".must_clean_reason").last().val().trim() === "";

        if ((allRoomsFilled || allRemarksFilled) && !lastRow) {
            let rowCount = $(".must_clean_room").length + 1;

            let newRow = `
                <tr>
                    <td  class="must_clean_room">
                        <input type="text" name="must_clean_room" id="must_clean_room_${rowCount}" class="must_clean_room" >
                    </td>
                    <td>
                        <input type="text" name="must_clean_room_to" id="must_clean_room_to" class="must_clean_room">
                    </td>
                    <td>
                        <input type="text" name="must_clean_reason" id="must_clean_reason_${rowCount}" class="must_clean_reason">
                    </td>
                </tr>
            `;

            $("#must_clean_table_body").append(newRow);
        }
    }

    //連絡事項欄の処理
    function checkAndAddContactRow() {
        let allNumbersFilled = true;
        let allCommentsFilled = true;

        $(".input_contact_number").each(function () {
            if ($(this).val().trim() === "") {
                allNumbersFilled = false;
            }
        });

        $(".input_contact").each(function () {
            if ($(this).val().trim() === "") {
                allCommentsFilled = false;
            }
        });

        let lastNumberEmpty = $(".input_contact_number").last().val().trim() === "";
        let lastCommentEmpty = $(".input_contact").last().val().trim() === "";

        if ((allNumbersFilled || allCommentsFilled) && !(lastNumberEmpty && lastCommentEmpty)) {
            let rowCount = $(".input_contact").length + 1;

            let newRow = `
                <tr>
                    <td>
                        <input type="text" name="contact_number_${rowCount}" id="contact_number_${rowCount}" class="input_contact_number">
                    </td>
                    <td>
                        <textarea type="text" name="contact_${rowCount}" id="contact_${rowCount}" class="input_contact"></textarea>
                    </td>
                </tr>
            `;

            $("#contact_table_body").append(newRow);
        }
    }

    // --- 1) 各清掃者ごとにフロア毎の清掃数を集計 ---
    function buildFloorHouseT() {
        // houseNos はテーブル上の清掃者 No のリスト（1,2,…）
        const houseRows = $(".tr_house");
        const houseNos = houseRows.map((i, tr) => $(tr).find(".input_no").val().trim()).get();
        const numCleaners = houseNos.length;

        // floors 2〜10 のフロア数＝9
        const numFloors = 9;
        // floorHouseT[i][j] = 清掃者 j が (i+2)F で掃除した部屋数
        const floorHouseT = Array.from({ length: numFloors }, () => Array(numCleaners).fill(0));

        // room_assignments: room → houseNo
        const roomAssignments = {};
        $(".input_room").each(function () {
            const room = $(this).closest("td").data("room");
            const no = $(this).val().trim();
            if (room && no !== "" && no !== "0") roomAssignments[room] = no;
        });

        // 各 room を見て、floorHouseT に加算
        Object.entries(roomAssignments).forEach(([room, no]) => {
            const floor = Math.floor(parseInt(room, 10) / 100);
            if (floor >= 2 && floor <= 10) {
                const i = floor - 2;           // 2F→idx0 … 10F→idx8
                const j = houseNos.indexOf(no);
                if (j !== -1) floorHouseT[i][j] += 1;
            }
        });
        return floorHouseT;
    }

    // --- 2) Python ロジックを JS 化して担当フロアを決定 ---
    function assignDdByAlgorithm(floorHouseT) {
        const numFloors = floorHouseT.length;       // 9
        const numCleaners = floorHouseT[0].length;    // houseRows.length

        // 各フロアの「1 部屋以上清掃した人」一覧
        const floorCands = floorHouseT.map(row =>
            row.map((cnt, j) => cnt > 0 ? j : -1).filter(j => j >= 0)
        );

        // 割当対象フロアのみを「候補人数の少ない順」にソート
        const floorsOrder = [];
        floorCands.forEach((cands, i) => {
            if (cands.length > 0) floorsOrder.push(i);
        });
        floorsOrder.sort((a, b) =>
            floorCands[a].length - floorCands[b].length
        );

        // assignments[j] = 担当フロアリスト（数が 1 つか空）
        const assignments = Array.from({ length: numCleaners }, () => []);
        const used = new Set();  // 既に1フロア割当を受けた清掃者

        floorsOrder.forEach(i => {
            // 未割当の候補
            let avail = floorCands[i].filter(j => !used.has(j));
            if (avail.length === 0) {
                // いなければ全候補
                avail = floorCands[i].slice();
            }
            // 努力目標として「最多掃除者」を優先
            let best = avail[0];
            let maxCnt = floorHouseT[i][best];
            avail.forEach(j => {
                if (floorHouseT[i][j] > maxCnt) {
                    best = j; maxCnt = floorHouseT[i][j];
                }
            });
            assignments[best].push(i + 2);
            // 1 フロアめなら used に追加
            if (assignments[best].length === 1) used.add(best);
        });

        // None（担当なし）は空配列をそのままに
        return assignments.map(a => a.length ? a : null);
    }

    // --- 3) .dd_cell に反映する関数 ---
    function updateDdCells() {
        const floorHouseT = buildFloorHouseT();
        const ddAssigns = assignDdByAlgorithm(floorHouseT);
        // houseRows と対応して書き込む
        $(".tr_house").each((idx, tr) => {
            const $dd = $(tr).find(".dd_cell");
            const assigned = ddAssigns[idx];
            $dd.val(assigned ? assigned.join(",") : "");
        });
    }


    //階数の一括処理
    $("#delete_floor_btn").on("click", function () {
        const floorVal = $("#delete_floor").val().trim();
        if (floorVal === "") {
            alert("階数を入力してください。");
            return;
        }

        // 指定された階に属する部屋番号を検出（例：501, 502... 5xx）
        $('[data-room]').each(function () {
            const $cell = $(this);
            const roomNumber = $cell.data("room");
            if (roomNumber && String(roomNumber).startsWith(floorVal)) {
                $cell.find(".input_room").val("0"); // 清掃指示を空にする
            }
        });

        updateHouseCount();             // 数を再計算
        updateHouseFloorAssignments(); // 担当階を再更新
        updateMutedRooms();            // muted 表示再更新
        updateAssignedRoomRows();      // 表示テーブル更新
        updateRoomStats();
    });
});

document.addEventListener('DOMContentLoaded', function () {
    function highlightRedRooms() {
        // タイプコードにTを含む部屋を赤色表示
        const roomsByType = window.rooms_by_type || {};
        const redRooms = new Set();
        for (const [code, list] of Object.entries(roomsByType)) {
            if (code.includes('T')) {
                list.forEach(r => redRooms.add(r));
            }
        }
        $('[data-room]').each(function () {
            const $cell = $(this);
            const roomNumber = $cell.data("room").toString();
            if (redRooms.has(roomNumber)) {
                $cell.addClass("red-room");
            } else {
                $cell.removeClass("red-room");
            }
        });
    }
    highlightRedRooms();

    const form = document.getElementById('main_form');
    const nameInput = document.getElementById('name');

    form.addEventListener('submit', function (event) {
        // どのボタンで送信されたか取得
        const btn = event.submitter;
        const skipIds = ["sidewind_btn", "wincal_btn"];  

        // スキップ対象のボタンなら名字チェックを行わない
        if (btn && skipIds.includes(btn.id)) {
            return;  
        }

        if (nameInput.value.trim() === '') {
            event.preventDefault();  // フォーム送信を中止
            alert('編集者名字を入力してください');
        }

        // 名前の値を全て取得
        const names = $('.input_name').map(function () {
            return $(this).val().trim();
        }).get();

        // 重複チェック用セット
        const seen = new Set();
        const duplicates = names.filter(function (name) {
            if (name === '') return false;
            if (seen.has(name)) return true;
            seen.add(name);
            return false;
        });

        // 重複がある場合は警告
        if (duplicates.length > 0) {
            const message = `同じ名前が複数入力されています（例: ${duplicates[0]}）。\nこのまま続行しますか？`;
            const proceed = window.confirm(message);

            if (!proceed) {
                event.preventDefault(); // プレビュー動作を中止
                return false;
            }
        }
    });
});