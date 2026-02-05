# CLAUDE.md - AI Assistant Guide for route294

## Project Overview

**route294** is a sophisticated hotel housekeeping management system (ホテル清掃指示書作成システム) built with Django. It manages cleaning instructions and room assignments for a 154-room hotel (10 floors, rooms 201-1017).

### Key Capabilities
- Visual room allocation interface with grid-based selection
- **Autopilot (Sidewind)**: Automated room assignment algorithm with constraint optimization
- **User Authentication System**: Login and permission-based access control
- **Administrator Panel**: Complete system management (users, CSV files, logs, settings)
- Multi-language support (Japanese/English)
- Print-ready cleaning instruction sheets
- Time management and workload optimization
- Special room type tracking (Eco, Amenity, Duvet)
- Wincal PMS integration for occupancy data
- AI-assisted optimization (OpenAI integration)

### Version
Current version: 1.4.12+ (January 2026)
- Recent focus: Authentication system and administrator panel
- Autopilot algorithm continuously improved
- Weekly cleaning master data retention

---

## Technology Stack

### Backend
- **Framework**: Django 5.1.7 (Python 3.x)
- **Database**: SQLite3 (`db.sqlite3`)
- **Authentication**: Django Auth with custom decorators
- **Server**: WSGI/ASGI compatible
- **Template Engine**: Django Templates

### Frontend
- **CSS Framework**: Bootstrap 5.x
- **JavaScript**: jQuery 3.7.1
- **AJAX**: XMLHttpRequest with CSRF protection
- **Plugins**: TableSorter (sortable tables)
- **Styling**: Custom CSS per feature

### Key Python Dependencies
- **AI/ML**: openai (1.93.0), torch (2.2.2), stanza (1.1.1)
- **Translation**: googletrans, deep-translator, google-cloud-translate, argostranslate
- **NLP**: ctranslate2, sentencepiece
- **Data**: numpy (2.3.3), pandas
- **Excel**: openpyxl (2.6.2+)
- **HTTP**: requests, httpx, beautifulsoup4

### External Services
- Gmail SMTP for email notifications
- OpenAI API for AI-assisted optimization
- Google Translate APIs for multi-language support

---

## Directory Structure

```
/Users/yutasato/work/rootinn/route294/
├── route/                          # Django project root
│   ├── route/                      # Project configuration
│   │   ├── settings.py            # Main settings (email, logging, i18n, auth)
│   │   ├── urls.py                # URL routing (11 endpoints)
│   │   ├── wsgi.py / asgi.py      # Server configs
│   │
│   ├── cleaning/                   # Main application
│   │   ├── views/                 # View controllers (11 files)
│   │   │   ├── home.py            # Main interface (427 lines)
│   │   │   ├── login.py           # Authentication system (39 lines) ⭐ NEW
│   │   │   ├── administrator.py   # Admin panel (388 lines) ⭐ NEW
│   │   │   ├── preview.py         # Print preview generation (209 lines)
│   │   │   ├── sidewind.py        # Autopilot input form (93 lines)
│   │   │   ├── sidewind_front.py  # Autopilot backend (273 lines)
│   │   │   ├── rooming_list.py    # Wincal integration (411 lines)
│   │   │   ├── report.py          # Bug reporting system (63 lines)
│   │   │   ├── download_json.py   # JSON export/import (71 lines)
│   │   │   ├── release.py         # Release notes viewer (12 lines)
│   │   │   └── tech.py            # Technology info page (12 lines)
│   │   │
│   │   ├── utils/                 # Business logic layer
│   │   │   ├── sidewind_core.py   # Room assignment algorithm (697 lines) 🔴 CRITICAL
│   │   │   ├── preview_util.py    # Preview formatting & translation (633 lines)
│   │   │   └── home_util.py       # CSV reading & data processing (91 lines)
│   │   │
│   │   ├── templates/             # HTML templates (11 files)
│   │   │   ├── base.html          # Base layout with navigation
│   │   │   ├── login.html         # Login page (93 lines) ⭐ NEW
│   │   │   ├── administrator.html # Admin panel (578 lines) ⭐ NEW
│   │   │   ├── home.html          # Main interface (561 lines)
│   │   │   ├── preview.html       # Print preview (344 lines)
│   │   │   ├── sidewind.html      # Autopilot interface (151 lines)
│   │   │   ├── rooming_list.html  # Wincal upload form
│   │   │   ├── report.html        # Bug report form
│   │   │   ├── release.html       # Release notes display
│   │   │   ├── tech.html          # Technology info
│   │   │   └── ai_assist.html     # AI assistance (297 lines)
│   │   │
│   │   ├── templatetags/          # Custom Django template filters
│   │   │   └── custom_tags.py
│   │   │
│   │   ├── migrations/            # Database migrations
│   │   ├── models.py              # Database models (minimal - uses Django User)
│   │   ├── admin.py               # Django admin config
│   │   └── apps.py                # App configuration
│   │
│   ├── static/                     # Static assets
│   │   ├── js/                    # JavaScript (4,114 lines total)
│   │   │   ├── home.js            # Main UI logic (1,572 lines)
│   │   │   ├── sidewind.js        # Autopilot UI logic (1,498 lines)
│   │   │   ├── administrator.js   # Admin panel logic (1,044 lines) ⭐ NEW
│   │   │   └── preview.js         # Preview logic (29 lines)
│   │   │
│   │   ├── css/                   # Stylesheets (9 files)
│   │   │   ├── home.css           # Main page styles (~8KB)
│   │   │   ├── login.css          # Login page styles ⭐ NEW
│   │   │   ├── administrator.css  # Admin panel styles ⭐ NEW
│   │   │   ├── preview.css        # Preview styles (~7KB)
│   │   │   ├── sidewind.css       # Autopilot styles (~8KB)
│   │   │   ├── report.css         # Bug report styles
│   │   │   ├── rooming_list.css   # Rooming list styles
│   │   │   ├── release.css        # Release notes styles
│   │   │   └── tech.css           # Tech info styles
│   │   │
│   │   ├── csv/                   # Configuration data files
│   │   │   ├── room_info.csv      # Room metadata (154 rooms)
│   │   │   ├── times_by_type.csv  # Cleaning time standards
│   │   │   ├── master_key.csv     # Floor/master key mapping
│   │   │   └── weekly.csv         # Weekly cleaning schedules
│   │   │
│   │   ├── prompt/                # AI prompt templates
│   │   │   └── openAI.txt         # OpenAI prompt template
│   │   │
│   │   ├── bootstrap/             # Bootstrap framework files
│   │   ├── jquery/                # jQuery library
│   │   ├── tablesorter/           # TableSorter plugin
│   │   ├── logo.png               # Application logo
│   │   ├── favicon.ico
│   │   ├── email.json             # Email configuration (gitignored) 🔒
│   │   └── openai.json            # OpenAI API key (gitignored) 🔒
│   │
│   ├── db.sqlite3                 # SQLite database (User, Session data)
│   ├── manage.py                  # Django CLI
│   └── media/                     # User-uploaded/generated files (gitignored)
│
├── requirements.txt               # Python dependencies (113 packages)
├── README.md                      # Basic project description
├── CLAUDE.md                      # This file - AI assistant guide
├── .gitignore                     # Git ignore rules
└── logs/                          # Application logs (gitignored)
```

---

## Key Features & Components

### 1. Authentication System (`/login/` - login.html) ⭐ NEW

**Purpose**: Secure access control for administrative features

**Features**:
- Custom login page (not Django admin)
- Username/password authentication
- Staff-only access verification (`is_staff` flag required)
- Session management with Django auth
- Professional UI with logo and branding
- Error messaging for failed attempts
- Logout functionality

**Security**:
- Custom `@staff_required` decorator
- CSRF protection on all forms
- Password hashing via Django
- Session-based authentication
- Permission checks (`is_superuser` for sensitive operations)

**URLs**:
- `/login/` - Login page
- `/logout/` - Logout endpoint (POST)

### 2. Administrator Panel (`/administrator/` - administrator.html) ⭐ NEW

**Purpose**: Complete system management interface (staff-only)

**Access Control**:
- Requires login (`@login_required`)
- Requires staff permission (`@staff_required`)
- Some features require superuser permission

**Core Modules**:

