# Mac Installation (5 minutes)

## 1. Build the workbook

```bash
cd gst-excel-utility
./build.sh
```

## 2. Import macros into Excel

1. Open `output/GST_Auto_Login_Utility.xlsx` in **Microsoft Excel for Mac**.
2. Press **Option + F11** (VBA Editor).
3. **File → Import File…** → choose `vba/GST_Utility_AllInOne.bas`.
4. In the Project panel, double-click **ThisWorkbook** and paste:

```vba
Private Sub Workbook_Open()
    On Error Resume Next
    InitializeUtility
End Sub
```

5. Close the VBA editor.

## 3. Add macro buttons (Dashboard sheet)

1. Go to **Dashboard**.
2. **Developer → Button** (Form Control).
3. Draw a button over cell **B23**, assign macro **AutoLoginSelectedClient**, label it **Auto Login**.
4. Repeat for:

| Cell | Macro | Button label |
|------|-------|--------------|
| C23 | CopyPasswordForSelectedClient | Copy Password |
| D23 | CheckReturnStatusSelectedClient | Check Status |
| E23 | CheckReturnStatusAllClients | Check All |
| B24 | RefreshClientDashboard | Refresh |
| C24 | ExportClientDataToExcel | Export Data |
| D24 | ExportCredentialsSheet | Export Credentials |
| E24 | OpenReturnStatusOnPortal | Portal Status |

> If **Developer** tab is hidden: Excel → Preferences → Ribbon → check **Developer**.

## 4. Save as macro-enabled workbook

**File → Save As → Format: Excel Macro-Enabled Workbook (.xlsm)**

Recommended name: `GST_Auto_Login_Utility.xlsm`

## 5. Enable macros

Excel → **Preferences → Security →** enable macros (or prompt on open).

## Usage tips

- Set **Selected Client Row** on Dashboard to the row number in **Client Master** (e.g. `5` for first client).
- Choose **Financial Year** from dropdown: `2026-27` or `2027-28`.
- GST portal CAPTCHA/OTP must be completed manually after **Auto Login**.
