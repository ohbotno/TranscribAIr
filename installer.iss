; Inno Setup Script for TranscribAIr
; Requires Inno Setup 6.0 or later: https://jrsoftware.org/isinfo.php
;
; To build the installer:
; 1. Build the executable first: python build.py
; 2. Install Inno Setup from https://jrsoftware.org/isinfo.php
; 3. Compile this script with Inno Setup Compiler
;
; The installer will be created in the Output directory

#define MyAppName "TranscribAIr"
#define MyAppVersion "1.0.5"
#define MyAppPublisher "Swansea University"
#define MyAppURL "https://github.com/otherworld-dev/TranscribAIr"
#define MyAppExeName "Transcribair.exe"
#define MyAppDescription "AI-powered audio transcription and feedback organization tool"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=Output
OutputBaseFilename=TranscribAIr-{#MyAppVersion}-Setup
SetupIconFile=dist\{#MyAppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoDescription={#MyAppDescription}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Include all files from dist folder
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Name: "{group}\README"; Filename: "{app}\README.md"
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\.transcribair"

[Code]
// Custom messages and functions can be added here

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Check for .NET Framework or other dependencies here if needed
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    // Show information about user data location
    MsgBox('TranscribAIr stores settings, models, and recordings in:' + #13#10 +
           ExpandConstant('{userappdata}') + '\.transcribair' + #13#10 + #13#10 +
           'This data will be preserved during updates and only deleted if you check "Delete user data" during uninstall.',
           mbInformation, MB_OK);
  end;
end;

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%n[name] is an AI-powered audio transcription and feedback organization tool designed for educators.%n%nIt is recommended that you close all other applications before continuing.