#### 2.1 User Management (Superuser Only)
- **Create Users**: Username, password (8+ chars), email, permissions
- **User Roles**:
  - Staff: Can access administrator panel
  - Superuser: Full admin privileges (user management, all settings)
  - Regular: No admin access
- **User Listing**: Shows all users with join dates, last login, status
- **Edit Permissions**: Toggle staff/superuser flags
- **Delete Users**: Remove users (except self)
- **User Status**: Active/inactive tracking

#### 2.2 Password Management
- **Change Own Password**: Current user can update password
- **Validation**:
  - Current password verification
  - 8-character minimum
  - Password confirmation matching
  - Maintains session after change (`update_session_auth_hash`)

#### 2.3 Master Data (CSV) Management
- **List Files**: All CSV files in `static/csv/` with metadata
- **Create CSV**: New file with optional initial content
- **Edit CSV**:
  - Dual-mode editor (table view / text view)
  - Inline editing with validation
  - Preview first 20 rows
- **Delete CSV**: Remove master data files
- **File Info**: Size, modification timestamp
- **Security**: Path traversal protection

#### 2.4 Log Viewer & Management
- **Display Logs**: Parsed from `logs/log_*.log` files
- **Search**: Keyword filtering
- **Level Filter**: ERROR, WARNING, INFO, ALL
- **Pagination**: Configurable page size (10/25/50/100)
- **Statistics**: Log count by level
- **Delete**: Clear all log files
- **Format**: Timestamp, level, message, file

#### 2.5 Email Configuration
- **Developer Email**: Update recipient for bug reports
- **Validation**: Email format checking
- **Storage**: `static/email.json`
- **Security**: Email pattern regex validation

**UI Features**:
- Hero panel with system summary
- Card-based layout
- AJAX operations (no page reload)
- Toast notifications (success/error/warning/info)
- Loading overlays
- Confirmation modals for destructive actions
- Responsive design

**JavaScript** (`administrator.js` - 1,044 lines):
- CSRF token management
- Toast notification system
- CSV editor with dual-mode editing
- Log viewer with pagination
- Form validation
- AJAX error handling
- Delete confirmations
- XSS protection (`escapeHtml()`)

### 3. Main Interface (`/` - home.html)

**Purpose**: Daily cleaning instruction creation

**Features**:
- **Room Grid**: Visual 9×17 grid representing 154 hotel rooms
- **Room Selection**: Click-to-select interface with status colors
  - Full Cleaning (default)
  - Eco (5-minute quick clean)
  - Amenity (Eco-Out - eco on checkout day)
  - None (no service)
- **Housekeeper Management**: Track up to 100 housekeepers with:
  - Name input
  - Room assignments
  - Language preference (Japanese/English)
  - Contact information per person
- **Special Room Types**:
  - Eco rooms tracking
  - Amenity (Eco-Out) rooms
  - Duvet rooms
- **Time Configuration**: Customizable cleaning times
  - Single room (default: 24 min)
  - Twin room (default: 28 min)
  - Bath cleaning (default: 50 min)
- **Multiple Night Stays**: Track up to 100 rooms with multi-night guests
- **Communication**:
  - Room changes (original → destination)
  - Out-ins (guest arrivals/departures)
  - Must-clean rooms (priority cleaning)
  - Remarks and special notes
  - Spot cleaning instructions
- **Data Management**:
  - Save session to JSON
  - Load previous sessions
  - Wincal CSV integration
- **Autopilot Launch**: One-click to Sidewind algorithm

### 4. Autopilot Feature (`/sidewind` - Sidewind)

**Purpose**: Automatically assign rooms to housekeepers with optimization

**Algorithm** (`sidewind_core.py` - 697 lines) 🔴 MOST CRITICAL:
- **Method**: Multi-constraint optimization with 200 random strategy attempts
- **Constraints**:
  - Room quotas per housekeeper
  - Twin room quotas per housekeeper
  - Bath assignments (2-4 people)
  - Floor constraints (max 3 housekeepers per floor)
  - Eco room floor restrictions
  - Master key auto-assignment per floor
- **Objectives**:
  1. Even workload distribution (rooms and time)
  2. Twin room distribution fairness
  3. Floor constraint satisfaction
  4. Quota verification and validation
- **Process**:
  1. Receive quota parameters
  2. Run 200 allocation attempts with different strategies
  3. Score each solution (workload variance, constraint violations)
  4. Select best solution
  5. Renumber housekeepers by floor and bath assignment
  6. Validate and return allocation

**Recent Improvements** (commits):
- `188f969` - update admin page
- `1af34da` - design login page
- `360ad25` - update autopilot algorithm
- `43ff60a` - fix bug that autopilot
- `0805b1a` - improve sidewind logic

**UI** (`sidewind.html`, `sidewind.js` - 1,498 lines):
- **Input**:
  - Number of housekeepers
  - Room quota per person
  - Twin room quota per person
  - Bath staff selection (2-4 checkboxes)
  - Special room type counts
- **Output**:
  - Optimized room assignments
  - Per-housekeeper room lists
  - Floor distribution
  - Twin room distribution
  - Workload summary
- **Integration**: Results flow back to main interface via session

### 5. Preview & Print (`/preview`)

**Purpose**: Generate print-ready cleaning instructions

**Processing** (`preview_util.py` - 633 lines):
1. Parse form data from home
2. Process multiple-night cleaning requests
3. Handle special bath cleaning requests
4. Manage eco room inclusion logic
5. Calculate room counts by type (S/T)
6. Calculate target completion times
7. Generate DD (double-check) lists
8. Create cover sheet with daily summary
9. Create individual sheets per housekeeper

**Output**:
- **Cover Sheet**:
  - Daily summary (date, editor, total rooms)
  - Total counts (Full/Eco/Amenity/Bath)
  - Room changes
  - Out-ins
  - Must-clean rooms
  - Contact information
  - Remarks
- **Individual Sheets** (per housekeeper):
  - Assigned rooms by floor
  - Room types and special characteristics
  - Bath assignments
  - DD assignments
  - Target completion time
  - Contact info
  - Signature area

**Multi-Language Support**:
- Each housekeeper can have individual language preference
- Translation services integration:
  - Google Translate API
  - googletrans library
  - deep-translator
  - argostranslate (offline)
- Translates all UI labels and instructions

**Print Features**:
- Print-optimized CSS (`preview.css`)
- Page breaks between sheets
- Professional formatting
- Logo and branding

### 6. Wincal PMS Integration (`/rooming_list/`)

**Purpose**: Process occupancy data from Wincal hotel management system

**Features**:
- **CSV Upload**: Accept two CSV files (today/tomorrow)
- **Data Processing**:
  - Parse Shift-JIS encoded CSVs
  - Identify multiple-night stays (same guest + room across days)
  - Identify unused rooms (not in occupancy data)
- **Excel Generation**:
  - Yellow highlighting for multiple-night rooms
  - Diagonal strikethrough for unused rooms
  - Per-floor occupancy counts
  - Daily summary statistics
  - Output to `media/` directory
- **Integration**: Transfer data to main interface

**Technology**: pandas, openpyxl

### 7. Data Management

**JSON Export/Import** (`/download/json/`):
- **Save Session**: Export all current work to timestamped JSON file
- **Load Session**: Restore previous work from JSON
- **Exported Data**:
  - Editor name and date
  - Time configurations
  - Room assignments
  - Bath staff assignments
  - Housekeeper information
  - Special room types (eco, amenity, duvet)
  - Room changes and out-ins
  - Multiple-night tracking
  - Spot cleaning notes
  - Remarks and contacts
- **File Output**: `media/` directory with timestamp naming

**CSV Configuration**:
- `room_info.csv`: Room metadata (154 rooms)
- `times_by_type.csv`: Cleaning time standards
- `master_key.csv`: Floor/master key mapping
- `weekly.csv`: Weekly cleaning schedules

### 8. Bug Reporting (`/report`)

**Features**:
- Email-based bug submission to developer
- **Emergency Level**: A (critical), B (high), C (medium), D (low)
- **Genre Categories**:
  - Bug (functional errors)
  - Data (data-related issues)
  - Security (security vulnerabilities)
  - Feature (feature requests)
  - Performance (speed/optimization)
  - Usability (UX improvements)
