# CLAUDE.md - AI Assistant Guide for route294

## Project Overview

**route294** is a sophisticated hotel housekeeping management system (ホテル清掃指示書作成システム) built with Django. It manages cleaning instructions and room assignments for a 154-room hotel (10 floors, rooms 201-1017).

### Key Capabilities
- Visual room allocation interface with grid-based selection
- **Autopilot (Sidewind)**: Automated room assignment algorithm with constraint optimization
- Multi-language support (Japanese/English)
- Print-ready cleaning instruction sheets
- Time management and workload optimization
- Special room type tracking (Eco, Amenity, Duvet)
- AI-assisted optimization (OpenAI integration)

### Version
Current version: 1.4.0+ (based on recent commits focusing on Autopilot algorithm improvements)

---

## Technology Stack

### Backend
- **Framework**: Django 5.1.7 (Python 3.x)
- **Database**: SQLite3 (`db.sqlite3`)
- **Server**: WSGI/ASGI compatible
- **Template Engine**: Django Templates

### Frontend
- **CSS Framework**: Bootstrap 5.x
- **JavaScript**: jQuery 3.7.1
- **Plugins**: TableSorter (sortable tables)
- **Styling**: Custom CSS per feature

### Key Python Dependencies
- **AI/ML**: openai (1.93.0), torch (2.2.2), stanza (1.1.1)
- **Translation**: googletrans, deep-translator, google-cloud-translate, argostranslate
- **NLP**: ctranslate2, sentencepiece
- **Data**: numpy (2.3.3)
- **HTTP**: requests, httpx, beautifulsoup4

### External Services
- Gmail SMTP for email notifications
- OpenAI API for AI-assisted optimization

---

## Directory Structure

```
/home/user/route294/
├── route/                          # Django project root
│   ├── route/                      # Project configuration
│   │   ├── settings.py            # Main settings (email, logging, i18n)
│   │   ├── urls.py                # URL routing
│   │   ├── wsgi.py / asgi.py      # Server configs
│   │
│   ├── cleaning/                   # Main application
│   │   ├── views/                 # View controllers (9 files)
│   │   │   ├── home.py            # Main interface (332 lines)
│   │   │   ├── preview.py         # Print preview generation (204 lines)
│   │   │   ├── sidewind.py        # Autopilot backend
│   │   │   ├── sidewind_front.py  # Autopilot frontend (216 lines)
│   │   │   ├── report.py          # Bug reporting system
│   │   │   ├── download_json.py   # JSON export/import
│   │   │   ├── release.py         # Release notes viewer
│   │   │   ├── tech.py            # Technology info page
│   │   │   └── administrator.py   # Admin panel
│   │   │
│   │   ├── utils/                 # Business logic layer
│   │   │   ├── sidewind_core.py   # Room assignment algorithm (CRITICAL)
│   │   │   ├── preview_util.py    # Preview formatting & translation
│   │   │   └── home_util.py       # CSV reading & data processing
│   │   │
│   │   ├── templates/             # HTML templates (9 files)
│   │   │   ├── base.html          # Base layout
│   │   │   ├── home.html          # Main interface (561 lines)
│   │   │   ├── preview.html       # Print preview (344 lines)
│   │   │   ├── sidewind.html      # Autopilot interface (151 lines)
│   │   │   └── ai_assist.html     # AI assistance (297 lines)
│   │   │
│   │   ├── templatetags/          # Custom Django template filters
│   │   │   └── custom_tags.py
│   │   │
│   │   ├── migrations/            # Database migrations
│   │   ├── models.py              # Database models (minimal usage)
│   │   ├── admin.py               # Django admin config
│   │   └── apps.py                # App configuration
│   │
│   ├── static/                     # Static assets
│   │   ├── js/                    # JavaScript (2,882 lines total)
│   │   │   ├── home.js            # Main UI logic (1,430 lines)
│   │   │   ├── sidewind.js        # Autopilot UI logic (1,423 lines)
│   │   │   └── preview.js         # Preview logic (29 lines)
│   │   │
│   │   ├── css/                   # Stylesheets
│   │   │   ├── home.css           # Main page styles (~8KB)
│   │   │   ├── preview.css        # Preview styles (~7KB)
│   │   │   └── sidewind.css       # Autopilot styles (~8KB)
│   │   │
│   │   ├── csv/                   # Configuration data files
│   │   │   ├── room_info.csv      # Room metadata (154 rooms)
│   │   │   ├── times_by_type.csv  # Cleaning time standards
│   │   │   └── master_key.csv     # Floor/master key mapping
│   │   │
│   │   ├── prompt/                # AI prompt templates
│   │   │   └── openAI.txt         # OpenAI prompt template
│   │   │
│   │   ├── bootstrap/             # Bootstrap framework files
│   │   ├── jquery/                # jQuery library
│   │   ├── tablesorter/           # TableSorter plugin
│   │   ├── logo.png               # Application logo
│   │   └── favicon.ico
│   │
│   ├── db.sqlite3                 # SQLite database
│   ├── manage.py                  # Django CLI
│   └── media/                     # User-uploaded/generated files (gitignored)
│
├── requirements.txt               # Python dependencies (113 packages)
├── README.md                      # Basic project description
├── .gitignore                     # Git ignore rules
└── logs/                          # Application logs (gitignored)
```

