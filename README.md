# Route294 - Hotel Housekeeping Management System
# ホテル清掃指示書作成システム

![Version](https://img.shields.io/badge/version-1.4.12+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.1.7-green.svg)
![Python](https://img.shields.io/badge/Python-3.x-yellow.svg)
![License](https://img.shields.io/badge/license-Private-red.svg)

A sophisticated web-based hotel housekeeping management system for a 153-room hotel. Features intelligent room allocation, multi-language support, and comprehensive administrative tools.

**ホテルの客室清掃業務を効率化する高度なWebアプリケーション。153室のホテル向けに、インテリジェントな部屋割り当て、多言語対応、包括的な管理ツールを提供します。**

---

## ✨ Key Features / 主な機能

### Core Functionality / コア機能
- **🏨 Visual Room Grid**: Interactive 9×17 grid for 153 rooms across 10 floors
  - **ビジュアル客室グリッド**: 10フロア・153室を9×17のインタラクティブなグリッドで表示
- **🤖 Autopilot (Sidewind)**: AI-powered room allocation algorithm with constraint optimization
  - **オートパイロット（Sidewind）**: 制約最適化による自動部屋割り当てアルゴリズム
- **🖨️ Print Preview**: Generate professional cleaning instruction sheets
  - **印刷プレビュー**: プロフェッショナルな清掃指示書を生成
- **🌏 Multi-Language**: Japanese/English support for international staff
  - **多言語対応**: 日本語/英語対応で外国人スタッフにも対応
- **🔒 Authentication**: Secure login system with role-based access control
  - **認証システム**: ロールベースのアクセス制御による安全なログイン
- **⚙️ Administrator Panel**: Complete system management (users, logs, CSV files)
  - **管理者パネル**: システム全体の管理（ユーザー、ログ、CSVファイル）

### Additional Features / その他の機能
- Wincal PMS integration for occupancy data / Wincal PMS連携による占有データ取得
- JSON-based session save/load / JSONベースのセッション保存/読み込み
- Special room tracking (Eco, Amenity, Duvet) / 特別室の追跡（エコ、アメニティ、羽毛布団）
- Multiple-night stay management / 連泊管理
- Bath cleaning assignments / 浴室清掃割り当て
- Workload balancing and time calculations / 作業負荷の均衡化と時間計算
- Email-based bug reporting / メールによるバグレポート

---

## 🚀 Quick Start / クイックスタート

### Prerequisites / 前提条件
- Python 3.x
- pip (Python package manager)
- Git

### Installation / インストール

```bash
# Clone the repository / リポジトリのクローン
git clone <repository-url>
cd route294

# Install dependencies / 依存関係のインストール
cd route
pip install -r ../requirements.txt

# Run database migrations / データベースマイグレーション
python manage.py migrate

# Create a superuser account / スーパーユーザーアカウントの作成
python manage.py createsuperuser

# Start the development server / 開発サーバーの起動
python manage.py runserver
```

### Access / アクセス

- **Main Interface**: http://localhost:8000/
  - メインインターフェース（誰でもアクセス可能）
- **Login Page**: http://localhost:8000/login/
  - ログインページ（スタッフ用）
- **Administrator Panel**: http://localhost:8000/administrator/
  - 管理者パネル（スタッフのみ、ログイン後）

---

## 📋 Basic Usage / 基本的な使い方

### Daily Cleaning Instructions / 日々の清掃指示書作成

1. **Access Main Interface** / メインインターフェースにアクセス
   - Navigate to http://localhost:8000/

2. **Select Rooms** / 部屋を選択
   - Click on room numbers in the grid to select rooms for cleaning
   - グリッド内の部屋番号をクリックして清掃する部屋を選択

3. **Assign Housekeepers** / ハウスキーパーを割り当て
   - Enter housekeeper names and assign rooms manually
   - ハウスキーパー名を入力し、手動で部屋を割り当て
   - **OR use Autopilot** for automatic assignment
   - **または自動割り当てにはオートパイロットを使用**

4. **Generate Instructions** / 指示書を生成
   - Click "Preview" to generate print-ready sheets
   - 「プレビュー」をクリックして印刷可能なシートを生成

### Autopilot (Automatic Assignment) / オートパイロット（自動割り当て）

1. Click "Autopilot" button from main interface / メインインターフェースで「オートパイロット」ボタンをクリック
2. Enter quotas for each housekeeper / 各ハウスキーパーの割り当て部屋数を入力
3. Select bath cleaning staff / 浴室清掃担当者を選択
4. Click "Run Algorithm" / 「アルゴリズム実行」をクリック
5. Review results and accept / 結果を確認して受け入れ

### Administrator Panel / 管理者パネル

**Staff-only feature** / スタッフ専用機能

1. **Login** at /login/ with staff credentials / スタッフ認証情報で /login/ にログイン
2. **User Management** (superuser only) / ユーザー管理（スーパーユーザーのみ）
   - Create, edit, delete users / ユーザーの作成、編集、削除
   - Assign permissions (staff/superuser) / 権限の割り当て（スタッフ/スーパーユーザー）
3. **CSV File Management** / CSVファイル管理
   - Edit master data files (room info, times, master keys) / マスターデータファイルの編集（部屋情報、時間、マスターキー）
4. **Log Viewing** / ログ表示
   - Search and filter application logs / アプリケーションログの検索とフィルタリング
5. **Email Settings** / メール設定
   - Configure developer email for bug reports / バグレポート用の開発者メールを設定

---

## 📁 Project Structure / プロジェクト構造

```
route294/
├── route/                      # Django project
│   ├── cleaning/              # Main application
│   │   ├── views/            # Controllers (11 files)
│   │   ├── utils/            # Business logic
│   │   ├── templates/        # HTML templates
│   │   └── ...
│   ├── static/               # CSS, JS, CSV config files
│   ├── db.sqlite3           # Database
│   └── manage.py            # Django CLI
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── CLAUDE.md                # Detailed developer guide
```

---

## 🔧 Configuration / 設定

### Required Files / 必須ファイル

Create these files in `route/static/` (gitignored):
これらのファイルを `route/static/` に作成してください（gitignoreされています）：

#### `email.json` (Required for bug reporting / バグレポートに必要)
```json
{
    "address": "your-email@gmail.com",
    "password": "your-gmail-app-password",
    "developer_address": "developer@example.com"
}
```

**Note**: Use Gmail App Password, not regular password
**注意**: 通常のパスワードではなく、GmailのAppパスワードを使用してください

#### `openai.json` (Optional for AI features / AI機能用、オプション)
```json
{
    "api_key": "sk-..."
}
```

### CSV Configuration Files / CSV設定ファイル

Located in `route/static/csv/`:
`route/static/csv/` に配置：

- **room_info.csv**: Room metadata (153 rooms)
  - 部屋のメタデータ（153室）
- **times_by_type.csv**: Standard cleaning times
  - 標準清掃時間
- **master_key.csv**: Floor/master key mapping
  - フロア/マスターキーのマッピング
- **weekly.csv**: Weekly cleaning schedules
  - 週次清掃スケジュール

---

## 👥 User Roles / ユーザーロール

| Role | Access / アクセス権限 |
|------|---------------------|
| **Public** | Main interface, preview, JSON export, Autopilot<br>メインインターフェース、プレビュー、JSONエクスポート、オートパイロット |
| **Staff** | All public features + Administrator panel<br>すべての公開機能 + 管理者パネル |
| **Superuser** | All features + User management<br>すべての機能 + ユーザー管理 |

---

## 🛠️ Technology Stack / 技術スタック

### Backend / バックエンド
- **Django 5.1.7** - Web framework
- **Python 3.x** - Programming language
- **SQLite3** - Database

### Frontend / フロントエンド
- **Bootstrap 5** - CSS framework
- **jQuery 3.7.1** - JavaScript library
- **AJAX** - Async operations

### External Services / 外部サービス
- Gmail SMTP - Email notifications
- Google Translate APIs - Multi-language support
- OpenAI API (optional) - AI optimization

---

## 📖 Documentation / ドキュメント

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive developer guide (English)
  - 包括的な開発者ガイド（英語）
  - ~2,171 lines of technical documentation
  - Architecture, API reference, troubleshooting
- **[README_ja.md](README_ja.md)** - Japanese version of this file
  - このファイルの日本語版

---

## 🔐 Security Notes / セキュリティに関する注意

⚠️ **Development Mode** - DO NOT use in production without changes:
⚠️ **開発モード** - 変更せずに本番環境で使用しないでください：

- `DEBUG = True` - Disable in production / 本番環境では無効化
- `SECRET_KEY` - Use environment variable / 環境変数を使用
- `ALLOWED_HOSTS = ['*']` - Restrict in production / 本番環境では制限
- Credentials in JSON files - Use secure storage / JSONファイルの認証情報 - 安全なストレージを使用

See [CLAUDE.md - Security Considerations](CLAUDE.md#security-considerations) for production recommendations.
本番環境の推奨事項については、[CLAUDE.md - セキュリティに関する考慮事項](CLAUDE.md#security-considerations)を参照してください。

---

## 🐛 Troubleshooting / トラブルシューティング

### Cannot Login / ログインできない
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> user.is_staff = True
>>> user.save()
```

### Application Won't Start / アプリケーションが起動しない
```bash
cd route
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

### More Issues / その他の問題
See [CLAUDE.md - Troubleshooting Guide](CLAUDE.md#troubleshooting-guide) for detailed solutions.
詳細な解決策については、[CLAUDE.md - トラブルシューティングガイド](CLAUDE.md#troubleshooting-guide)を参照してください。

---

## 📝 Version History / バージョン履歴

### v1.4.12+ (January 2026 / 2026年1月)
- ⭐ Authentication system (login/logout)
  - 認証システム（ログイン/ログアウト）
- ⭐ Administrator panel (user/CSV/log management)
  - 管理者パネル（ユーザー/CSV/ログ管理）
- Weekly cleaning master data retention
  - 週次清掃マスターデータの保持
- Admin page updates
  - 管理ページの更新

### v1.4.11 (December 2025 / 2025年12月)
- Autopilot algorithm improvements
  - オートパイロットアルゴリズムの改善
- Bug fixes / バグ修正

### v1.4.10 (December 2025 / 2025年12月)
- Multiple-night room input improvements
  - 連泊部屋入力の改善
- Sidewind logic fixes
  - Sidewindロジックの修正

### Earlier Versions / 以前のバージョン
- v1.4.0: Major Autopilot improvements
- v1.3.x: Translation features, Wincal integration
- v1.2.x: Autopilot initial implementation
- v1.1.x: Core features
- v1.0.x: Initial release

See full history in [CLAUDE.md - Release History](CLAUDE.md#release-history).

---

## 📄 License / ライセンス

Private/Proprietary - University of Tsukuba
非公開/プロプライエタリ - 筑波大学

---

## 👨‍💻 Developer / 開発者

**YutaSato**
- University of Tsukuba / 筑波大学
- 2025-2026

---

## 📧 Contact & Support / お問い合わせとサポート

### Bug Reports / バグ報告
Use the built-in bug report feature:
組み込みのバグレポート機能を使用してください：
- Navigate to http://localhost:8000/report/
- Fill out the form with details / 詳細を記入
- Email automatically sent to developer / 開発者に自動的にメール送信

### Administrator Support / 管理者サポート
- Login to administrator panel: http://localhost:8000/administrator/
- Access logs, user management, system settings
- 管理者パネルにログイン：http://localhost:8000/administrator/
- ログ、ユーザー管理、システム設定にアクセス

---

## 🎯 Quick Reference / クイックリファレンス

### Common Commands / よく使うコマンド
```bash
# Start server / サーバー起動
python manage.py runserver

# Create superuser / スーパーユーザー作成
python manage.py createsuperuser

# View logs / ログ表示
tail -f logs/log_$(date +%Y%m%d).log

# Database migrations / データベースマイグレーション
python manage.py migrate
```

### Key URLs / 主要URL
- Main: http://localhost:8000/
- Login: http://localhost:8000/login/
- Admin: http://localhost:8000/administrator/
- Preview: http://localhost:8000/preview/
- Autopilot: http://localhost:8000/sidewind/

---

## 🌟 Features at a Glance / 機能概要

| Feature | Description |
|---------|-------------|
| 🏨 **Room Management** | Visual grid, status tracking, special types<br>ビジュアルグリッド、ステータス追跡、特別タイプ |
| 🤖 **Autopilot** | Processing-powered automatic room allocation<br>計算による自動部屋割り当て |
| 👥 **Staff Management** | Up to 100 housekeepers, quotas, assignments<br>最大100人のハウスキーパー、割り当て数、割り当て |
| 🖨️ **Print System** | Professional cleaning instruction sheets<br>プロフェッショナルな清掃指示書 |
| 🌏 **Multi-Language** | Japanese/English per housekeeper<br>ハウスキーパーごとに日本語/英語 |
| 📊 **Wincal Integration** | Import occupancy data from PMS<br>PMSから占有データをインポート |
| 💾 **Data Management** | JSON save/load, CSV configuration<br>JSON保存/読み込み、CSV設定 |
| 🔒 **Security** | Login system, role-based access<br>ログインシステム、ロールベースアクセス |
| ⚙️ **Administration** | User/CSV/log management, settings<br>ユーザー/CSV/ログ管理、設定 |

---

**For detailed technical documentation, see [CLAUDE.md](CLAUDE.md)** 📚
**詳細な技術ドキュメントについては、[CLAUDE.md](CLAUDE.md)を参照してください** 📚