- **Email Integration**:
  - Reads `static/email.json` for developer address
  - Sends via Gmail SMTP (TLS, port 587)
  - Requires Gmail app password

### 9. Information Pages

- **Release Notes** (`/release`): Version history and changes
- **Technology Info** (`/technology`): Tech stack and dependencies

---

## Architecture & Design Patterns

### MTV Pattern (Model-Template-View)
Django's standard architecture with clear separation:
- **Models**: Minimal database usage (Django User model + session-based state)
- **Templates**: Feature-specific HTML files with inheritance
- **Views**: Class-based views (TemplateView) + utility modules

### Authentication & Authorization Pattern
- **Login Required**: `@login_required` decorator redirects to `/login/`
- **Staff Required**: Custom `@staff_required` decorator checks `is_staff` flag
- **Permission Levels**:
  1. Public: Main interface, preview, JSON export
  2. Staff: Administrator panel access
  3. Superuser: User management, sensitive settings

### Utility Layer Pattern
Business logic separated into `utils/` modules:
- **sidewind_core.py**: Complex algorithm implementation
- **preview_util.py**: Data transformation, translation, formatting
- **home_util.py**: CSV reading, data processing helpers

### Session-Based State Management
- **Autopilot Results**: Stored in session (`request.session`)
- **Redirect Pattern**: sidewind → home (POST-redirect-GET variant)
- **Flag-Based State**: `sidewind_flag` tracks data source
- **Advantages**: No persistent storage, simple state handling
- **Limitations**: Data lost on session expiry, no undo/redo

### AJAX Pattern (Administrator Panel)
- **Non-Blocking Operations**: All admin actions use AJAX
- **Response Format**: JSON with `{success: bool, message: str}`
- **User Feedback**: Toast notifications for all operations
- **Loading States**: Overlay prevents double-submission
- **Error Handling**: Try-catch with user-friendly messages

### Data Flow Pattern
```
User Input (POST) → View Controller → Utility Processing →
Context Building → Template Rendering → Response
```

**Autopilot Flow**:
```
home.html → sidewind.html → sidewind_front.py → sidewind_core.py →
Session storage → home.py (with sidewind_flag) → home.html
```

**Print Flow**:
```
home.html (POST) → preview.py → preview_util.py →
preview.html → Browser print
```

### Code Organization Principles
1. **Feature-Based Separation**: Each feature has dedicated view, template, JS, CSS
2. **Utility Abstraction**: Reusable logic in utils modules
3. **Template Inheritance**: Base template with feature-specific extensions
4. **Custom Template Tags**: Filters in `templatetags/custom_tags.py`
5. **AJAX Integration**: Admin operations use AJAX for better UX
6. **Security Layers**: Decorators, CSRF, XSS protection, password validation

---

## Development Conventions

### Python Code Style
- **Views**: Class-based views inheriting from `TemplateView`
- **Imports**: Standard Django imports, then project imports
- **Logging**: Use Django's logging system (`logger = logging.getLogger('django')`)
- **Error Handling**: Try-except blocks with session flag checks
- **Decorators**: `@login_required`, `@staff_required` for access control

### Naming Conventions
- **Views**: `{feature}View` class (e.g., `homeView`, `administratorView`)
- **Templates**: `{feature}.html` (lowercase)
- **URLs**: Lowercase with underscores (e.g., `sidewind_front`)
- **JavaScript**: `{feature}.js` matching template name
- **CSS**: `{feature}.css` matching template name
- **Functions**: snake_case for Python, camelCase for JavaScript

### File Organization
- **Views**: One file per major feature in `views/`
- **Utils**: Separate files for distinct business logic
- **Templates**: One-to-one mapping with views
- **Static Assets**: Organized by type (js/, css/, csv/, etc.)
- **Security Files**: Gitignored (email.json, openai.json)

### Session Data Patterns
When passing data between views via redirect:
```python
# Setting data
request.session['sidewind_flag'] = True
request.session['allocation'] = allocation_dict

# Retrieving data
if request.session.get('sidewind_flag'):
    allocation = request.session['allocation']
    request.session['sidewind_flag'] = False
```

### AJAX Patterns (Administrator Panel)
```javascript
// Standard AJAX call
$.ajax({
    url: '/administrator/',
    method: 'POST',
    data: {
        action: 'action_name',
        param1: value1,
        csrfmiddlewaretoken: csrftoken
    },
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    },
    success: function(response) {
        if (response.success) {
            showToast('success', response.message);
        } else {
            showToast('danger', response.message);
        }
    },
    error: function() {
        showToast('danger', 'エラーが発生しました');
    }
});
```

### CSV Data Format
Configuration files in `static/csv/`:
- **room_info.csv**: Room number, type, floor
- **times_by_type.csv**: Room type, cleaning time
- **master_key.csv**: Floor, master key assignment
- **weekly.csv**: Week day, Japanese instructions, English instructions

---

## Important Files & Their Roles

### Critical Configuration Files

#### `route/route/settings.py`
- **Language**: `LANGUAGE_CODE = 'ja'` (Japanese)
- **Timezone**: `TIME_ZONE = 'Asia/Tokyo'`
- **Authentication**:
  - `LOGIN_URL = '/login/'`
  - `LOGIN_REDIRECT_URL = '/administrator/'`
  - `LOGOUT_REDIRECT_URL = '/'`
- **Email**: Gmail SMTP configuration (requires `static/email.json`)
- **Logging**: Daily log files in `logs/log_{YYYYMMDD}.log`
- **Static Files**: `STATICFILES_DIRS` points to `static/`
- **Media**: `MEDIA_ROOT` for uploaded/generated files
- **Security Warning**: `DEBUG = True` - DO NOT use in production

#### `route/route/urls.py`
URL routing structure:
- `/` → homeView (main interface - public)
- `/login/` → LoginView (authentication - public)
- `/logout/` → logout_view (logout - authenticated)
- `/administrator/` → administratorView (admin panel - staff only)
- `/administrator/get-csv/` → get_csv_view (CSV fetch - staff only)
- `/preview/` → previewView (print preview - public)
- `/sidewind/` → sidewindView (autopilot input - public)
- `/sidewind_front/` → sidewind_front (autopilot processor - public)
- `/rooming_list/` → roomingListView (Wincal integration - public)
- `/download/json/` → download_json (JSON export - public)
- `/report/` → reportView (bug reporting - public)
- `/release/` → releaseView (release notes - public)
- `/technology/` → techView (tech info - public)
- `/admin/` → Django Admin (superuser only)

### Critical Business Logic Files

#### `cleaning/views/administrator.py` (388 lines) ⭐ NEW
**THE ADMIN CONTROL CENTER**

Key components:
- **`@staff_required` decorator**: Custom login enforcement
- **`administratorView` class**: Main admin panel controller
- **`_list_master_files()`**: CSV file inventory with previews
- **`_list_logs(query)`**: Log parsing and filtering
- **`_load_json_setting(filename)`**: JSON config loader
- **`_save_json_setting(filename, data)`**: JSON config saver
- **`_list_users()`**: User listing with metadata
- **POST actions**:
  - `create_master` - New CSV file
  - `update_master` - Edit CSV content
  - `delete_master` - Remove CSV
  - `delete_logs` - Clear all logs
  - `update_email_settings` - Change developer email
  - `change_password` - Update user password
  - `create_user` - Add new user (superuser only)
  - `delete_user` - Remove user (superuser only)

**Security features**:
- CSRF validation
- Email format validation (regex)
- Password strength (8+ chars)
- Path traversal protection
- Permission checks (staff/superuser)
- Self-deletion prevention

#### `cleaning/views/login.py` (39 lines) ⭐ NEW
**AUTHENTICATION GATEWAY**

- **`LoginView`**: Custom login page handler
- **GET**: Display login form
- **POST**: Validate credentials
  - `authenticate(username, password)` - Django auth
  - Check `is_staff` flag
  - `login(request, user)` - Create session
  - Redirect to `/administrator/` or `next` URL
- **Error Handling**: Invalid credentials message
- **logout_view**: Session termination

#### `cleaning/utils/sidewind_core.py` (697 lines) ⚠️ MOST CRITICAL
The heart of the Autopilot feature. Contains:
- **`assign_rooms()` function**: Main allocation algorithm
  - 200 random strategy attempts
  - Multi-objective optimization
  - Constraint satisfaction checking
