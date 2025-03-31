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

            let newRow = `
                <tr class="tr_house">
                    <td class="td_no">
                        <input type="number" name="no_${rowCount}" id="no_${rowCount}" class="input_no">
                    </td>
                    <td class="td_name">
                        <input type="text" name="name_${rowCount}" id="name_${rowCount}" class="input_name">
                    </td>
                    <td><p>0</p></td>
                    <td><p>0</p></td>
                    <td><p>2A</p></td>
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
