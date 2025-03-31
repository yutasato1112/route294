$(document).ready(function () {
    function checkAndAddRow() {
        let allNameFilled = true;
        let allNoFilled = true;

        // 名前欄チェック
        $(".input_name").each(function () {
            if ($(this).val().trim() === "") {
                allNameFilled = false;
            }
        });

        // No欄チェック
        $(".input_no").each(function () {
            if ($(this).val().trim() === "") {
                allNoFilled = false;
            }
        });

        // すでに追加済みの行があると複数追加されるのを防ぐ
        let lastRow = $(".tr_house").last();
        let lastNo = lastRow.find(".input_no").val().trim();
        let lastName = lastRow.find(".input_name").val().trim();
        let lastEmpty = (lastNo === "" && lastName === "");

        // 名前またはNoが全部埋まっていて、最後の行が空なら追加
        if ((allNameFilled || allNoFilled) && !lastEmpty) {
            let rowCount = $(".tr_house").length + 1;

            // 9行目までは value を設定、10行目は空欄
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
                    <td><p>None</p></td>
                </tr>
            `;

            $("#house_table_body").append(newRow);
        }
    }

    // 入力イベント監視（Noまたは名前）
    $(document).on("input", ".input_no, .input_name", function () {
        checkAndAddRow();
    });
});

$(document).ready(function () {
    function checkAndAddCleanMethodRow() {
        let allEcoFilled = true;
        let allAmenityFilled = true;
        let allDuvetFilled = true;

        // エコ部屋（全input_ecoが空でない）
        $(".input_eco").each(function () {
            if ($(this).val().trim() === "") {
                allEcoFilled = false;
            }
        });

        // アメニティ
        $(".input_amenity").each(function () {
            if ($(this).val().trim() === "") {
                allAmenityFilled = false;
            }
        });

        // デュべ
        $(".input_duvet").each(function () {
            if ($(this).val().trim() === "") {
                allDuvetFilled = false;
            }
        });

        // 最後の行が空のままなら追加しない
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

    // 入力が発生したらチェック
    $(document).on("input", ".input_eco, .input_amenity, .input_duvet", function () {
        checkAndAddCleanMethodRow();
    });
});

$(document).ready(function () {
    function checkAndAddRemarkRow() {
        let allRoomsFilled = true;
        let allRemarksFilled = true;

        // 部屋番号チェック
        $(".input_remark_room").each(function () {
            if ($(this).val().trim() === "") {
                allRoomsFilled = false;
            }
        });

        // 備考欄チェック
        $(".input_remark").each(function () {
            if ($(this).val().trim() === "") {
                allRemarksFilled = false;
            }
        });

        // 最後の行が空なら追加しない
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

    // 入力があったらチェック
    $(document).on("input", ".input_remark_room, .input_remark", function () {
        checkAndAddRemarkRow();
    });
});

$(document).ready(function () {
    function highlightRooms() {
        // 一旦すべてリセット
        $('[data-room]').css('background-color', '');

        // まず eco の部屋番号をリストに入れて黄色に
        let ecoRooms = new Set();
        $('.input_eco').each(function () {
            let roomNumber = $(this).val().trim();
            if (roomNumber !== '') {
                ecoRooms.add(roomNumber);
                $('[data-room="' + roomNumber + '"]').css('background-color', 'yellow');
            }
        });

        // duvet の部屋番号で、ecoに含まれてない部屋だけ青に
        $('.input_duvet').each(function () {
            let roomNumber = $(this).val().trim();
            if (roomNumber !== '' && !ecoRooms.has(roomNumber)) {
                $('[data-room="' + roomNumber + '"]').css('background-color', 'lightblue');
            }
        });
    }

    // 入力イベントでチェック
    $(document).on('input', '.input_eco, .input_duvet', function () {
        highlightRooms();
    });

    // ページ読み込み時にも実行
    highlightRooms();
});

$(document).ready(function () {
    function updateHouseCount() {
        // 1. すべての input_room の値を収集
        let roomValues = [];
        $(".input_room").each(function () {
            const val = $(this).val().trim();
            if (val !== "") {
                roomValues.push(val);
            }
        });

        // 2. 各ハウスの No を取得して、roomValues に一致する数をカウント
        $(".tr_house").each(function () {
            const $row = $(this);
            const noVal = $row.find(".input_no").val().trim();
            let count = 0;

            if (noVal !== "") {
                count = roomValues.filter(room => room === noVal).length;
            }

            // 数欄に反映
            $row.find(".count_cell").text(count);
        });
    }

    // 入力が変更されたときにカウントを更新
    $(document).on("input", ".input_room, .input_no", function () {
        updateHouseCount();
    });

    // 初期化時に1回実行
    updateHouseCount();
});

$(document).ready(function () {
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

            // フォーム送信を防ぐ（ここが重要！）
            return false;
        }
    }

    // 入力完了後のチェック（changeイベント）
    $(document).on("change", ".input_no", function (e) {
        const result = checkDuplicateNo($(this));
        if (result === false) {
            e.preventDefault(); // ← これで送信を止める！
        }
    });
});

$(document).ready(function () {
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
    }

    // 入力イベント時に担当階更新
    $(document).on("input", ".input_room, .input_no", function () {
        updateHouseFloorAssignments();
    });

    // 初期表示時にも実行
    updateHouseFloorAssignments();
});

$(document).ready(function () {
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

    // 入力イベントでチェック
    $(document).on("input", ".input_room", function () {
        updateMutedRooms();
    });

    // 初期表示時にもチェック
    updateMutedRooms();
});