- **`_RoomAllocator` class**: Allocation engine
  - Room pool management
  - Floor tracking
  - Quota enforcement
  - Solution scoring
- **Constraints handled**:
  - Room quotas per housekeeper
  - Twin room quotas
  - Bath staff assignment (2-4 people)
  - Floor distribution (max 3 per floor)
  - Eco room allocation with floor restrictions
  - Master key assignment per floor

**When modifying**:
- Understand all constraints and objectives
- Review recent commits (algorithm actively improved)
- Test with various scenarios
- Verify quota totals match room counts
- Check edge cases (uneven distribution, floor restrictions)
- Test with maximum housekeepers (100)

#### `cleaning/utils/preview_util.py` (633 lines)
Data transformation for printing:
- **`catch_post(request)`**: Parse form data
- **`get_cover(request)`**: Extract cover sheet info
- **`multiple_night(request)`**: Process multi-night rooms
- **`special_clean(request)`**: Handle bath cleaning flags
- **`calc_room(...)`**: List rooms per housekeeper
- **`calc_room_type_count(...)`**: Count S/T rooms
- **`calc_end_time(...)`**: Calculate completion time
- **`calc_DD_list(...)`**: Create double-check assignments
- **`language(word, lang, text)`**: Bilingual translation
- **`weekly_cleaning(date)`**: Load weekly instructions
- Translation services integration
- Time calculations
- Cover sheet generation

#### `cleaning/utils/home_util.py` (91 lines)
Helper functions:
- **`read_csv()`**: Load configuration CSVs
- **`processing_list(room_info_data)`**: Convert room data to 2D array by floor
- **`dist_room(room_info_data)`**: Separate rooms by type (Single/Twin)
- **`room_person(room_num_table, room_inputs)`**: Map rooms to assigned housekeepers
- **`room_char(eco, ame, duvet)`**: Process special room characteristics

### Frontend Files

#### `static/js/administrator.js` (1,044 lines) ⭐ NEW
Administrator panel logic:
- **CSRF Management**: Token extraction and header setup
- **Toast System**: `showToast(type, message, duration)`
  - Success, danger, warning, info styles
  - Auto-hide after duration
- **Loading Overlay**: `showLoading()` / `hideLoading()`
- **CSV Editor**:
  - Dual-mode (table/text)
  - Inline editing
  - Validation
  - AJAX save
- **User Management**:
  - Create user modal
  - Delete user confirmation
  - Password change form
  - Validation (8+ chars, email format)
- **Log Viewer**:
  - Search/filter
  - Pagination
  - Level filtering (ERROR/WARNING/INFO/ALL)
- **Email Settings**: Update developer address
- **Error Handling**: Try-catch with user feedback
- **XSS Protection**: `escapeHtml()` function

#### `static/js/home.js` (1,572 lines)
Main interface logic:
- **Room Selection Engine**:
  - Click handlers for room grid
  - Status updates (Full/Eco/Ame/None)
  - Color coding
- **Housekeeper Management**:
  - Dynamic form field generation
  - Quota calculation
  - Assignment validation
- **Data Validation**:
  - Room count verification
  - Quota matching
  - Required field checking
- **Special Room Handling**:
  - Eco/Amenity/Duvet tracking
  - Remarks management
- **Communication Fields**:
  - Room changes (original → destination)
  - Out-ins tracking
  - Must-clean rooms
  - Spot cleaning notes
  - Contacts per housekeeper
- **Multiple-Night Stay Management**:
  - 100 room capacity
  - Multi-row display
- **Form Submission**:
  - JSON generation
  - Validation before submission
  - File upload handling
- **JSON Import/Export**:
  - Session restore
  - Format validation

#### `static/js/sidewind.js` (1,498 lines)
Autopilot interface logic:
- **Quota Input Handling**:
  - Dynamic row generation
  - Room quota per housekeeper
  - Twin quota per housekeeper
  - Bath staff checkboxes
- **Validation Engine**:
  - Quota total matching
  - Room type distribution
  - Twin room distribution
  - Floor constraint checking
- **Data Preparation**:
  - Form serialization
  - Housekeepers array creation
  - Room lists preparation
- **Result Display**:
  - Per-housekeeper room assignments
  - Workload distribution
  - Twin room distribution
  - Floor assignments
- **Algorithm Integration**:
  - Backend call
  - Response processing
  - Error reporting

#### `static/js/preview.js` (29 lines)
- Print functionality
- Page break handling
- Print stylesheet integration

### Template Files

#### `cleaning/templates/login.html` (93 lines) ⭐ NEW
Login page with:
- Centered card design
- Logo and branding ("Route294")
- Username/password fields with icons
- Error message display
- Submit button with icon
- Footer with copyright
- Decorative background circles
- Bootstrap styling
- CSRF protection

#### `cleaning/templates/administrator.html` (578 lines) ⭐ NEW
Administrator panel with:
- **Hero Panel**:
  - System summary
  - Eyebrow text ("Administrator")
  - Intro description
  - Feature pills (マスタ管理, APIキー, ログ監視)
  - Logout button
- **User Management Section** (superuser only):
  - User listing table
  - Create user modal
  - Delete user buttons
  - Password change button
  - Permission badges (staff/superuser)
- **Master Data Section**:
  - CSV file listing
  - Edit/delete buttons
  - Preview collapse
  - Create CSV button
  - Timestamp and size display
- **Settings Section**:
  - Email configuration form
  - Developer address input
- **Log Viewer Section**:
  - Search input
  - Level filters (ERROR/WARNING/INFO/ALL)
  - Page size selector
  - Log statistics
  - Delete all logs button
  - Paginated log table
- **Modals**:
  - Create User Modal (with role selection)
  - Change Password Modal
  - CSV Create Modal
  - CSV Editor Modal (dual-mode)
  - Delete Confirmation Modal
- **UI Components**:
  - Toast notification container
  - Loading overlay
  - Card-based layout
  - Responsive design

#### `cleaning/templates/base.html`
Base layout with:
- Bootstrap integration
- jQuery integration
- TableSorter plugin
- Common navigation footer
  - Report, Release, Tech, Admin links
- Block definitions for child templates
- Favicon and logo

#### `cleaning/templates/home.html` (561 lines)
Main interface template:
- Editor name and date inputs
- Time configuration section
- Room grid (9 floors × 17 rooms)
- Housekeeper assignment forms (dynamic)
- Special room selection areas
- Communication sections
- Multiple-night stay tracking
- Action buttons (Save, Preview, Autopilot, Wincal)
- JavaScript integration

#### `cleaning/templates/preview.html` (344 lines)
Print preview with:
- Cover sheet section
- Per-housekeeper instruction pages
- Room assignment lists by floor
- Bath assignment displays
- DD (double-check) lists
- Contact information
- Signature areas
- Print-optimized styling

---

## Common Development Tasks

### Starting the Development Server
```bash
cd /Users/yutasato/work/rootinn/route294/route
python manage.py runserver
```

Access:
- Main interface: http://localhost:8000/
- Login page: http://localhost:8000/login/
- Admin panel: http://localhost:8000/administrator/ (after login)

### Database Migrations
```bash
cd /Users/yutasato/work/rootinn/route294/route
python manage.py makemigrations
python manage.py migrate
```

### Creating Users

**Via Django Admin** (requires superuser):
```bash
cd /Users/yutasato/work/rootinn/route294/route
python manage.py createsuperuser
# Follow prompts
```

**Via Administrator Panel** (requires superuser login):
1. Login at `/login/`
2. Navigate to `/administrator/`
3. Click "新規ユーザー" button
4. Fill form:
   - Username
   - Password (8+ chars)
   - Email (optional)
   - is_staff (checkbox) - allows admin access
   - is_superuser (checkbox) - allows user management
5. Submit

### Changing Passwords

**Via Administrator Panel** (any staff user):
1. Login and go to `/administrator/`
2. Click "パスワード変更" button
3. Enter:
   - Current password
   - New password (8+ chars)
   - Confirm new password
4. Submit

