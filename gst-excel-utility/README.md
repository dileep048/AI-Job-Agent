# GST Auto Login Excel Utility (Mac)

Excel macro utility for Indian tax professionals to manage multiple GST clients, open the GST portal quickly, check return status hints, and export client data.

## Features

- One-click GST portal login helper (opens portal + copies username)
- Client Master dashboard (Name, GSTIN, Email, Contact, filer type)
- Return status checker (GSTR-1 & GSTR-3B hints via public GST services)
- Export client data and login credentials to `.xlsx`
- Financial year selection: **2026-27** and **2027-28**
- Monthly / quarterly filer tracking

## Requirements

- **Microsoft Excel for Mac** (Office 2016 or later)
- macOS with network access to `gst.gov.in`
- Excel setting: **Preferences → Security → Enable macros** (or prompt)
- Excel setting: **Preferences → Security → Trust access to the VBA project object model** (needed for automated build only)

## Build

```bash
cd gst-excel-utility
chmod +x build.sh
./build.sh
```

Outputs:

- `output/GST_Auto_Login_Utility.xlsx` — workbook structure (sheets, sample clients, dashboard)
- `vba/GST_Utility_AllInOne.bas` — all VBA macros (single import for Mac)

After import, save as **`.xlsm`** (macros are not stored in plain `.xlsx`). See [INSTALL_MAC.md](INSTALL_MAC.md).

## Manual VBA import (if build script cannot inject macros)

1. Open `output/GST_Auto_Login_Utility.xlsx` (if fallback was created) or create a new workbook and copy sheet structure from the build output.
2. Press `Option + F11` to open the VBA editor.
3. **File → Import File…** and import every file from `vba/`.
4. In `ThisWorkbook`, add:

```vba
Private Sub Workbook_Open()
    On Error Resume Next
    InitializeUtility
End Sub
```

5. Save as **Excel Macro-Enabled Workbook** (`.xlsm`).
6. On the Dashboard sheet, insert form buttons and assign macros listed in cells B23:E24.

## Usage

1. Open `GST_Auto_Login_Utility.xlsm` and enable macros.
2. Edit **Client Master** with real client rows.
3. On **Dashboard**, choose financial year and set **Selected Client Row** to the client’s row number in Client Master.
4. Click **Auto Login** — GST login opens; username is on the clipboard. Use **Copy Password** as needed.
5. Click **Check Status** or **Check All Status** for online status hints.
6. Use **Export Data** / **Export Credentials** for Excel backups.

## Important limitations

- GST portal CAPTCHA and OTP cannot be automated; login still needs manual verification.
- Return status uses public GST endpoints and should be verified on the official portal before compliance decisions.
- Store exported credential files securely.

## File layout

```text
gst-excel-utility/
├── build/build_workbook.py
├── build.sh
├── vba/                 # VBA source modules
├── output/              # Built workbook
└── README.md
```
