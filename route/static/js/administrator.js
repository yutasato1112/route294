/**
 * 管理画面 - JavaScript
 *
 * 機能:
 * - Ajax通信（CSRF対応）
 * - トースト通知システム
 * - ローディング表示
 * - CSVエディタ
 * - ログビューア
 * - 設定管理
 * - 削除確認ダイアログ
 */

$(document).ready(function() {
    // CSRF トークン設定
    const csrftoken = $('[name=csrfmiddlewaretoken]').val();
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    });
});

// ========================================
// ユーティリティ関数
// ========================================

/**
 * HTML文字列をエスケープ（XSS対策）
 * @param {string} text - エスケープする文字列
 * @returns {string} エスケープ済み文字列
 */
function escapeHtml(text) {
    if (text === null || text === undefined) {
        return '';
    }
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// ========================================
// トースト通知システム
// ========================================

/**
 * トースト通知を表示
 * @param {string} type - 通知タイプ (success, danger, warning, info)
 * @param {string} message - 表示メッセージ
 * @param {number} duration - 表示時間（ミリ秒、デフォルト: 3000）
 */
function showToast(type, message, duration = 3000) {
    // デバッグ: 空メッセージや不正な呼び出しを防ぐ
    if (!message || message.trim() === '') {
        console.warn('showToast called with empty message');
        return;
    }

    // デバッグ: 呼び出し元を追跡
    console.log('showToast called:', { type, message, duration });
    console.trace('Call stack:');

    const toast = document.getElementById('notification-toast');
    const toastBody = document.getElementById('toast-body');
    const toastTitle = document.getElementById('toast-title');
    const toastHeader = toast.querySelector('.toast-header');

    // タイプ別設定
    const config = {
        success: { title: '成功', bg: 'bg-success text-white' },
        danger: { title: 'エラー', bg: 'bg-danger text-white' },
        warning: { title: '警告', bg: 'bg-warning' },
        info: { title: '情報', bg: 'bg-info text-white' }
    };

    const settings = config[type] || config.info;

    // スタイル適用
    toastHeader.className = `toast-header ${settings.bg}`;
    toastTitle.textContent = settings.title;
    toastBody.textContent = message;

    // 表示
    const bsToast = new bootstrap.Toast(toast, { delay: duration, autohide: true });
    bsToast.show();
}

// ========================================
// ローディング表示
// ========================================

/**
 * ローディングオーバーレイを表示
 */
function showLoading() {
    $('#loading-overlay').fadeIn(200);
}

/**
 * ローディングオーバーレイを非表示
 */
function hideLoading() {
    $('#loading-overlay').fadeOut(200);
}

// ========================================
// 削除確認ダイアログ
// ========================================

let deleteAction = null;
let deleteData = null;

/**
 * 削除確認ダイアログを表示
 * @param {string} type - 削除対象のタイプ（マスタデータ、ログ等）
 * @param {string|null} name - 削除対象の名前（nullの場合は全体削除）
 * @param {string} action - 実行するアクション名
 * @param {object} data - 送信するデータ
 */
function showDeleteConfirm(type, name, action, data) {
    const message = name
        ? `${type}「${name}」を削除しますか？`
        : `${type}を削除しますか？`;

    $('#delete-confirm-message').text(message);
    $('#confirmDeleteModal').modal('show');

    // 確認ボタンのイベント設定
    deleteAction = action;
    deleteData = data;
}

/**
 * 削除を実行
 */
function executeDelete() {
    if (!deleteAction) return;

    showLoading();

    $.ajax({
        url: '',
        method: 'POST',
        data: {
            action: deleteAction,
            csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val(),
            ...deleteData
        },
        success: function(response) {
            hideLoading();
            $('#confirmDeleteModal').modal('hide');

            if (response.success !== false) {
                showToast('success', response.message || '削除しました', 3000);
                setTimeout(() => location.reload(), 3500);
            } else {
                showToast('danger', response.message || '削除に失敗しました');
            }
        },
        error: function(xhr) {
            hideLoading();
            const message = xhr.responseJSON?.message || '削除に失敗しました';
            showToast('danger', message);
        }
    });
}

// 削除確認ボタンのイベント設定
$(document).ready(function() {
    $('#confirm-delete-btn').on('click', executeDelete);

    // モーダルクリーンアップ（バックドロップが残らないようにする）
    $('#confirmDeleteModal, #csvEditorModal').on('hidden.bs.modal', function() {
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open').css('overflow', '');
    });
});

// ========================================
// マスタデータ削除
// ========================================

$(document).ready(function() {
    $(document).on('click', '.delete-master-btn', function(e) {
        e.preventDefault();
        const filename = $(this).data('filename');
        showDeleteConfirm('マスタデータ', filename, 'delete_master', { master_id: filename });
    });
});

// ========================================
// ログ削除
// ========================================

$(document).ready(function() {
    $('#delete-logs-btn').on('click', function(e) {
        e.preventDefault();
        showDeleteConfirm('すべてのログ', null, 'delete_logs', {});
    });
});

// ========================================
// プレビュー折りたたみ
// ========================================

$(document).ready(function() {
    $('.preview-toggle').on('click', function() {
        const icon = $(this).hasClass('collapsed') ? '▼' : '▶';
        const text = 'プレビュー';
        $(this).html(`${icon} ${text}`);
    });
});

// ========================================
// CSVエディタ
// ========================================

let currentFilename = null;
let validateTimeout = null;

/**
 * CSVエディタモーダルを開く
 * @param {string} filename - 編集するCSVファイル名
 */
function openCSVEditor(filename) {
    currentFilename = filename;

    showLoading();

    $.ajax({
        url: '/administrator/get-csv/',
        method: 'GET',
        data: { filename },
        success: function(response) {
            hideLoading();
            loadCSVIntoEditor(filename, response.data);
            $('#csvEditorModal').modal('show');
        },
        error: function(xhr) {
            hideLoading();
            const message = xhr.responseJSON?.error || 'CSVファイルの読み込みに失敗しました';
            showToast('danger', message);
        }
    });
}

/**
 * CSVデータをエディタに読み込む
 * @param {string} filename - ファイル名
 * @param {Array<Array<string>>} rows - CSVデータ（2次元配列）
 */
function loadCSVIntoEditor(filename, rows) {
    $('#edit-filename').text(filename);

    if (rows.length === 0) {
        rows = [['列1', '列2', '列3']]; // デフォルトヘッダー
    }

    const header = rows[0];
    const body = rows.slice(1);

    // ヘッダー生成
    let headerHtml = '<tr>';
    header.forEach((col, index) => {
        headerHtml += `
            <th>
                <input type="text" class="form-control form-control-sm header-cell"
                       value="${escapeHtml(col)}" data-col="${index}">
            </th>
        `;
    });
    headerHtml += '<th style="width: 50px;"></th></tr>';
    $('#csv-header').html(headerHtml);

    // ボディ生成
    renderCSVBody(body, header.length);

    // テキストエディタにも反映
    updateTextEditor(rows);

    // バリデーション実行
    const result = validateCSVData(rows);
    showValidationResult(result);
}

/**
 * CSVボディテーブルを生成
 * @param {Array<Array<string>>} rows - データ行
 * @param {number} colCount - 列数
 */
function renderCSVBody(rows, colCount) {
    let bodyHtml = '';

    rows.forEach((row, rowIndex) => {
        bodyHtml += '<tr data-row="' + rowIndex + '">';

        for (let i = 0; i < colCount; i++) {
            const value = row[i] || '';
            bodyHtml += `
                <td>
                    <input type="text" class="form-control form-control-sm data-cell"
                           value="${escapeHtml(value)}"
                           data-row="${rowIndex}" data-col="${i}">
                </td>
            `;
        }

        bodyHtml += `
            <td>
                <button type="button" class="btn btn-sm btn-outline-danger delete-row"
                        data-row="${rowIndex}">×</button>
            </td>
        `;
        bodyHtml += '</tr>';
    });

    $('#csv-body').html(bodyHtml);
}

/**
 * テーブルデータを配列に変換
 * @returns {Array<Array<string>>} CSVデータ（2次元配列）
 */
function collectTableData() {
    const rows = [];

    // ヘッダー
    const header = [];
    $('#csv-header .header-cell').each(function() {
        header.push($(this).val());
    });
    rows.push(header);

    // データ行
    $('#csv-body tr').each(function() {
        const row = [];
        $(this).find('.data-cell').each(function() {
            row.push($(this).val());
        });
        rows.push(row);
    });

    return rows;
}

/**
 * テキストエディタを更新
 * @param {Array<Array<string>>} rows - CSVデータ
 */
function updateTextEditor(rows) {
    const csvText = rows.map(row => row.join(',')).join('\n');
    $('#csv-text').val(csvText);
}

/**
 * CSVデータをバリデーション
 * @param {Array<Array<string>>} rows - CSVデータ
 * @returns {Object} バリデーション結果 {valid: boolean, errors: Array<string>}
 */
function validateCSVData(rows) {
    const errors = [];

    if (rows.length === 0) {
        errors.push('データが空です');
        return { valid: false, errors };
    }

    const colCount = rows[0].length;

    // 列数の一貫性チェック
    rows.forEach((row, index) => {
        if (row.length !== colCount) {
            errors.push(`行${index + 1}: 列数が不正（期待: ${colCount}, 実際: ${row.length}）`);
        }
    });

    // ファイル別バリデーション（特定のファイルのみ）
    if (currentFilename === 'room_info.csv') {
        validateRoomInfo(rows, errors);
    } else if (currentFilename === 'times_by_type.csv') {
        validateTimesByType(rows, errors);
    } else if (currentFilename === 'master_key.csv') {
        validateMasterKey(rows, errors);
    }
    // weekly.csvや他のファイルは列数チェックのみ

    return {
        valid: errors.length === 0,
        errors
    };
}

/**
 * room_info.csvのバリデーション
 */
function validateRoomInfo(rows, errors) {
    // データ型チェックのみ（ヘッダーチェックは不要）
    rows.slice(1).forEach((row, index) => {
        const roomNumber = row[0];
        const type = row[1];
        const floor = row[2];

        if (roomNumber && !/^\d{3,4}$/.test(roomNumber)) {
            errors.push(`行${index + 2}: 1列目（部屋番号）が不正（${roomNumber}）`);
        }

        if (type && !['S', 'T'].includes(type)) {
            errors.push(`行${index + 2}: 2列目（部屋タイプ）は S または T である必要があります`);
        }

        if (floor && !/^\d+$/.test(floor)) {
            errors.push(`行${index + 2}: 3列目（階数）は数字である必要があります`);
        }
    });
}

/**
 * times_by_type.csvのバリデーション
 */
function validateTimesByType(rows, errors) {
    // データ型チェックのみ（ヘッダーチェックは不要）
    rows.slice(1).forEach((row, index) => {
        const minutes = row[1];

        if (minutes && !/^\d+$/.test(minutes)) {
            errors.push(`行${index + 2}: 2列目（分数）は数字である必要があります`);
        }
    });
}

/**
 * master_key.csvのバリデーション
 */
function validateMasterKey(rows, errors) {
    // データ型チェックのみ（ヘッダーチェックは不要）
    rows.slice(1).forEach((row, index) => {
        const floor = row[0];

        if (floor && !/^\d+$/.test(floor)) {
            errors.push(`行${index + 2}: 1列目（階数）は数字である必要があります`);
        }
    });
}

/**
 * バリデーション結果を表示
 * @param {Object} result - バリデーション結果
 */
function showValidationResult(result) {
    const container = $('#validation-result');

    if (result.valid) {
        container.html(`
            <div class="alert alert-success">
                <strong>✓ 検証OK:</strong> データは正常です
            </div>
        `);
    } else {
        let html = '<div class="alert alert-danger"><strong>✗ 検証エラー:</strong><ul class="mb-0 mt-2">';
        result.errors.forEach(error => {
            html += `<li>${error}</li>`;
        });
        html += '</ul></div>';
        container.html(html);
    }
}

// ========================================
// CSVエディタ - イベントハンドラ
// ========================================

$(document).ready(function() {
    // 新規作成ボタンクリック
    $('#create-csv-btn').on('click', function() {
        $('#csvCreateModal').modal('show');
    });

    // 新規作成フォーム送信
    $('#csvCreateModal form').on('submit', function(e) {
        e.preventDefault();

        const formData = {
            action: 'create_master',
            name: $(this).find('input[name="name"]').val(),
            body: $(this).find('textarea[name="body"]').val(),
            csrfmiddlewaretoken: $(this).find('[name=csrfmiddlewaretoken]').val()
        };

        showLoading();

        $.ajax({
            url: '',
            method: 'POST',
            data: formData,
            success: function(response) {
                hideLoading();
                $('#csvCreateModal').modal('hide');

                if (response.success !== false) {
                    showToast('success', response.message || 'CSV作成しました', 3000);
                    setTimeout(() => location.reload(), 3500);
                } else {
                    showToast('danger', response.message || 'CSV作成に失敗しました');
                }
            },
            error: function(xhr) {
                hideLoading();
                const message = xhr.responseJSON?.message || 'CSV作成に失敗しました';
                showToast('danger', message);
            }
        });
    });

    // 新規作成モーダルを閉じた時にフォームをクリア
    $('#csvCreateModal').on('hidden.bs.modal', function() {
        $(this).find('form')[0].reset();
        // バックドロップを確実に削除
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open').css('overflow', '');
    });

    // 編集ボタンクリック
    $(document).on('click', '.edit-master-btn', function(e) {
        e.preventDefault();
        const filename = $(this).data('filename');
        openCSVEditor(filename);
    });

    // 行追加
    $('#add-row').on('click', function() {
        const colCount = $('#csv-header th').length - 1;
        const rowIndex = $('#csv-body tr').length;

        let rowHtml = '<tr data-row="' + rowIndex + '">';
        for (let i = 0; i < colCount; i++) {
            rowHtml += `
                <td>
                    <input type="text" class="form-control form-control-sm data-cell"
                           value="" data-row="${rowIndex}" data-col="${i}">
                </td>
            `;
        }
        rowHtml += `
            <td>
                <button type="button" class="btn btn-sm btn-outline-danger delete-row"
                        data-row="${rowIndex}">×</button>
            </td>
        `;
        rowHtml += '</tr>';

        $('#csv-body').append(rowHtml);

        // バリデーション更新
        const rows = collectTableData();
        const result = validateCSVData(rows);
        showValidationResult(result);
    });

    // 行削除
    $(document).on('click', '.delete-row', function() {
        $(this).closest('tr').remove();

        // 行番号振り直し
        $('#csv-body tr').each(function(index) {
            $(this).attr('data-row', index);
            $(this).find('.data-cell').attr('data-row', index);
            $(this).find('.delete-row').attr('data-row', index);
        });

        // バリデーション更新
        const rows = collectTableData();
        const result = validateCSVData(rows);
        showValidationResult(result);
        updateTextEditor(rows);
    });

    // セル変更時のリアルタイムバリデーション
    $(document).on('input', '.header-cell, .data-cell', function() {
        clearTimeout(validateTimeout);
        validateTimeout = setTimeout(() => {
            const rows = collectTableData();
            const result = validateCSVData(rows);
            showValidationResult(result);
            updateTextEditor(rows);
        }, 500);
    });

    // テキストエディタタブ表示時
    $('#text-editor-tab').on('shown.bs.tab', function() {
        const rows = collectTableData();
        updateTextEditor(rows);
    });

    // テーブルエディタタブ表示時
    $('#table-editor-tab').on('shown.bs.tab', function() {
        try {
            const text = $('#csv-text').val();
            const rows = text.split('\n').map(line =>
                line.split(',').map(cell => cell.trim())
            );

            if (rows.length > 0) {
                loadCSVIntoEditor(currentFilename, rows);
            }
        } catch (e) {
            showToast('danger', 'CSV形式が不正です');
        }
    });

    // 保存ボタンクリック
    $('#save-csv').on('click', function() {
        const rows = collectTableData();

        // バリデーション
        const result = validateCSVData(rows);
        if (!result.valid) {
            showToast('danger', 'データが不正です。エラーを修正してください');
            return;
        }

        // CSV文字列生成
        const csvText = rows.map(row => row.join(',')).join('\n');

        // 保存
        showLoading();

        $.ajax({
            url: '',
            method: 'POST',
            data: {
                action: 'update_master',
                master_id: currentFilename,
                name: currentFilename,
                body: csvText,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                hideLoading();
                $('#csvEditorModal').modal('hide');

                if (response.success !== false) {
                    showToast('success', '保存しました', 3000);
                    setTimeout(() => location.reload(), 3500);
                } else {
                    showToast('danger', response.message || '保存に失敗しました');
                }
            },
            error: function(xhr) {
                hideLoading();
                const message = xhr.responseJSON?.message || '保存に失敗しました';
                showToast('danger', message);
            }
        });
    });
});

// ========================================
// ログビューア
// ========================================

/**
 * LogViewerクラス - ログのページネーション・フィルタリング
 */
class LogViewer {
    constructor(initialLogs) {
        this.allLogs = initialLogs || [];
        this.filteredLogs = this.allLogs;
        this.currentPage = 1;
        this.pageSize = 10;
        this.levelFilter = 'ERROR';
        this.searchQuery = '';

        this.init();
    }

    init() {
        // イベントリスナー設定
        $('#page-size').on('change', (e) => {
            this.pageSize = parseInt(e.target.value);
            this.currentPage = 1;
            this.render();
        });

        $('#log-search').on('input', (e) => {
            this.searchQuery = e.target.value;
            this.filter();
        });

        $('#clear-search').on('click', () => {
            $('#log-search').val('');
            this.searchQuery = '';
            this.filter();
        });

        $('.log-filter').on('click', (e) => {
            $('.log-filter').removeClass('active');
            $(e.target).addClass('active');
            this.levelFilter = $(e.target).data('level');
            this.filter();
        });

        $(document).on('click', '.page-link', (e) => {
            e.preventDefault();
            const page = $(e.target).data('page');
            if (page && page > 0) {
                this.currentPage = page;
                this.render();
            }
        });

        // 初回レンダリング
        this.filter();
    }

    filter() {
        this.filteredLogs = this.allLogs.filter(log => {
            // レベルフィルタ
            if (this.levelFilter !== 'ALL' && log.level !== this.levelFilter) {
                return false;
            }

            // 検索クエリ
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                const searchText = `${log.timestamp} ${log.level} ${log.message}`.toLowerCase();
                if (!searchText.includes(query)) {
                    return false;
                }
            }

            return true;
        });

        this.currentPage = 1;
        this.render();
    }

    render() {
        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const pageData = this.filteredLogs.slice(start, end);

        // テーブル更新
        this.renderTable(pageData);

        // ページネーション更新
        this.renderPagination();

        // 統計更新
        this.renderStats();
    }

    renderTable(logs) {
        const tbody = $('#log-table-body');
        tbody.empty();

        if (logs.length === 0) {
            tbody.append(`
                <tr>
                    <td colspan="4" class="text-center text-muted">該当するログがありません</td>
                </tr>
            `);
            return;
        }

        logs.forEach(log => {
            const levelClass = this.getLevelBadgeClass(log.level);
            tbody.append(`
                <tr>
                    <td class="text-nowrap">${escapeHtml(log.timestamp)}</td>
                    <td><span class="badge ${levelClass}">${escapeHtml(log.level)}</span></td>
                    <td class="text-muted small">${escapeHtml(log.file || '')}</td>
                    <td>${escapeHtml(log.message)}</td>
                </tr>
            `);
        });
    }

    renderPagination() {
        const totalPages = Math.ceil(this.filteredLogs.length / this.pageSize);

        if (totalPages <= 1) {
            $('#log-pagination').empty();
            return;
        }

        let html = '<nav><ul class="pagination pagination-sm justify-content-center">';

        // 前へ
        const prevDisabled = this.currentPage === 1 ? 'disabled' : '';
        html += `
            <li class="page-item ${prevDisabled}">
                <a class="page-link" href="#" data-page="${this.currentPage - 1}">‹</a>
            </li>
        `;

        // ページ番号
        const maxVisible = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
        let endPage = Math.min(totalPages, startPage + maxVisible - 1);

        if (endPage - startPage < maxVisible - 1) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }

        if (startPage > 1) {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
            if (startPage > 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            const active = i === this.currentPage ? 'active' : '';
            html += `
                <li class="page-item ${active}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a></li>`;
        }

        // 次へ
        const nextDisabled = this.currentPage === totalPages ? 'disabled' : '';
        html += `
            <li class="page-item ${nextDisabled}">
                <a class="page-link" href="#" data-page="${this.currentPage + 1}">›</a>
            </li>
        `;

        html += '</ul></nav>';
        $('#log-pagination').html(html);
    }

    renderStats() {
        if (this.filteredLogs.length === 0) {
            $('#log-stats').text('0件');
            return;
        }

        const start = (this.currentPage - 1) * this.pageSize + 1;
        const end = Math.min(start + this.pageSize - 1, this.filteredLogs.length);
        const total = this.filteredLogs.length;

        $('#log-stats').text(`${start}-${end} / ${total}件`);
    }

    getLevelBadgeClass(level) {
        const classes = {
            'ERROR': 'bg-danger',
            'WARNING': 'bg-warning text-dark',
            'INFO': 'bg-info text-dark',
            'DEBUG': 'bg-secondary'
        };
        return classes[level] || 'bg-light text-dark';
    }
}

// ログビューアの初期化
let logViewer;
$(document).ready(function() {
    if (window.logsData) {
        logViewer = new LogViewer(window.logsData);
    }
});

// ========================================
// 設定管理
// ========================================

$(document).ready(function() {
    // メール設定保存
    $('#email-settings-form').on('submit', function(e) {
        e.preventDefault();

        const developerAddress = $('#developer-address').val().trim();

        // バリデーション
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

        if (!emailPattern.test(developerAddress)) {
            showToast('danger', '開発者メールアドレスの形式が不正です');
            return;
        }

        // 保存
        showLoading();

        $.ajax({
            url: '',
            method: 'POST',
            data: {
                action: 'update_email_settings',
                developer_address: developerAddress,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                hideLoading();

                if (response.success !== false) {
                    showToast('success', response.message || 'メール設定を保存しました');
                } else {
                    showToast('danger', response.message || '保存に失敗しました');
                }
            },
            error: function(xhr) {
                hideLoading();
                const message = xhr.responseJSON?.message || '保存に失敗しました';
                showToast('danger', message);
            }
        });
    });
});