**Via Django shell**:
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='username')
>>> user.set_password('new_password')
>>> user.save()
```

### Managing CSV Files

**Via Administrator Panel**:
1. Login and go to `/administrator/`
2. Master Data section:
   - **Create**: Click "新規作成", enter filename and content
   - **Edit**: Click "編集", modify in table or text mode
   - **Delete**: Click "削除", confirm
   - **Preview**: Click "▶ プレビュー" to see first 20 rows

**Via File System**:
```bash
cd /Users/yutasato/work/rootinn/route294/route/static/csv
# Edit files directly
nano room_info.csv
```

### Viewing Logs

**Via Administrator Panel**:
1. Login and go to `/administrator/`
2. Scroll to Log section
3. Use filters:
   - Level: ERROR, WARNING, INFO, ALL
   - Search: Keyword search
   - Page size: 10/25/50/100

**Via Terminal**:
```bash
cd /Users/yutasato/work/rootinn/route294/route
tail -f logs/log_$(date +%Y%m%d).log
```

### Adding New Features - Recommended Workflow

1. **Create View File** in `cleaning/views/{feature}.py`:
```python
from django.views.generic import TemplateView
from django.shortcuts import render

class featureView(TemplateView):
    template_name = "feature.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Handle form submission
        pass
```

2. **Create Template** in `cleaning/templates/{feature}.html`:
```html
{% extends "base.html" %}
{% load static %}
{% block content %}
<title>Feature Name</title>
<link rel="stylesheet" href="{% static 'css/feature.css' %}">

<!-- Feature content -->

{% endblock %}

{% block scripts %}
<script src="{% static 'js/feature.js' %}"></script>
{% endblock %}
```

3. **Add URL Route** in `route/urls.py`:
```python
from cleaning.views import feature as feature_view

# In urlpatterns:
path('feature/', feature_view.featureView.as_view(), name='feature'),
```

4. **Create Static Assets**:
- `static/js/{feature}.js` for JavaScript logic
- `static/css/{feature}.css` for styles

5. **Add Utility Functions** if needed in `cleaning/utils/{feature}_util.py`

6. **Update Navigation** in `base.html` if public-facing

7. **Add Tests** (recommended but not currently implemented)

### Modifying Autopilot Algorithm

**Location**: `cleaning/utils/sidewind_core.py`

**Before Modifying**:
1. Understand current constraints and objectives
2. Review recent commits (algorithm actively improved):
   - `360ad25` - update autopilot algorithm
   - `43ff60a` - fix bug that autopilot
   - `0805b1a` - improve sidewind logic
3. Test with various scenarios
4. Document changes

**After Modifying**:
1. Test edge cases:
   - Uneven quotas
   - Floor restrictions
   - Twin distribution
   - Maximum housekeepers (100)
2. Verify total quota matches total rooms
3. Check performance (200 attempts should complete quickly)
4. Test UI integration via sidewind page
5. Test with real data from hotel

**Testing Checklist**:
- [ ] Quota totals match room counts
- [ ] Floor constraints respected (max 3 per floor)
- [ ] Bath assignments correct (2-4 people)
- [ ] Twin rooms distributed evenly
- [ ] Eco rooms allocated properly with floor restrictions
- [ ] Master keys assigned per floor
- [ ] No unassigned rooms
- [ ] Workload balanced reasonably (time variance minimized)
- [ ] Solution found (not failing to allocate)
- [ ] Performance acceptable (< 5 seconds)

### Adding Authentication to New Features

**To require login**:
```python
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class NewFeatureView(TemplateView):
    # ...
```

**To require staff permission**:
```python
from cleaning.views.administrator import staff_required

@staff_required
def new_feature_view(request):
    # ...
```

**To check superuser**:
```python
def some_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Superuser required")
    # ...
