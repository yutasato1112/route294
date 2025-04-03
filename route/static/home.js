$(document).ready(function () {
    let masterKeyList = window.master_key || [];
    let usedKeys = [];

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
                    <td><p class="count_cell">0</p></td>
                    <td><p class="floor_cell">None</p></td>
                    <td><input type="text" class="key_cell" value="None"></td>
                </tr>
            `;

            $("#house_table_body").append(newRow);
        }
    }

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

    function updateResultTableColumns() {
        const headerRow = $("#result_table_header");
        headerRow.empty(); // 一度リセット
    
        const names = [];
    
        $(".input_name").each(function () {
            const name = $(this).val().trim();
            if (name && !names.includes(name)) {
                names.push(name);
            }
        });
    
        names.forEach(name => {
            headerRow.append(`<th>${name}</th>`);
        });
    }
    function updateResultTableColumns() {
        const headerRow = $("#result_table_header");
        const bathRow = $("#bath_row");
    
        // 初期化
        headerRow.empty().append("<th></th>");
        bathRow.empty().append("<td><strong>大浴場清掃</strong></td>");
    
        const nameNoPairs = [];
    
        $(".tr_house").each(function () {
            const name = $(this).find(".input_name").val().trim();
            const no = $(this).find(".input_no").val().trim();
            if (name && no) {
                nameNoPairs.push({ name, no });
            }
        });
    
        const bathAssignedNos = [];
        $(".input_bath").each(function () {
            const val = $(this).val().trim();
            if (val !== "") {
                bathAssignedNos.push(val);
            }
        });
    
        nameNoPairs.forEach(pair => {
            headerRow.append(`<th>${pair.name}</th>`);
            if (bathAssignedNos.includes(pair.no)) {
                bathRow.append("<td>〇</td>");
            } else {
                bathRow.append("<td></td>");
            }
        });
    }
    
    function updateAssignedRoomRows() {
        $(".room_cell_row").remove();
    
        //番号と名前のペアを取得
        const nameNoPairs = [];
        $(".tr_house").each(function () {
            const name = $(this).find(".input_name").val().trim();
            const no = $(this).find(".input_no").val().trim();
            if (name && no) {
                nameNoPairs.push({ name, no });
            }
        });
    
        // 部屋の割り当てを取得
        const roomAssignments = [];
        $(".input_room").each(function () {
            const val = $(this).val().trim();
            if (val !== "") {
                const room = $(this).closest("td").data("room");
                roomAssignments.push({ room, no: val });
            }
        });
    
        // エコ部屋のリストを取得
        const ecoRooms = new Set();
        $(".input_eco").each(function () {
            const eco = $(this).val().trim();
            if (eco !== "") ecoRooms.add(eco);
        });
        
        // マッピング初期化
        const roomMap = {};
        nameNoPairs.forEach(({ no }) => {
            roomMap[no] = { normal: [], eco: [] };
        });

        // 部屋の分類
        roomAssignments.forEach(({ room, no }) => {
            const cleanRoom = String(room).trim();
            if (!roomMap[no]) return;

            if (ecoRooms.has(cleanRoom)) {
                roomMap[no].eco.push(cleanRoom);  // ✅ エコ部屋
            } else {
                roomMap[no].normal.push(cleanRoom);  // ✅ 通常部屋
            }
        });
    
        const $body = $("#result_table_body");
    
        // 通常部屋の最大行数
        const maxNormal = Math.max(...Object.values(roomMap).map(r => r.normal.length), 0);
        if (maxNormal > 0) {
            const normalLabelRow = $("<tr class='room_cell_row'></tr>").append("<td><strong>担当部屋</strong></td>");
            nameNoPairs.forEach(({ no }) => {
                const val = roomMap[no].normal[0] || "";
                normalLabelRow.append(`<td>${val}</td>`);
            });
            $body.append(normalLabelRow);
    
            for (let i = 1; i < maxNormal; i++) {
                const row = $("<tr class='room_cell_row'></tr>").append("<td></td>");
                nameNoPairs.forEach(({ no }) => {
                    const val = roomMap[no].normal[i] || "";
                    row.append(`<td>${val}</td>`);
                });
                $body.append(row);
            }
        }
    
        // エコ部屋の最大行数
        const maxEco = Math.max(...Object.values(roomMap).map(r => r.eco.length), 0);
        if (maxEco > 0) {
            const ecoLabelRow = $("<tr class='room_cell_row'></tr>").append("<td><strong>エコ部屋</strong></td>");
            nameNoPairs.forEach(({ no }) => {
                const val = roomMap[no].eco[0] || "";  // ← ここでデータを含める
                const cell = val ? `<td style="background-color: yellow;">${val}</td>` : "<td></td>";
                ecoLabelRow.append(cell);
            });
            $body.append(ecoLabelRow);
        
            for (let i = 1; i < maxEco; i++) {
                const row = $("<tr class='room_cell_row'></tr>").append("<td></td>");
                nameNoPairs.forEach(({ no }) => {
                    const val = roomMap[no].eco[i] || "";
                    const cell = val ? `<td style="background-color: yellow;">${val}</td>` : "<td></td>";
                    row.append(cell);
                });
                $body.append(row);
            }
        }        
    }
    
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
                $cell.find(".input_room").val(""); // 清掃指示を空にする
            }
        });

        updateHouseCount();             // 数を再計算
        updateHouseFloorAssignments(); // 担当階を再更新
        updateMutedRooms();            // muted 表示再更新
        updateAssignedRoomRows();      // 表示テーブル更新
    });
    

    $(document).on("input", ".input_no, .input_name", function () {
        checkAndAddRow();
        updateHouseCount();
        updateHouseFloorAssignments();
        updateNoneStyling();
    });

    $(document).on("input", ".input_room", function () {
        updateHouseCount();
        updateHouseFloorAssignments();
        updateMutedRooms();
        updateNoneStyling();
    });

    $(document).on("change", ".input_no", function (e) {
        const result = checkDuplicateNo($(this));
        if (result === false) {
            e.preventDefault();
        }
    });

    $(document).on("input", ".input_eco, .input_duvet", function () {
        highlightRooms();
    });

    $(document).on("input", ".input_eco, .input_amenity, .input_duvet", function () {
        checkAndAddCleanMethodRow();
    });

    $(document).on("input", ".input_remark_room, .input_remark", function () {
        checkAndAddRemarkRow();
    });

    $(document).on("input", ".input_name", function () {
        checkAndAddRow(); // 既存
        updateHouseCount(); // 既存
        updateHouseFloorAssignments(); // 既存
        updateNoneStyling(); // 既存
        updateResultTableColumns(); // ← 追加
    });
    $(document).on("input", ".input_name, .input_no, .input_bath", function () {
        updateResultTableColumns();
    });
    $(document).on("input", ".input_name, .input_no, .input_bath, .input_room, .input_eco", function () {
        updateResultTableColumns();
        updateAssignedRoomRows();
    });    
    
    
    

    updateHouseCount();
    updateHouseFloorAssignments();
    updateMutedRooms();
    updateNoneStyling();
    highlightRooms();
});