---

## Key Features & Components

### 1. Main Interface (`/` - home.html)
- **Room Grid**: Visual 9x17 grid representing 154 hotel rooms
- **Room Selection**: Click-to-select interface with status colors
- **Housekeeper Management**: Track up to 100 housekeepers with quotas
- **Special Room Types**: Eco, Amenity (Eco-Out), Duvet rooms
- **Time Configuration**: Customizable cleaning times per room type
- **Multiple Night Stays**: Track up to 100 rooms with multi-night guests
- **Communication**: Room changes, out-ins, must-clean rooms, remarks

### 2. Autopilot Feature (`/sidewind` - Sidewind)
**Purpose**: Automatically assign rooms to housekeepers with optimization

**Algorithm** (`sidewind_core.py`):
- Multi-constraint optimization for room allocation
- Considers: room quotas, bath assignments, floor constraints, twin distribution
- Even workload distribution
- Eco room allocation with floor restrictions
- Master key auto-assignment per floor
- Quota verification and validation

**Recent Improvements** (commits `2ccde6f`, `bd5c88a`, `33ce3ee`, `67686ce`):
- Core algorithm fixes
- Automatic DD and master key assignment on submit
- Algorithm optimization for better allocation

**UI** (`sidewind.html`, `sidewind.js`):
- Input: Number of housekeepers, quotas, bath staff (2-4 people)
- Output: Optimized room assignments
- Integration: Results flow back to main interface via session

### 3. Preview & Print (`/preview`)
- Generate print-ready cleaning instructions
- Individual sheets per housekeeper
- Cover sheet with daily summary
- Multi-language output (Japanese/English per housekeeper)
- Translation services integration
- Time calculations and workload display

### 4. Data Management
- **JSON Export/Import** (`/download/json/`): Save/load work sessions
- **CSV Configuration**: Room info, cleaning times, master keys
- **Media Storage**: Generated files saved to `media/` directory
- **Timestamp-based Naming**: Files named with date/time

### 5. Bug Reporting (`/report`)
- Email-based bug submission to developer
- Emergency level classification (A-D)
- Category tracking (bug, data, security, feature, performance, usability)
- Direct Gmail SMTP integration

### 6. Administration
- Release notes viewer (`/release`)
- Technology info page (`/technology`)
- Administrator panel (`/administrator`)

---

## Architecture & Design Patterns

### MTV Pattern (Model-Template-View)
Django's standard architecture with clear separation:
- **Models**: Minimal database usage (mostly session-based state)
- **Templates**: Feature-specific HTML files
- **Views**: Class-based views (TemplateView) + utility modules

### Utility Layer Pattern
Business logic separated into `utils/` modules:
- **sidewind_core.py**: Complex algorithm implementation
- **preview_util.py**: Data transformation, translation, formatting
- **home_util.py**: CSV reading, data processing helpers

### Session-Based State Management
- Autopilot results stored in session (`request.session`)
- Redirect pattern: sidewind → home (POST-redirect-GET variant)
- Flag-based state tracking (`sidewind_flag`)

### Data Flow Pattern
```
User Input (POST) → View Controller → Utility Processing →
Context Building → Template Rendering → Response
```

### Code Organization Principles
1. **Feature-Based Separation**: Each feature has dedicated view, template, JS, CSS
2. **Utility Abstraction**: Reusable logic in utils modules
3. **Template Inheritance**: Base template with feature-specific extensions
4. **Custom Template Tags**: Filters in `templatetags/custom_tags.py`