```

---

## Testing & Quality Assurance

### Manual Testing Checklist

#### Authentication (`/login/`)
- [ ] Login with valid staff credentials succeeds
- [ ] Login with invalid credentials shows error
- [ ] Login with non-staff user is rejected
- [ ] Redirect to `/administrator/` after successful login
- [ ] Logout clears session and redirects to `/`
- [ ] Protected pages redirect to login when not authenticated

#### Administrator Panel (`/administrator/`)
- [ ] Access denied for non-authenticated users
- [ ] Access denied for non-staff users
- [ ] Superuser can see user management section
- [ ] Non-superuser cannot see user management section
- [ ] All AJAX operations show toast notifications
- [ ] Loading overlay appears during operations
- [ ] Page doesn't reload on AJAX operations

#### User Management (Superuser)
- [ ] Create user with valid data succeeds
- [ ] Create user with duplicate username fails
- [ ] Create user with short password fails
- [ ] Password validation enforces 8+ characters
- [ ] Email validation rejects invalid formats
- [ ] User listing shows all users with correct data
- [ ] Delete user removes from database
- [ ] Cannot delete self
- [ ] User roles (staff/superuser) display correctly

#### Password Management
- [ ] Change password with correct current password succeeds
- [ ] Change password with wrong current password fails
- [ ] Password confirmation mismatch fails
- [ ] 8-character minimum enforced
- [ ] Session maintained after password change

#### CSV Management
- [ ] CSV list displays all files with metadata
- [ ] Preview shows first 20 rows correctly
- [ ] Create CSV with valid name succeeds
- [ ] Edit CSV saves changes
- [ ] Delete CSV removes file
- [ ] Dual-mode editor (table/text) works
- [ ] Invalid CSV format shows error

#### Log Viewer
- [ ] Logs display with correct formatting
- [ ] Search filters logs by keyword
- [ ] Level filters work (ERROR/WARNING/INFO/ALL)
- [ ] Pagination works
- [ ] Page size selector changes display
- [ ] Delete all logs clears log files
- [ ] Statistics show correct counts

#### Email Settings
- [ ] Update developer email with valid format succeeds
- [ ] Invalid email format is rejected
- [ ] Settings persist across sessions

#### Main Interface (`/`)
- [ ] Room grid displays correctly (9 floors × 17 rooms)
- [ ] Room selection/deselection works
- [ ] Status changes (Full/Eco/Ame/None) update colors
- [ ] Housekeeper form fields appear/disappear correctly
- [ ] Time inputs validate properly
- [ ] JSON export includes all data
- [ ] JSON import restores state correctly
- [ ] Autopilot button navigates to sidewind
- [ ] Wincal button opens rooming list

#### Autopilot (`/sidewind`)
- [ ] Input validation works (quotas, bath staff)
- [ ] Quota total validation matches room count
- [ ] Algorithm runs without errors
- [ ] Results display correctly
- [ ] Integration with main interface works
- [ ] Master keys assigned automatically
- [ ] Quota verification passes
- [ ] Edge cases handled:
  - [ ] Uneven quotas
  - [ ] Maximum housekeepers (100)
  - [ ] Minimum housekeepers (1)
  - [ ] All twin rooms
  - [ ] All single rooms
  - [ ] Floor restrictions

#### Preview (`/preview`)
- [ ] All housekeepers have sheets
- [ ] Cover sheet displays correctly
- [ ] Times calculated accurately
- [ ] Room lists complete and correct
- [ ] Translation works (if English selected)
- [ ] Print formatting suitable
- [ ] Page breaks between sheets
- [ ] DD lists correct
- [ ] Bath assignments displayed

#### Bug Reporting (`/report`)
- [ ] Form validates inputs
- [ ] Email sends successfully
- [ ] Categories and priorities work
- [ ] Developer email from settings used

#### Wincal Integration (`/rooming_list/`)
- [ ] CSV upload accepts valid files
- [ ] Multiple-night detection works
- [ ] Unused room detection works
- [ ] Excel file generates correctly
- [ ] Formatting (colors, strikethrough) correct
- [ ] Data transfer to main interface works

### Common Issues & Solutions

#### Cannot Login / Always Redirected to Login
- **Check**: User exists and has `is_staff = True`
- **Fix**:
  ```bash
  python manage.py shell
  >>> from django.contrib.auth.models import User
  >>> user = User.objects.get(username='username')
  >>> user.is_staff = True
  >>> user.save()
  ```

#### "Permission Denied" on Administrator Page
- **Cause**: User not marked as staff
- **Fix**: Same as above, set `is_staff = True`

#### Email Not Sending (Bug Report)
- **Check**: `static/email.json` exists with valid credentials
- **Check**: Gmail "App Password" (not regular password)
- **Check**: Email settings in `settings.py`
- **Fix**: Create `static/email.json`:
  ```json
  {
      "address": "your-email@gmail.com",
      "password": "your-app-password",
      "developer_address": "developer@example.com"
  }
  ```

#### CSV Files Not Loading
- **Check**: Files exist in `static/csv/`
- **Check**: CSV format (no extra commas, proper headers)
- **Check**: File encoding (should be UTF-8)
- **Check**: File permissions (readable)

#### Session Data Lost (Autopilot Results)
- **Check**: Session middleware in `MIDDLEWARE` (settings.py)
- **Check**: Session storage (default: database)
- **Check**: `sidewind_flag` logic in views
- **Cause**: Session timeout or server restart
- **Prevention**: Use JSON export to save work

#### JavaScript Errors
- **Check**: Browser console (F12)
- **Check**: jQuery loading errors
- **Check**: CSRF token present
- **Check**: Static file paths in templates
- **Check**: AJAX response format

#### Autopilot Algorithm Issues
- **Check**: Input validation in `sidewind.js`
- **Check**: Quota totals match room counts
- **Check**: `sidewind_core.py` for algorithm errors
- **Review**: Recent commits for known fixes
- **Debug**: Add logging to algorithm
- **Test**: With smaller datasets first

#### AJAX Operations Failing
- **Check**: CSRF token in request
- **Check**: `X-Requested-With` header
- **Check**: Response format (JSON with success/message)
- **Check**: Server logs for errors
- **Debug**: Browser network tab

#### Toast Notifications Not Showing
- **Check**: Bootstrap JS loaded
- **Check**: Toast container in HTML
- **Check**: `showToast()` function defined
- **Check**: Message not empty

---

## Git Workflow & Branching

### Recent Commit History
```
188f969 - update admin page (2026-01-XX)
1af34da - design login page (2026-01-XX)
63b83f6 - delete debug log
9ce3a77 - 管理画面修正 (admin screen fix)
05915a6 - ver.1.4.12
308fc51 - Changed weekly cleaning settings to retain master data
360ad25 - update autopilot algorithm
43ff60a - fix bug that autopilot
0805b1a - improve sidewind logic
```

### Current Branch Strategy
- **Main Branch**: `main`
- **Feature Branches**: Use descriptive names
- **Hotfix Branches**: For urgent fixes

### Commit Message Conventions
Based on recent history:
- Direct descriptions (e.g., "fix autopilot core algorithm")
- Mix of English and Japanese (both acceptable)
- Feature additions: "add {feature}"
- Bug fixes: "fix {issue}" or "bug fix"
- Updates: "update {component}"
- Version tags: "ver.X.Y.Z"

### Example Commit Messages
```
add user authentication system
update admin panel with CSV editor
fix autopilot allocation algorithm
design login page
ver.1.4.12
管理画面修正 (admin screen fixes)
```

### Workflow Recommendations

**New Feature**:
```bash
git checkout -b feature/feature-name
# Make changes
git add .
git commit -m "add feature-name"
git push origin feature/feature-name
# Create pull request
```

**Bug Fix**:
```bash
git checkout -b fix/bug-description
# Fix bug
git add .
git commit -m "fix bug-description"
git push origin fix/bug-description
```

**Version Release**:
```bash
# Update version in relevant files
git add .
git commit -m "ver.X.Y.Z"
git tag -a vX.Y.Z -m "Version X.Y.Z"
git push origin main --tags
```

---

## Dependencies & External Services

### Required External Files (Gitignored)

#### `static/email.json` 🔒 REQUIRED
```json
{
    "address": "your-email@gmail.com",
    "password": "your-gmail-app-password",
    "developer_address": "developer@example.com"
}
```
- Required for bug reporting feature
- Required for administrator email settings
- Uses Gmail app password (not regular password)
- To create app password: Google Account → Security → 2-Step Verification → App passwords

#### `static/openai.json` 🔒 OPTIONAL
```json
{
    "api_key": "sk-..."
}
```
- Required for AI-assisted optimization features
- Optional if not using OpenAI integration

### Python Package Installation
```bash
cd /Users/yutasato/work/rootinn/route294
pip install -r requirements.txt
```

**Note**: 113 packages total, including:
- Django 5.1.7
- Heavy ML libraries (PyTorch 2.2.2, Stanza 1.1.1)
- Translation libraries (multiple providers)
- Excel processing (openpyxl)
- Data processing (pandas, numpy)

### Frontend Libraries (Included in `static/`)
- **Bootstrap 5.x**: UI framework
- **jQuery 3.7.1**: JavaScript library
- **TableSorter**: Sortable table plugin

### External Service Setup

#### Gmail SMTP
1. Enable 2-Step Verification in Google Account
2. Create App Password
3. Add credentials to `static/email.json`
4. Configure in `settings.py` (already done)

#### OpenAI API (Optional)
1. Sign up at platform.openai.com
2. Generate API key
3. Add to `static/openai.json`

#### Google Translate API (Optional)
- Currently uses free googletrans library
- For production, consider Google Cloud Translation API
- Requires API key and billing setup

---

## Security Considerations

### Current Security Features ✅

**Implemented**:
- **Authentication**: Django's built-in auth system
- **Authorization**: Custom decorators (`@staff_required`)
- **CSRF Protection**: Tokens in all forms and AJAX requests
- **Password Hashing**: Django's default (PBKDF2)
- **Password Strength**: 8-character minimum enforced
- **Email Validation**: Regex pattern matching
- **XSS Protection**:
  - HTML escaping in templates
  - `escapeHtml()` function in JavaScript
- **Path Traversal Protection**: `path.resolve()` checks in file access
- **JSON Validation**: Input validation on import
- **Session Security**: Session-based state (no persistent sensitive data)
- **Permission Checks**: Role-based access (public/staff/superuser)
- **Self-Deletion Prevention**: Cannot delete own user account

### Current Security Issues ⚠️

**Development Mode (DO NOT USE IN PRODUCTION)**:
1. **DEBUG = True**: Exposes sensitive error information
2. **SECRET_KEY**: Hardcoded in settings.py (should use environment variable)
3. **ALLOWED_HOSTS = ['*']**: Too permissive for production
4. **Email Credentials**: Stored in JSON file (consider environment variables)
5. **OpenAI API Key**: Stored in JSON file (consider secure vault)
6. **No HTTPS Enforcement**: HTTP allowed
7. **No Rate Limiting**: Brute-force login attempts possible
8. **No Audit Trail**: Admin actions not logged comprehensively
9. **No Input Sanitization**: CSV upload accepts any content
10. **No File Size Limits**: Large file uploads possible

### Recommendations for Production

#### 1. Environment Variables
```python
# settings.py
import os

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Email from environment
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# OpenAI from environment
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
```

#### 2. HTTPS Enforcement
```python
# settings.py (production only)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

#### 3. Rate Limiting
Install django-ratelimit:
```bash
pip install django-ratelimit
```

Apply to login view:
```python
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # ...
```

#### 4. Database
Consider PostgreSQL for production:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '5432',
    }
}
```

#### 5. Static Files
Use `collectstatic` and serve via web server:
```bash
python manage.py collectstatic
```

Configure Nginx/Apache to serve static files directly.

#### 6. Logging & Monitoring
- Log all admin actions
- Monitor failed login attempts
- Alert on suspicious activity
- Rotate logs regularly
- Use centralized logging (e.g., Sentry)

#### 7. File Upload Security
```python
# Validate file types
ALLOWED_EXTENSIONS = ['.csv', '.json', '.xlsx']

# Limit file sizes
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

#### 8. Secrets Management
Use Django secrets or cloud secret managers:
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager
- HashiCorp Vault

#### 9. Backup Strategy
- Daily database backups
- CSV master data backups
- Log archival
- Disaster recovery plan

#### 10. Security Headers
Add Django security middleware:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ... other middleware
]

