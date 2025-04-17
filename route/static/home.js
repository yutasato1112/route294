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
    $(document).on("input", ".input_eco, .input_duvet", function () {
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

    $(document).on("input", ".input_name, .input_no, .input_bath, .input_room, .input_eco, #single_time, #twin_time, #bath_time", function () {
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
        checkAndAddOutInRow();
    });
    $(document).on("input", ".must_clean_room, .must_clean_reason", function () {
        checkAndAddMustCleanRow();
    });


    updateHouseCount();
    updateHouseFloorAssignments();
    updateMutedRooms();
    updateNoneStyling();
    highlightRooms();
    updateEndTimeRow();
    updateRoomStats();

    if (window.method === "POST") {
        updateResultTableColumns();
        updateAssignedRoomRows();
        updateEndTimeRow();
    }


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
                        <p class="floor_cell" id="floor_${rowCount}">None</p>
                    </td>
                    <td>
                        <input type="text" name="key_${rowCount}" id="key_${rowCount}" class="key_cell" value="None">
                    </td>
                </tr>
            `;

            $("#house_table_body").append(newRow);
        }
    }

    //マスターキーの更新
    function updateHouseKeys() {
        usedKeys = [];

        $(".tr_house").each(function () {
            const $row = $(this);
            const floorsText = $row.find(".floor_cell").text().trim();
            if (!floorsText || floorsText === "None") {
                $row.find(".key_cell").val("None");
                return;
            }

            const floors = floorsText.split(',');
            let assignedKeys = [];

            floors.forEach(floor => {
                const floorKeys = masterKeyList.filter(([f, k]) => f === floor && !usedKeys.includes(k));
                if (floorKeys.length > 0) {
                    assignedKeys.push(floorKeys[0][1]);
                    usedKeys.push(floorKeys[0][1]);
                } else {
                    assignedKeys.push(`${floor}N`);
                }
            });

            $row.find(".key_cell").val(assignedKeys.join(","));
        });
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
                $row.find(".floor_cell").text("None");
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
                $row.find(".floor_cell").text(floors.join(","));
            } else {
                $row.find(".floor_cell").text("None");
            }
        });

        updateHouseKeys();
    }

    //ハウスさん表でNone表示の時の処理
    function updateNoneStyling() {
        $(".count_cell, .floor_cell, .key_cell").each(function () {
            const isInput = $(this).is("input");
            const value = isInput ? $(this).val().trim() : $(this).text().trim();

            if (value === "None") {
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

        let ecoRooms = new Set();
        $('.input_eco').each(function () {
            let roomNumber = $(this).val().trim();
            if (roomNumber !== '') {
                ecoRooms.add(roomNumber);
                $('[data-room="' + roomNumber + '"]').css('background-color', 'yellow');
            }
        });

        $('.input_duvet').each(function () {
            let roomNumber = $(this).val().trim();
            if (roomNumber !== '' && !ecoRooms.has(roomNumber)) {
                $('[data-room="' + roomNumber + '"]').css('background-color', 'lightblue');
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

    //清掃指示表の氏名(列数)と大浴場清掃を管理
    function updateResultTableColumns() {
        const headerRow = $("#result_table_header");
        const bathRow = $("#bath_row");
    
        // 初期化
        headerRow.empty().append("<th></th>");
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
    
        // No → Name 辞書作成
        const noToName = {};
        $(".tr_house").each(function () {
            const no = $(this).find(".input_no").val().trim();
            const name = $(this).find(".input_name").val().trim();
            if (no) noToName[no] = name || "None";
        });
    
        const sortedNos = [...assignedNos].sort((a, b) => parseInt(a) - parseInt(b));
    
        sortedNos.forEach(no => {
            const name = noToName[no] || "None";
            headerRow.append(`<th>${name}</th>`);
            bathRow.append(bathAssignedNos.includes(no) ? "<td>〇</td>" : "<td></td>");
        });
    }
    

    //清掃指示表で担当部屋・エコ部屋を管理
    function updateAssignedRoomRows() {
        $(".room_cell_row").remove();
    
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
        $(".input_eco").each(function () {
            const val = $(this).val().trim();
            if (val !== "") ecoRooms.add(val);
        });
    
        const roomMap = {};
        nos.forEach(no => roomMap[no] = { normal: [], eco: [] });
    
        roomAssignments.forEach(({ room, no }) => {
            if (!roomMap[no]) return;
            if (ecoRooms.has(room)) {
                roomMap[no].eco.push(room);
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
                labelRow.append(`<td>${val}</td>`);
            });
            $body.append(labelRow);
    
            for (let i = 1; i < maxNormal; i++) {
                const row = $("<tr class='room_cell_row'></tr>").append("<td></td>");
                nos.forEach(no => {
                    const val = roomMap[no].normal[i] || "";
                    row.append(`<td>${val}</td>`);
                });
                $body.append(row);
            }
        }
    
        // エコ部屋
        const maxEco = Math.max(...Object.values(roomMap).map(r => r.eco.length), 0);
        if (maxEco > 0) {
            const labelRow = $("<tr class='room_cell_row'></tr>").append("<td><strong>エコ部屋</strong></td>");
            nos.forEach(no => {
                const val = roomMap[no].eco[0] || "";
                labelRow.append(val ? `<td style="background-color: yellow;">${val}</td>` : "<td></td>");
            });
            $body.append(labelRow);
    
            for (let i = 1; i < maxEco; i++) {
                const row = $("<tr class='room_cell_row'></tr>").append("<td></td>");
                nos.forEach(no => {
                    const val = roomMap[no].eco[i] || "";
                    row.append(val ? `<td style="background-color: yellow;">${val}</td>` : "<td></td>");
                });
                $body.append(row);
            }
        }
    }
    
    //清掃指示表で終了予定時刻を管理
    //清掃指示表で終了予定時刻を管理
    function updateEndTimeRow() {
        $("#end_time_row").remove();

        const singleRooms = new Set(window.single_rooms || []);
        const twinRooms = new Set(window.twin_rooms || []);
        const singleTime = parseInt($("#single_time").val()) || 0;
        const twinTime = parseInt($("#twin_time").val()) || 0;
        const bathTime = parseInt($("#bath_time").val()) || 0;
        const ecoTime = 5;

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

        const assignedNos = [...new Set(assignments.map(a => a.no))].sort((a, b) => parseInt(a) - parseInt(b));

        const $row = $("<tr id='end_time_row'><td><strong>終了予定</strong></td></tr>");
        assignedNos.forEach(no => {
            const assignedRooms = assignments.filter(a => a.no === no).map(a => a.room);
            let singleCount = 0, twinCount = 0, ecoCount = 0;

            assignedRooms.forEach(room => {
                if (ecoRooms.has(room)) {
                    ecoCount++;
                } else if (singleRooms.has(room)) {
                    singleCount++;
                } else if (twinRooms.has(room)) {
                    twinCount++;
                }
            });

            const hasBath = bathNos.includes(no);
            const totalMin = (singleCount * singleTime) + (twinCount * twinTime) + (ecoCount * ecoTime) + (hasBath ? bathTime : 0);

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
    function checkAndAddOutInRow() {
        let allRoomsFilled = true;

        $(".outin_room").each(function () {
            if ($(this).val().trim() === "") {
                allRoomsFilled = false;
            }
        });

        let lastRow = $(".outin_room").last().val().trim() === "";

        if ((allRoomsFilled) && !lastRow) {
            let rowCount = $(".outin_room").length + 1;

            let newRow = `
                <tr>
                    <td>
                        <input type="text" name="outin" id="outin class="outin_room">
                    </td>
                </tr>
            `;

            $("#outin_table_body").append(newRow);
        }
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
                        <input type="text" name="must_clean_reason" id="must_clean_reason_${rowCount}" class="must_clean_reason">
                    </td>
                </tr>
            `;

            $("#must_clean_table_body").append(newRow);
        }
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