---

## Development Conventions

### Python Code Style
- **Views**: Class-based views inheriting from `TemplateView`
- **Imports**: Standard Django imports, then project imports
- **Logging**: Use Django's logging system (`logger = logging.getLogger('django')`)
- **Error Handling**: Try-except blocks with session flag checks

### Naming Conventions
- **Views**: `{feature}View` class (e.g., `homeView`, `sidewindView`)
- **Templates**: `{feature}.html` (lowercase)
- **URLs**: Lowercase with underscores (e.g., `sidewind_front`)
- **JavaScript**: `{feature}.js` matching template name
- **CSS**: `{feature}.css` matching template name

### File Organization
- **Views**: One file per major feature in `views/`
- **Utils**: Separate files for distinct business logic
- **Templates**: One-to-one mapping with views
- **Static Assets**: Organized by type (js/, css/, csv/, etc.)

### Session Data Patterns
When passing data between views via redirect:
```python
# Setting data
request.session['sidewind_flag'] = True
request.session['allocation'] = allocation_dict

# Retrieving data
if request.session['sidewind_flag']:
    allocation = request.session['allocation']
    request.session['sidewind_flag'] = False
```

### CSV Data Format
Configuration files in `static/csv/`:
- **room_info.csv**: Room number, type, floor
- **times_by_type.csv**: Room type, cleaning time
- **master_key.csv**: Floor, master key assignment

---

## Important Files & Their Roles

### Critical Configuration Files

#### `route/route/settings.py`
- **Language**: `LANGUAGE_CODE = 'ja'` (Japanese)
- **Timezone**: `TIME_ZONE = 'Asia/Tokyo'`
- **Email**: Gmail SMTP configuration (requires `static/email.json`)
- **Logging**: Daily log files in `logs/log_{YYYYMMDD}.log`
- **Static Files**: `STATICFILES_DIRS` points to `/route/static/`
- **Media**: `MEDIA_ROOT` for uploaded/generated files
- **Security Warning**: `DEBUG = True` - DO NOT use in production

#### `route/route/urls.py`
URL routing structure:
- `/` → homeView (main interface)
- `/preview/` → previewView (print preview)
- `/sidewind/` → sidewindView (autopilot backend)
- `/sidewind_front/` → sidewind_front (autopilot display)
- `/download/json/` → download_json (JSON export)
- `/report/` → reportView (bug reporting)
- `/release/` → releaseView (release notes)
- `/technology/` → techView (tech info)
- `/administrator/` → administratorView (admin panel)

### Critical Business Logic Files

#### `cleaning/utils/sidewind_core.py` ⚠️ MOST CRITICAL
The heart of the Autopilot feature. Contains:
- Room allocation algorithm
- Constraint-based optimization
- Multi-objective balancing
- Recent algorithm improvements (see git history)

**When modifying**:
- Understand constraints: quotas, floors, bath assignments, twins, eco rooms
- Test thoroughly with various scenarios
- Verify quota totals match room counts
- Check edge cases (uneven distribution, floor restrictions)

#### `cleaning/utils/preview_util.py`
Data transformation for printing:
- Format room assignments per housekeeper
- Translation services integration
- Time calculations
- Cover sheet generation

#### `cleaning/utils/home_util.py`
Helper functions:
- `read_csv()`: Load configuration CSVs
- `processing_list()`: Convert room data to 2D array by floor
- `dist_room()`: Separate rooms by type (Single/Twin)
- `room_person()`: Map rooms to assigned housekeepers
- `room_char()`: Process special room characteristics

### Frontend Files

#### `static/js/home.js` (1,430 lines)
Main interface logic:
- Room selection/deselection
- Status updates (Full/Eco/Ame/None)
- Dynamic form field management
- Housekeeper count controls
- Data validation before submission
- Multiple night stay management
- JSON import/export

#### `static/js/sidewind.js` (1,423 lines)
Autopilot interface logic:
- Housekeeper input validation
- Quota calculations
- Bath staff selection
- Data preparation for backend
- Result display formatting

### Template Files

#### `cleaning/templates/base.html`
Base layout with:
- Bootstrap integration
- jQuery integration
- Common navigation
- Block definitions for child templates

#### `cleaning/templates/home.html` (561 lines)
Main interface template:
- Room grid rendering (9 floors × 17 rooms)
- Housekeeper input forms (dynamic)
- Special room selection areas
- Time configuration inputs
- Communication sections
- JavaScript integration