X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
```

---

## AI Assistant Guidelines

### When Working on This Codebase

#### DO ✅:
- Read existing code before making changes
- Follow the established naming conventions
- Use the utility layer for business logic
- Test Autopilot changes thoroughly (mission-critical)
- Maintain feature-based file organization
- Keep views simple, move complexity to utils
- Use session for cross-view data passing
- Log important operations
- Consider both Japanese and English users
- Check CSV files for configuration data
- Test with authentication (login as staff/superuser)
- Verify permission checks work correctly
- Test AJAX operations in admin panel
- Ensure CSRF tokens present in forms
- Validate user input on both client and server
- Use decorators for access control
- Document security-sensitive changes

#### DON'T ❌:
- Mix business logic in views (use utils/)
- Break the session-based flow (sidewind → home)
- Ignore the existing constraint system in sidewind_core.py
- Add dependencies without updating requirements.txt
- Hardcode values (use CSV files or settings)
- Forget to test with maximum housekeepers (100)
- Change URL patterns without good reason
- Remove logging statements
- Skip authentication checks on new features
- Expose sensitive data in templates or JavaScript
- Store credentials in code
- Disable CSRF protection
- Create security vulnerabilities (XSS, SQL injection, etc.)
- Delete the .gitignore for sensitive files

### Understanding the Domain

**Hotel Context**:
- 154 rooms across 9 floors (2-10)
- Room types: Single (S), Twin (T)
- Cleaning types: Full, Eco (5 min), Amenity, None
- Special: Duvet rooms, multiple-night stays
- Housekeepers: Up to 100, with quotas and assignments
- Bath cleaning: Special task requiring 2-4 people
- Master keys: Floor-specific access

**User Roles**:
- **Public Users**: Can use main interface, create instructions, export data
- **Staff Users**: Can login, access administrator panel, manage system
- **Superusers**: Can manage users, full system control

**Business Rules**:
- Workload must be balanced fairly
- Floor constraints may apply (max 3 housekeepers per floor)
- Twin rooms distributed evenly
- Eco rooms have special allocation rules
- Quotas must match total rooms to clean
- Time calculations critical for scheduling
- Master key per floor for security

### Feature Priority Understanding
Based on git history, current focus areas:
1. **Authentication system** (login, permissions) ⭐ RECENT
2. **Administrator panel** (user/CSV/log management) ⭐ RECENT
3. **Autopilot algorithm** (continuous improvements)
4. **Weekly cleaning** (master data retention)
5. **Translation functionality**
6. **Logging and monitoring**

### When Asked to Add Features

1. **Determine Feature Scope**: Standalone page or integration?
2. **Determine Access Level**: Public, staff-only, or superuser-only?
3. **Follow Established Pattern**:
   - Create view in `views/{feature}.py`
   - Add decorators if authentication required
   - Create template in `templates/{feature}.html`
   - Add route in `urls.py`
   - Create JS in `static/js/{feature}.js`
   - Create CSS in `static/css/{feature}.css`
   - Add utility functions if needed in `utils/{feature}_util.py`
4. **Consider Integration Points**: How does it fit with existing features?
5. **Data Storage**: Session, database, CSV, or JSON export?
6. **Security**: Authentication, authorization, validation, sanitization
7. **Testing**: Manual test checklist

### When Asked to Debug

1. **Check Logs**: `logs/log_{date}.log`
2. **Check Browser Console**: For JavaScript errors
3. **Check Network Tab**: For AJAX/HTTP errors
4. **Check Session Data**: May need to clear/reset
5. **Check CSV Files**: Configuration may be wrong
6. **Check Email/OpenAI Config**: External dependencies
7. **Check User Permissions**: Staff/superuser flags
8. **Review Recent Commits**: Issue may be recently introduced
9. **Check Authentication**: Login state, session timeout
10. **Verify CSRF Tokens**: Forms and AJAX requests

### When Modifying Authentication/Authorization

**Critical Areas**:
- `views/login.py` - Login/logout logic
- `views/administrator.py` - Admin panel and permissions
- `@staff_required` decorator - Custom access control
- URL configuration - Public vs protected routes
- Templates - Conditional display based on permissions

**Testing Required**:
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Access protected pages without login
- [ ] Access as non-staff user
- [ ] Access as staff user
- [ ] Access as superuser
- [ ] Logout clears session
- [ ] Session timeout works
- [ ] CSRF protection active

---

## Troubleshooting Guide

### Application Won't Start

**Check**:
1. Python dependencies installed (`pip install -r requirements.txt`)
2. Working directory is `/Users/yutasato/work/rootinn/route294/route/`
3. Port 8000 not already in use
4. Database migrations applied (`python manage.py migrate`)
5. `static/email.json` exists (can be empty `{}` for testing)

**Fix**:
```bash
cd /Users/yutasato/work/rootinn/route294/route
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

### Cannot Login

**Symptoms**: Always redirected to login page, or "invalid credentials"

**Check**:
1. User exists in database
2. User has `is_staff = True` flag
3. Password is correct
4. Session middleware enabled
5. Database accessible

**Fix**:
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> user.is_staff = True
>>> user.save()
>>> # Or create new user
>>> User.objects.create_user('admin', password='password', is_staff=True)
```

### Administrator Panel Shows "Permission Denied"

**Cause**: User not marked as staff

**Fix**: Set `is_staff = True` (see above)

### Superuser Features Not Visible

**Symptoms**: Cannot see user management section

**Check**: User has `is_superuser = True`

**Fix**:
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> user.is_superuser = True
>>> user.save()
```

### Autopilot Not Working

**Check**:
1. Input validation passes (quotas, bath staff count)
2. Total quota matches room count
3. Check `sidewind_core.py` for algorithm errors
4. Session data set correctly (`sidewind_flag`)
5. Review recent algorithm fixes in git history

**Debug**:
```bash
tail -f /Users/yutasato/work/rootinn/route294/route/logs/log_*.log
# Run autopilot and watch for errors
```

### Preview Not Generating

**Check**:
1. Room assignments exist in submitted data
2. CSV files loaded correctly
3. Translation services available (for English output)
4. Context data complete in `preview_util.py`

### CSV Data Not Loading

**Check**:
1. Files exist in `static/csv/`
2. File encoding is UTF-8
3. CSV format correct (headers, no extra commas)
4. File permissions allow reading

**Fix**:
```bash
cd /Users/yutasato/work/rootinn/route294/route/static/csv
ls -la
cat room_info.csv | head
```

### Session Data Issues

**Check**:
1. Session middleware enabled in settings
2. Database migrations applied
3. `sidewind_flag` logic correct in views
4. Session not expired (default timeout: 2 weeks)

**Clear Session**:
```bash
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> Session.objects.all().delete()
```

### AJAX Operations Failing

**Symptoms**: Admin operations show errors, no toast notifications

**Check**:
1. CSRF token in request headers
2. `X-Requested-With: XMLHttpRequest` header present
3. Response is valid JSON
4. Server logs for errors
5. Browser network tab for HTTP status

**Debug**:
```javascript
// In browser console
console.log('CSRF Token:', $('[name=csrfmiddlewaretoken]').val());
```

### Email Not Sending

**Check**:
1. `static/email.json` exists with valid credentials
2. Gmail "App Password" (not regular password)
3. 2-Step Verification enabled in Google Account
4. Email settings in `settings.py` correct
5. Network allows SMTP (port 587)

**Fix**:
Create `static/email.json`:
```json
{
    "address": "your-email@gmail.com",
    "password": "your-16-char-app-password",
    "developer_address": "developer@example.com"
}
```

### Translation Not Working

**Check**:
1. Translation libraries installed
2. Internet connection available (for online services)
3. API keys configured (if using paid services)
4. Language parameter passed correctly

**Fallback**: Japanese only if translation fails

### Database Locked Error

**Symptoms**: "database is locked" errors

**Cause**: SQLite concurrency limitations

**Fix**:
- Wait and retry
- Ensure no multiple processes accessing database
- Consider PostgreSQL for production

### Static Files Not Loading

**Symptoms**: CSS/JS not applied, 404 errors

**Check**:
1. `STATICFILES_DIRS` in settings.py
2. File paths in templates (`{% static 'path' %}`)
3. Files exist in `static/` directory
4. Proper capitalization

**Fix**:
```bash
python manage.py findstatic home.js
# Should show full path
```

---

## Release History

### Recent Versions
- **1.4.12** (January 2026): Current version
  - Authentication system (login/logout)
  - Administrator panel (user management, CSV editor, log viewer)
  - Weekly cleaning master data retention
  - Admin page updates

- **1.4.11** (December 2025)
  - Autopilot algorithm improvements
  - Bug fixes

