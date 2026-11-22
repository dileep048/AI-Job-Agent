Attribute VB_Name = "modDashboard"
Option Explicit

Public Sub InitializeUtility()
    Dim wsDash As Worksheet
    Set wsDash = ThisWorkbook.Worksheets(SHEET_DASHBOARD)
    If Trim$(CStr(wsDash.Range("FY_Selected").Value)) = "" Then
        wsDash.Range("FY_Selected").Value = FY_2026_27
    End If
    If Trim$(CStr(wsDash.Range("Selected_Client_Row").Value)) = "" Then
        wsDash.Range("Selected_Client_Row").Value = CLIENT_FIRST_DATA_ROW
    End If
    wsDash.Range("App_Status").Value = "Ready"
    RefreshClientDashboard
End Sub

Public Sub SetFinancialYear2026_27()
    ThisWorkbook.Worksheets(SHEET_DASHBOARD).Range("FY_Selected").Value = FY_2026_27
    MsgBox "Financial year set to 2026-27.", vbInformation, APP_NAME
End Sub

Public Sub SetFinancialYear2027_28()
    ThisWorkbook.Worksheets(SHEET_DASHBOARD).Range("FY_Selected").Value = FY_2027_28
    MsgBox "Financial year set to 2027-28.", vbInformation, APP_NAME
End Sub

Public Sub ShowHelp()
    ThisWorkbook.Worksheets(SHEET_HELP).Activate
End Sub

Public Sub ProtectPasswordColumn()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets(SHEET_CLIENTS)
    On Error Resume Next
    ws.Unprotect Password:=GetSheetPassword()
    ws.Columns(COL_PASSWORD).Hidden = True
    ws.Protect Password:=GetSheetPassword(), UserInterfaceOnly:=True
    MsgBox "Password column hidden. Unhide from Excel Format menu if needed.", vbInformation, APP_NAME
End Sub

Public Function GetSheetPassword() As String
    GetSheetPassword = "gstutility"
End Function
