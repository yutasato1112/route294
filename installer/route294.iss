; ========================================
; Route294 Installer - Inno Setup Script
; ホテル清掃指示書作成システム
; ========================================

#define MyAppName "Route294"
#define MyAppVersion "1.5.3"
#define MyAppPublisher "YutaSato -University of Tsukuba-"
#define MyAppURL "http://localhost:8000/"
#define MyAppExeName "launcher.bat"

[Setup]
AppId={{A3F2B8C1-7D4E-4A5F-9B6C-8E2D1F3A4B5C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=Route294_Setup_{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Japanese language
LanguageDetectionMethod=uilanguage

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "デスクトップにショートカットを作成"; GroupDescription: "追加オプション:"
Name: "startmenuicon"; Description: "スタートメニューにショートカットを作成"; GroupDescription: "追加オプション:"

[Files]
; Python Embedded + packages
Source: "build\python\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs

; Django project
Source: "build\route\*"; DestDir: "{app}\route"; Flags: ignoreversion recursesubdirs createallsubdirs

; Launcher scripts
Source: "build\launcher.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "build\stop.bat"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\route\logs"; Permissions: users-modify
Name: "{app}\route\media"; Permissions: users-modify

[Icons]
; Desktop shortcut
Name: "{autodesktop}\Route294"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\route\static\favicon.ico"; Comment: "Route294 - ホテル清掃指示書作成システム"; Tasks: desktopicon

; Start Menu shortcuts
Name: "{group}\Route294"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\route\static\favicon.ico"; Tasks: startmenuicon
Name: "{group}\Route294 停止"; Filename: "{app}\stop.bat"; WorkingDir: "{app}"; IconFilename: "{app}\route\static\favicon.ico"; Tasks: startmenuicon
Name: "{group}\アンインストール"; Filename: "{uninstallexe}"; Tasks: startmenuicon

[Run]
; Optionally launch after install
Filename: "{app}\{#MyAppExeName}"; Description: "Route294 を起動する"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent shellexec

[UninstallRun]
; Stop server before uninstall
Filename: "{app}\stop.bat"; Flags: runhidden waituntilterminated

[UninstallDelete]
Type: filesandordirs; Name: "{app}\route\logs"
Type: filesandordirs; Name: "{app}\route\media"
Type: filesandordirs; Name: "{app}\route\db.sqlite3"
Type: filesandordirs; Name: "{app}\route\__pycache__"
Type: filesandordirs; Name: "{app}\python\Lib\site-packages\__pycache__"

[Messages]
WelcomeLabel2=Route294（ホテル清掃指示書作成システム）をインストールします。%n%nこのソフトウェアはローカルWebサーバーとして動作します。%nインストール後、デスクトップのショートカットからワンクリックで起動できます。