- **1.4.10** (December 2025)
  - Multiple-night room input improvements
  - Sidewind logic fixes

### Major Feature Additions by Version
- **1.4.x**: Authentication, administrator panel, user management
- **1.4.0**: Major Autopilot improvements
- **1.3.x**: Translation features, Wincal integration
- **1.2.x**: Autopilot initial implementation
- **1.1.x**: Core features (room grid, preview, JSON export)
- **1.0.x**: Initial release

---

## Future Considerations

### Planned Improvements
1. **Full AI Integration**: Complete OpenAI-assisted optimization
2. **Database Persistence**: Move from session-based to database models
3. **RESTful API**: For mobile apps or external integrations
4. **Real-time Updates**: WebSocket for collaborative editing
5. **Analytics Dashboard**: Housekeeper performance tracking
6. **Audit Trail**: Complete logging of admin actions
7. **Two-Factor Authentication**: Enhanced security
8. **Role-Based Permissions**: Fine-grained access control
9. **Automated Testing**: Unit tests, integration tests
10. **Email Notifications**: For various system events

### Scalability Considerations
- **Current Limits**: 100 housekeepers, 154 rooms
- **Session-Based State**: May not scale well with many concurrent users
- **SQLite**: Suitable for single-hotel, consider PostgreSQL for multiple hotels
- **Algorithm Performance**: 200 attempts is fast now, may need optimization for larger hotels

### Potential Extensions
1. **Mobile App**: React Native or Flutter app
2. **Multi-Property**: Support multiple hotels in one system
3. **Reporting**: Generate weekly/monthly reports
4. **Integration**: Connect to other PMS systems beyond Wincal
5. **Inventory Management**: Track cleaning supplies
6. **Schedule Management**: Shift planning for housekeepers
7. **Quality Tracking**: Inspection results and feedback
8. **Guest Preferences**: Special requests and VIP tracking

---

## Contact & Support

### Bug Reporting
Use built-in bug report feature at `/report/`:
- Email sent to developer (configured in `static/email.json`)
- Include emergency level (A-D)
- Specify category (bug/data/security/feature/performance/usability)
- Provide detailed description

### Developer Information
- **University**: University of Tsukuba
- **Developer**: YutaSato
- **Year**: 2025-2026
- **Contact**: Via email in `email.json` settings

### Administrator Panel
For system administrators:
- Login at `/administrator/`
- Access logs, user management, CSV files
- Configure email settings
- View system status

---

## Quick Reference

### Key File Locations
| Purpose | Path |
|---------|------|
| Main View | `route/cleaning/views/home.py` |
| Login View | `route/cleaning/views/login.py` ⭐ |
| Admin View | `route/cleaning/views/administrator.py` ⭐ |
| Autopilot Algorithm | `route/cleaning/utils/sidewind_core.py` |
| Main Template | `route/cleaning/templates/home.html` |
| Login Template | `route/cleaning/templates/login.html` ⭐ |
| Admin Template | `route/cleaning/templates/administrator.html` ⭐ |
| Main JavaScript | `route/static/js/home.js` |
| Admin JavaScript | `route/static/js/administrator.js` ⭐ |
| Settings | `route/route/settings.py` |
| URL Routing | `route/route/urls.py` |
| Room Config | `route/static/csv/room_info.csv` |
| Times Config | `route/static/csv/times_by_type.csv` |
| Email Config | `route/static/email.json` 🔒 |

### Key URLs
| URL | Purpose | Access Level |
|-----|---------|--------------|
| `/` | Main interface | Public |
| `/login/` | Authentication | Public |
| `/logout/` | Logout | Authenticated |
| `/administrator/` | Admin panel | Staff only |
| `/administrator/get-csv/` | CSV fetch | Staff only |
| `/sidewind/` | Autopilot input | Public |
| `/sidewind_front/` | Autopilot processor | Public |
| `/preview/` | Print preview | Public |
| `/download/json/` | JSON export | Public |
| `/rooming_list/` | Wincal integration | Public |
| `/report/` | Bug reporting | Public |
| `/release/` | Release notes | Public |
| `/technology/` | Tech info | Public |

### Common Commands
```bash
# Navigate to project
cd /Users/yutasato/work/rootinn/route294/route

# Start server
python manage.py runserver

# Access points
# Main: http://localhost:8000/
# Login: http://localhost:8000/login/
# Admin: http://localhost:8000/administrator/

# Database operations
python manage.py makemigrations
python manage.py migrate

# User management
python manage.py createsuperuser
python manage.py shell

# View logs
tail -f logs/log_$(date +%Y%m%d).log

# Install dependencies
pip install -r ../requirements.txt

# Git operations
git status
git log --oneline -10
git add .
git commit -m "message"
git push
```

### User Role Reference
| Role | Permissions |
|------|-------------|
| **Public** | Main interface, preview, JSON export, Autopilot, bug report |
| **Staff** | All public + Administrator panel access |
| **Superuser** | All staff + User management, sensitive settings |

### File Size Reference
| Component | Lines of Code |
|-----------|---------------|
| **Views** | ~1,999 total |
| - administrator.py ⭐ | 388 |
| - home.py | 427 |
| - rooming_list.py | 411 |
| - sidewind_front.py | 273 |
| - preview.py | 209 |
| **Utils** | ~1,421 total |
| - sidewind_core.py | 697 |
| - preview_util.py | 633 |
| - home_util.py | 91 |
| **JavaScript** | ~4,143 total |
| - home.js | 1,572 |
| - sidewind.js | 1,498 |
| - administrator.js ⭐ | 1,044 |
| - preview.js | 29 |
| **Templates** | ~2,581 total |
| - administrator.html ⭐ | 578 |
| - home.html | 561 |
| - preview.html | 344 |
| - sidewind.html | 151 |
| - login.html ⭐ | 93 |
| **Total Code** | ~10,144 lines |

---

## Conclusion

Route294 is a **well-architected, feature-rich hotel housekeeping management system** with:

✅ **Strong Core Features**:
- Sophisticated Autopilot room allocation algorithm
- Comprehensive main interface for daily operations
- Print-ready instruction sheets with multi-language support
- Wincal PMS integration for occupancy data

✅ **Modern Authentication** ⭐ NEW:
- Secure login system with Django auth
- Role-based access control (public/staff/superuser)
- Session management with CSRF protection

✅ **Powerful Administrator Panel** ⭐ NEW:
- Complete user management (create/edit/delete)
- CSV master data editor with dual-mode (table/text)
- Log viewer with search and filtering
- Email configuration management
- Password change functionality
- AJAX-based operations with toast notifications

✅ **Modern Web Stack**:
- Django 5.1.7 with best practices
- Bootstrap 5 + jQuery for responsive UI
- AJAX for non-blocking operations
- Clean separation of concerns (MTV pattern)

✅ **Multi-Language Support**:
- Japanese/English throughout
- Individual housekeeper language preferences
- Translation services integration

✅ **Integration Capabilities**:
- Wincal PMS (CSV import)
- Excel generation (openpyxl)
- Email notifications (Gmail SMTP)
- OpenAI API (partial)
- Google Translate APIs

⚠️ **Production Readiness Notes**:
- Change `DEBUG = False`
- Use environment variables for secrets
- Enable HTTPS enforcement
- Consider PostgreSQL for production
- Implement rate limiting
- Add comprehensive audit logging
- Regular security audits

**Primary Focus Areas** (Current Development):
1. **Authentication System** ⭐ - Login, permissions, user management
2. **Administrator Panel** ⭐ - System management interface
3. **Autopilot Algorithm** - Continuous optimization
4. **Weekly Cleaning** - Master data management
5. **Logging & Monitoring** - System observability

**Version**: 1.4.12+ (January 2026)
**Status**: Production-ready with proper configuration
**Total Codebase**: ~10,144 lines of Python/JavaScript/HTML

---

**Document Version**: 2.0
**Last Updated**: 2026-01-XX
**Codebase Version**: 1.4.12+
**Changes in v2.0**:
- ⭐ Added authentication system documentation
- ⭐ Added administrator panel documentation
- ⭐ Added user management documentation
- Updated file structure with new components
- Updated URL endpoints (+3 new)
- Added security considerations section
- Updated testing checklist
- Added troubleshooting for authentication issues
- Updated statistics (code lines, features)