---

## Common Development Tasks

### Starting the Development Server
```bash
cd /home/user/route294/route
python manage.py runserver
```

### Database Migrations
```bash
cd /home/user/route294/route
python manage.py makemigrations
python manage.py migrate
```

### Creating a Superuser (Django Admin)
```bash
cd /home/user/route294/route
python manage.py createsuperuser
```

### Viewing Logs
```bash
cd /home/user/route294/route
tail -f logs/log_$(date +%Y%m%d).log
```

### Adding New Features - Recommended Workflow

1. **Create View File** in `cleaning/views/{feature}.py`:
```python
from django.views.generic import TemplateView

class featureView(TemplateView):
    template_name = "feature.html"

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)
```

2. **Create Template** in `cleaning/templates/{feature}.html`:
```html
{% extends "base.html" %}
{% block content %}
<!-- Feature content -->
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

### Modifying Autopilot Algorithm

**Location**: `cleaning/utils/sidewind_core.py`

**Before Modifying**:
1. Understand current constraints and objectives
2. Review recent commits (algorithm has been actively improved)
3. Test with various scenarios

**After Modifying**:
1. Test edge cases: uneven quotas, floor restrictions, twin distribution
2. Verify total quota matches total rooms
3. Check performance with maximum housekeepers (100)
4. Test UI integration via sidewind page

**Testing Checklist**:
- [ ] Quota totals match room counts
- [ ] Floor constraints respected
- [ ] Bath assignments correct (2-4 people)
- [ ] Twin rooms distributed evenly
- [ ] Eco rooms allocated properly
- [ ] Master keys assigned per floor
- [ ] No unassigned rooms
- [ ] Workload balanced reasonably

### Modifying CSV Configuration

**Room Info** (`static/csv/room_info.csv`):
```csv
room_number,type,floor
201,S,2
202,T,2
```

**Cleaning Times** (`static/csv/times_by_type.csv`):
```csv
type,minutes
Single,24
Twin,28
Bath,50
Eco,5
```

**Master Keys** (`static/csv/master_key.csv`):
```csv
floor,master_key
2,A
3,B
```

---

## Testing & Quality Assurance

### Manual Testing Checklist

#### Main Interface (`/`)
- [ ] Room grid displays correctly (9 floors × 17 rooms)
- [ ] Room selection/deselection works
- [ ] Status changes (Full/Eco/Ame/None) update colors
- [ ] Housekeeper form fields appear/disappear correctly
- [ ] Time inputs validate properly
- [ ] JSON export includes all data
- [ ] JSON import restores state correctly

#### Autopilot (`/sidewind`)
- [ ] Input validation works (quotas, bath staff)
- [ ] Algorithm runs without errors
- [ ] Results display correctly
- [ ] Integration with main interface works
- [ ] Master keys assigned automatically
- [ ] Quota verification passes
- [ ] Edge cases handled (see above)

#### Preview (`/preview`)
- [ ] All housekeepers have sheets
- [ ] Cover sheet displays correctly
- [ ] Times calculated accurately
- [ ] Room lists complete and correct
- [ ] Translation works (if English selected)
- [ ] Print formatting suitable

#### Bug Reporting (`/report`)
- [ ] Form validates inputs
- [ ] Email sends successfully
- [ ] Categories and priorities work

### Common Issues & Solutions

#### Email Not Sending
- Check `static/email.json` exists with valid credentials
- Verify Gmail "App Password" (not regular password)
- Check email settings in `settings.py`

#### CSV Files Not Loading
- Verify files exist in `static/csv/`
- Check CSV format (no extra commas, proper headers)
- Look for encoding issues (should be UTF-8)

#### Session Data Lost
- Check session middleware in `MIDDLEWARE` (settings.py)
- Verify session storage (default: database)
- Check `sidewind_flag` logic in views

#### JavaScript Errors
- Open browser console (F12)
- Check for jQuery loading errors
- Verify static file paths in templates

#### Autopilot Algorithm Issues
- Review `sidewind_core.py` logic
- Check input validation in `sidewind.js`
- Verify quota totals match room counts
- Look at recent commits for known fixes

---

## Git Workflow & Branching

### Current Branch Strategy
- **Main Branch**: (unspecified in git status)
- **Feature Branches**: Use `claude/` prefix with session ID
- **Current Branch**: `claude/claude-md-mihnrzhsw1htiyeu-01U3WPMmTRCE5Y8Phb9Zy1Nu`

### Commit Message Conventions
Based on recent history:
- Direct descriptions (e.g., "fix autopilot core algorithm")
- Mix of English and Japanese (both acceptable)
- Feature additions: "add {feature}"
- Bug fixes: "fix {issue}" or "bug fix"
- Version tags: "ver.X.Y.Z"

### Example Commit Messages
```
fix autopilot core algorithm
add auto dd and masterkey when submit sidewind
ver.1.4.0
add autopilot process
bug fix
add translate function
```

### Pushing Changes
Always use:
```bash
git push -u origin <branch-name>
```
Branch must start with `claude/` and match session ID.

---

## Dependencies & External Services

### Required External Files (Gitignored)

#### `static/email.json`
```json
{
    "address": "your-email@gmail.com",
    "password": "your-app-password"
}
```
Required for bug reporting feature.

#### `static/openai.json` (if using AI features)
```json
{
    "api_key": "sk-..."
}
```
Required for OpenAI integration.

### Python Package Installation
```bash
pip install -r requirements.txt
```

**Note**: 113 packages total, including heavy ML libraries (PyTorch, etc.)

### Frontend Libraries (Included)
- Bootstrap 5.x (in `static/bootstrap/`)
- jQuery 3.7.1 (in `static/jquery/`)
- TableSorter (in `static/tablesorter/`)

---

## Security Considerations

### Current Security Issues ⚠️

1. **DEBUG = True**: Must be False in production
2. **SECRET_KEY**: Visible in settings.py (should use environment variable)
3. **ALLOWED_HOSTS = ['*']**: Too permissive for production
4. **Email Credentials**: Stored in JSON file (consider environment variables)

### Recommendations for Production

1. **Environment Variables**:
```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
```

2. **Database**: Consider PostgreSQL for production (currently SQLite)

3. **Static Files**: Use `collectstatic` and serve via web server

4. **HTTPS**: Enforce HTTPS in production:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## AI Assistant Guidelines

### When Working on This Codebase

#### DO:
- ✅ Read existing code before making changes
- ✅ Follow the established naming conventions
- ✅ Use the utility layer for business logic
- ✅ Test Autopilot changes thoroughly (it's mission-critical)
- ✅ Maintain feature-based file organization
- ✅ Keep views simple, move complexity to utils
- ✅ Use session for cross-view data passing
- ✅ Log important operations
- ✅ Consider both Japanese and English users
- ✅ Check CSV files for configuration data

#### DON'T:
- ❌ Mix business logic in views (use utils/)
- ❌ Break the session-based flow (sidewind → home)
- ❌ Ignore the existing constraint system in sidewind_core.py
- ❌ Add dependencies without updating requirements.txt
- ❌ Hardcode values (use CSV files or settings)
- ❌ Forget to test with maximum housekeepers (100)
- ❌ Change URL patterns without good reason
- ❌ Remove logging statements

### Understanding the Domain

**Hotel Context**:
- 154 rooms across 9 floors (2-10)
- Room types: Single (S), Twin (T)
- Cleaning types: Full, Eco (5 min), Amenity, None
- Special: Duvet rooms, multiple-night stays
- Housekeepers: Up to 100, with quotas and assignments
- Bath cleaning: Special task requiring 2-4 people
- Master keys: Floor-specific access

**Business Rules**:
- Workload must be balanced fairly
- Floor constraints may apply
- Twin rooms distributed evenly
- Eco rooms have special allocation rules
- Quotas must match total rooms to clean
- Time calculations critical for scheduling

### Feature Priority Understanding
Based on git history, current focus areas:
1. **Autopilot algorithm** (multiple recent fixes)
2. Auto-assignment features (DD, master keys)
3. Translation functionality
4. Logging and monitoring

### When Asked to Add Features

1. **Determine Feature Scope**: Standalone page or integration?
2. **Follow Established Pattern**:
   - Create view in `views/{feature}.py`
   - Create template in `templates/{feature}.html`
   - Add route in `urls.py`
   - Create JS in `static/js/{feature}.js`
   - Create CSS in `static/css/{feature}.css`
3. **Consider Integration Points**: How does it fit with existing features?
4. **Data Storage**: Session, database, CSV, or JSON export?

### When Asked to Debug

1. **Check Logs**: `logs/log_{date}.log`
2. **Check Browser Console**: For JavaScript errors
3. **Check Session Data**: May need to clear/reset
4. **Check CSV Files**: Configuration may be wrong
5. **Check Email/OpenAI Config**: External dependencies
6. **Review Recent Commits**: Issue may be recently introduced

---

## Troubleshooting Guide

### Application Won't Start

**Check**:
1. `static/email.json` exists with valid credentials
2. Python dependencies installed (`pip install -r requirements.txt`)
3. Working directory is `/home/user/route294/route/`
4. Port 8000 not already in use

### Autopilot Not Working

**Check**:
1. Input validation passes (quotas, bath staff count)
2. Total quota matches room count
3. Check `sidewind_core.py` for algorithm errors
4. Session data set correctly (`sidewind_flag`)
5. Review recent algorithm fixes in git history

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

### Session Data Issues

**Check**:
1. Session middleware enabled in settings
2. Database migrations applied
3. `sidewind_flag` logic correct in views
4. Session not expired (default timeout)

---

## Release History (Recent)

Based on git log:
- **1.4.0**: Major version (commit `bfea3c1`)
- **Recent Focus**: Autopilot algorithm improvements (3 consecutive commits)
- **Recent Additions**: Auto DD/master key on sidewind submit
- **1.3.12**: Previous version
- **1.3.11**: Earlier version

---

## Future Considerations

### Potential Improvements
1. **AI Integration**: Fully implement OpenAI-assisted optimization
2. **Database Models**: Move from session-based to database persistence
3. **API**: RESTful API for mobile apps or external integrations
4. **User Authentication**: Multi-user support with permissions
5. **Real-time Updates**: WebSocket for collaborative editing
6. **Analytics**: Housekeeper performance tracking over time
7. **Testing**: Unit tests for algorithm, integration tests for views

### Scalability Considerations
- Current limit: 100 housekeepers, 154 rooms
- Session-based state may not scale well
- SQLite suitable for single-user, consider PostgreSQL for multi-user

---

## Contact & Support

### Bug Reporting
Use built-in bug report feature at `/report/`:
- Email sent to developer (configured in `static/email.json`)
- Include emergency level (A-D)
- Specify category (bug/data/security/feature/performance/usability)

### Developer Information
Based on email configuration in settings.py

---

## Quick Reference

### Key File Locations
| Purpose | Path |
|---------|------|
| Main View | `route/cleaning/views/home.py` |
| Autopilot Algorithm | `route/cleaning/utils/sidewind_core.py` |
| Main Template | `route/cleaning/templates/home.html` |
| Main JavaScript | `route/static/js/home.js` |
| Settings | `route/route/settings.py` |
| URL Routing | `route/route/urls.py` |
| Room Config | `route/static/csv/room_info.csv` |
| Times Config | `route/static/csv/times_by_type.csv` |

### Key URLs
| URL | Purpose |
|-----|---------|
| `/` | Main interface |
| `/sidewind/` | Autopilot (backend) |
| `/sidewind_front/` | Autopilot (display) |
| `/preview/` | Print preview |
| `/download/json/` | JSON export |
| `/report/` | Bug reporting |
| `/release/` | Release notes |
| `/technology/` | Tech info |
| `/administrator/` | Admin panel |

### Common Commands
```bash
# Start server
cd /home/user/route294/route && python manage.py runserver

# View logs
tail -f /home/user/route294/route/logs/log_$(date +%Y%m%d).log

# Database migrations
cd /home/user/route294/route && python manage.py migrate

# Install dependencies
pip install -r /home/user/route294/requirements.txt
```

---

## Conclusion

This is a well-structured Django application with sophisticated business logic, particularly in the Autopilot room allocation algorithm. The codebase follows Django best practices with clear separation of concerns. The recent development focus has been on improving the Autopilot algorithm and adding automation features.

When working on this codebase, pay special attention to:
1. **Autopilot algorithm** (`sidewind_core.py`) - mission-critical
2. **Session-based data flow** - unique pattern in this app
3. **Multi-language support** - Japanese and English throughout
4. **CSV configuration** - external data dependencies
5. **Recent commits** - algorithm actively being improved

Always test changes thoroughly, especially anything touching the Autopilot feature or room allocation logic.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-27
**Codebase Version**: 1.4.0+
