Attribute VB_Name = "GSTUtility"
' GST Auto Login Excel Utility — single-module build for easy Mac import
' Import this ONE file in Excel VBA editor (Option+F11 → File → Import File)
Option Explicit

' === Constants ===
Private Const APP_NAME As String = "GST Auto Login Utility"
Private Const GST_LOGIN_URL As String = "https://services.gst.gov.in/services/login"
Private Const GST_HOME_URL As String = "https://www.gst.gov.in/"
Private Const GST_RETURN_STATUS_URL As String = "https://services.gst.gov.in/services/auth/searchtp"
Private Const GST_TP_SEARCH_URL As String = "https://services.gst.gov.in/services/api/search/tp"
Private Const SHEET_DASHBOARD As String = "Dashboard"
Private Const SHEET_CLIENTS As String = "Client Master"
Private Const SHEET_STATUS As String = "Return Status"
Private Const FY_2026_27 As String = "2026-27"
Private Const FY_2027_28 As String = "2027-28"
Private Const COL_CLIENT_ID As Long = 1
Private Const COL_CLIENT_NAME As Long = 2
Private Const COL_GSTIN As Long = 3
Private Const COL_USERNAME As Long = 4
Private Const COL_PASSWORD As Long = 5
Private Const COL_EMAIL As Long = 6
Private Const COL_CONTACT As Long = 7
Private Const COL_FILER_TYPE As Long = 8
Private Const COL_ACTIVE As Long = 9
Private Const COL_LAST_LOGIN As Long = 10
Private Const COL_NOTES As Long = 11
Private Const CLIENT_HEADER_ROW As Long = 4
Private Const CLIENT_FIRST_DATA_ROW As Long = 5

' === Workbook open (paste same code into ThisWorkbook module) ===
' Private Sub Workbook_Open()
'     On Error Resume Next
'     InitializeUtility
' End Sub

Public Sub InitializeUtility()
    Dim wsDash As Worksheet
    Set wsDash = ThisWorkbook.Worksheets(SHEET_DASHBOARD)
    If Trim$(CStr(wsDash.Range("FY_Selected").Value)) = "" Then wsDash.Range("FY_Selected").Value = FY_2026_27
    If Trim$(CStr(wsDash.Range("Selected_Client_Row").Value)) = "" Then wsDash.Range("Selected_Client_Row").Value = CLIENT_FIRST_DATA_ROW
    wsDash.Range("App_Status").Value = "Ready"
    RefreshClientDashboard
End Sub

Public Sub RefreshClientDashboard()
    Dim wsDash As Worksheet, wsClients As Worksheet, lastRow As Long, r As Long, outRow As Long
    Set wsDash = ThisWorkbook.Worksheets(SHEET_DASHBOARD)
    Set wsClients = ThisWorkbook.Worksheets(SHEET_CLIENTS)
    lastRow = wsClients.Cells(wsClients.Rows.Count, COL_GSTIN).End(xlUp).Row
    If lastRow < CLIENT_FIRST_DATA_ROW Then lastRow = CLIENT_FIRST_DATA_ROW
    wsDash.Range("Client_List").ClearContents
    outRow = 1
    For r = CLIENT_FIRST_DATA_ROW To lastRow
        If Trim$(CStr(wsClients.Cells(r, COL_GSTIN).Value)) <> "" Then
            wsDash.Cells(outRow + 11, 2).Value = wsClients.Cells(r, COL_CLIENT_ID).Value
            wsDash.Cells(outRow + 11, 3).Value = wsClients.Cells(r, COL_CLIENT_NAME).Value
            wsDash.Cells(outRow + 11, 4).Value = wsClients.Cells(r, COL_GSTIN).Value
            wsDash.Cells(outRow + 11, 5).Value = wsClients.Cells(r, COL_EMAIL).Value
            wsDash.Cells(outRow + 11, 6).Value = wsClients.Cells(r, COL_CONTACT).Value
            wsDash.Cells(outRow + 11, 7).Value = wsClients.Cells(r, COL_FILER_TYPE).Value
            wsDash.Cells(outRow + 11, 8).Value = wsClients.Cells(r, COL_ACTIVE).Value
            outRow = outRow + 1
        End If
    Next r
    wsDash.Range("Client_Count").Value = outRow - 1
    wsDash.Range("Last_Refresh").Value = Now
    MsgBox "Client dashboard refreshed. " & (outRow - 1) & " client(s) listed.", vbInformation, APP_NAME
End Sub

Public Sub AutoLoginSelectedClient()
    AutoLoginClientRow SelectedClientRow
End Sub

Public Sub AutoLoginClientRow(ByVal rowNum As Long)
    Dim username As String, password As String, gstin As String, clientName As String
    username = GetClientField(rowNum, COL_USERNAME)
    gstin = GetClientField(rowNum, COL_GSTIN)
    clientName = GetClientField(rowNum, COL_CLIENT_NAME)
    If gstin = "" Then MsgBox "No GSTIN found on row " & rowNum, vbExclamation, APP_NAME: Exit Sub
    If Not ValidateGSTIN(gstin) Then MsgBox "GSTIN format looks invalid: " & gstin, vbExclamation, APP_NAME
    If username = "" Then MsgBox "Username is empty for " & clientName, vbExclamation, APP_NAME: Exit Sub
    SetClipboardText username
    OpenUrl GST_LOGIN_URL
    MarkClientLogin rowNum
    MsgBox "GST login opened." & vbCrLf & "Client: " & clientName & vbCrLf & "GSTIN: " & gstin & vbCrLf & "Username copied — complete CAPTCHA/OTP on portal.", vbInformation, APP_NAME
End Sub

Public Sub CopyPasswordForSelectedClient()
    Dim password As String
    password = GetClientField(SelectedClientRow, COL_PASSWORD)
    If password = "" Then MsgBox "No password stored.", vbExclamation, APP_NAME: Exit Sub
    SetClipboardText password
    MsgBox "Password copied to clipboard.", vbInformation, APP_NAME
End Sub

Public Sub CheckReturnStatusSelectedClient()
    CheckReturnStatusForRow SelectedClientRow, True
End Sub

Public Sub CheckReturnStatusAllClients()
    Dim wsClients As Worksheet, lastRow As Long, r As Long
    Set wsClients = ThisWorkbook.Worksheets(SHEET_CLIENTS)
    lastRow = wsClients.Cells(wsClients.Rows.Count, COL_GSTIN).End(xlUp).Row
    ThisWorkbook.Worksheets(SHEET_STATUS).Range("Status_Data").ClearContents
    Application.ScreenUpdating = False
    For r = CLIENT_FIRST_DATA_ROW To lastRow
        If Trim$(GetClientField(r, COL_GSTIN)) <> "" And UCase$(GetClientField(r, COL_ACTIVE)) <> "NO" Then
            CheckReturnStatusForRow r, False
            DoEvents
        End If
    Next r
    Application.ScreenUpdating = True
    MsgBox "Return status check completed for FY " & SelectedFinancialYear & ".", vbInformation, APP_NAME
End Sub

Private Sub CheckReturnStatusForRow(ByVal rowNum As Long, ByVal showMsg As Boolean)
    Dim wsStatus As Worksheet, fy As String, gstin As String, clientName As String, tpJson As String, legalName As String, outRow As Long
    gstin = GetClientField(rowNum, COL_GSTIN)
    clientName = GetClientField(rowNum, COL_CLIENT_NAME)
    fy = SelectedFinancialYear
    If gstin = "" Then Exit Sub
    Set wsStatus = ThisWorkbook.Worksheets(SHEET_STATUS)
    wsStatus.Range("FY_Display").Value = fy
    wsStatus.Range("Status_Last_Check").Value = Now
    outRow = wsStatus.Cells(wsStatus.Rows.Count, 1).End(xlUp).Row + 1
    If outRow < 6 Then outRow = 6
    tpJson = CurlGet(GST_TP_SEARCH_URL & "?gstin=" & gstin)
    legalName = JsonValue(tpJson, "lgnm")
    If legalName = "" Then legalName = JsonValue(tpJson, "tradeNam")
    WriteStatusRow wsStatus, outRow, clientName, gstin, fy, tpJson, legalName
    If showMsg Then MsgBox "Status updated for " & clientName, vbInformation, APP_NAME
End Sub

Private Sub WriteStatusRow(ByVal ws As Worksheet, ByVal outRow As Long, ByVal clientName As String, ByVal gstin As String, ByVal fy As String, ByVal tpJson As String, ByVal legalName As String)
    Dim filingJson As String, gstr1 As String, gstr3b As String
    ws.Cells(outRow, 1).Value = clientName
    ws.Cells(outRow, 2).Value = gstin
    ws.Cells(outRow, 3).Value = legalName
    ws.Cells(outRow, 4).Value = fy
    If tpJson = "" Then
        ws.Cells(outRow, 5).Value = "Offline"
        ws.Cells(outRow, 6).Value = "Check portal"
        ws.Cells(outRow, 7).Value = "Check portal"
    Else
        ws.Cells(outRow, 5).Value = JsonValue(tpJson, "sts")
        filingJson = CurlPostJson("https://services.gst.gov.in/services/api/search/taxpayerReturnDetails", "{""gstin"":""" & gstin & """,""fy"":""" & fy & """}")
        gstr1 = ParseReturnStatus(filingJson, "GSTR1")
        gstr3b = ParseReturnStatus(filingJson, "GSTR3B")
        ws.Cells(outRow, 6).Value = IIf(gstr1 = "", "Verify on portal", gstr1)
        ws.Cells(outRow, 7).Value = IIf(gstr3b = "", "Verify on portal", gstr3b)
    End If
    ws.Cells(outRow, 8).Value = Format$(Now, "dd-mmm-yyyy hh:nn")
End Sub

Public Sub ExportClientDataToExcel()
    Dim exportPath As String, newWb As Workbook, srcWs As Worksheet, lastRow As Long
    Set srcWs = ThisWorkbook.Worksheets(SHEET_CLIENTS)
    lastRow = srcWs.Cells(srcWs.Rows.Count, COL_GSTIN).End(xlUp).Row
    If lastRow < CLIENT_FIRST_DATA_ROW Then MsgBox "No data to export.", vbExclamation, APP_NAME: Exit Sub
    exportPath = DesktopPath() & Application.PathSeparator & "GST_Clients_Export_" & Format$(Now, "yyyymmdd_hhnnss") & ".xlsx"
    Set newWb = Workbooks.Add(xlWBATWorksheet)
    srcWs.Range("A" & CLIENT_HEADER_ROW & ":K" & lastRow).Copy Destination:=newWb.Worksheets(1).Range("A1")
    Application.CutCopyMode = False
    newWb.SaveAs exportPath, xlOpenXMLWorkbook
    newWb.Close False
    MsgBox "Exported to:" & vbCrLf & exportPath, vbInformation, APP_NAME
End Sub

Public Sub ExportCredentialsSheet()
    Dim exportPath As String, newWb As Workbook, srcWs As Worksheet, dstWs As Worksheet, lastRow As Long, r As Long, outR As Long
    Set srcWs = ThisWorkbook.Worksheets(SHEET_CLIENTS)
    lastRow = srcWs.Cells(srcWs.Rows.Count, COL_GSTIN).End(xlUp).Row
    If lastRow < CLIENT_FIRST_DATA_ROW Then MsgBox "No credentials to export.", vbExclamation, APP_NAME: Exit Sub
    exportPath = DesktopPath() & Application.PathSeparator & "GST_Login_Credentials_" & Format$(Now, "yyyymmdd_hhnnss") & ".xlsx"
    Set newWb = Workbooks.Add(xlWBATWorksheet)
    Set dstWs = newWb.Worksheets(1)
    dstWs.Range("A1:E1").Value = Array("Client ID", "Client Name", "GSTIN", "Username", "Password")
    outR = 2
    For r = CLIENT_FIRST_DATA_ROW To lastRow
        If Trim$(GetClientField(r, COL_GSTIN)) <> "" Then
            dstWs.Cells(outR, 1).Value = srcWs.Cells(r, COL_CLIENT_ID).Value
            dstWs.Cells(outR, 2).Value = srcWs.Cells(r, COL_CLIENT_NAME).Value
            dstWs.Cells(outR, 3).Value = srcWs.Cells(r, COL_GSTIN).Value
            dstWs.Cells(outR, 4).Value = srcWs.Cells(r, COL_USERNAME).Value
            dstWs.Cells(outR, 5).Value = srcWs.Cells(r, COL_PASSWORD).Value
            outR = outR + 1
        End If
    Next r
    newWb.SaveAs exportPath, xlOpenXMLWorkbook
    newWb.Close False
    MsgBox "Credentials exported. Store securely:" & vbCrLf & exportPath, vbInformation, APP_NAME
End Sub

Public Sub OpenReturnStatusOnPortal()
    Dim gstin As String
    gstin = GetClientField(SelectedClientRow, COL_GSTIN)
    If gstin = "" Then MsgBox "Select a client with GSTIN first.", vbExclamation, APP_NAME: Exit Sub
    OpenUrl GST_RETURN_STATUS_URL
    SetClipboardText gstin
    MsgBox "Portal opened. GSTIN copied.", vbInformation, APP_NAME
End Sub

Public Sub SetFinancialYear2026_27()
    ThisWorkbook.Worksheets(SHEET_DASHBOARD).Range("FY_Selected").Value = FY_2026_27
End Sub

Public Sub SetFinancialYear2027_28()
    ThisWorkbook.Worksheets(SHEET_DASHBOARD).Range("FY_Selected").Value = FY_2027_28
End Sub

Private Function GetClientField(ByVal rowNum As Long, ByVal colNum As Long) As String
    GetClientField = Trim$(CStr(ThisWorkbook.Worksheets(SHEET_CLIENTS).Cells(rowNum, colNum).Value))
End Function

Private Sub MarkClientLogin(ByVal rowNum As Long)
    ThisWorkbook.Worksheets(SHEET_CLIENTS).Cells(rowNum, COL_LAST_LOGIN).Value = Now
End Sub

Private Function SelectedFinancialYear() As String
    SelectedFinancialYear = Trim$(CStr(ThisWorkbook.Worksheets(SHEET_DASHBOARD).Range("FY_Selected").Value))
    If SelectedFinancialYear = "" Then SelectedFinancialYear = FY_2026_27
End Function

Private Function SelectedClientRow() As Long
    Dim n As Long
    n = CLng(Val(ThisWorkbook.Worksheets(SHEET_DASHBOARD).Range("Selected_Client_Row").Value))
    If n < CLIENT_FIRST_DATA_ROW Then n = CLIENT_FIRST_DATA_ROW
    SelectedClientRow = n
End Function

Private Function ValidateGSTIN(ByVal gstin As String) As Boolean
    Dim cleaned As String
    cleaned = UCase$(Trim$(gstin))
    If Len(cleaned) <> 15 Then Exit Function
    ValidateGSTIN = (cleaned Like "[0-9][0-9][A-Z][A-Z][A-Z][A-Z][A-Z][0-9][0-9][A-Z][0-9][Z][A-Z0-9][A-Z0-9]")
End Function

Private Function ParseReturnStatus(ByVal jsonText As String, ByVal returnType As String) As String
    Dim pos As Long, slice As String, statusVal As String, dofVal As String
    If jsonText = "" Then Exit Function
    pos = InStr(1, jsonText, """rtntype"":""" & returnType & """", vbTextCompare)
    If pos = 0 Then Exit Function
    slice = Mid$(jsonText, pos, 250)
    statusVal = JsonValue(slice, "status")
    dofVal = JsonValue(slice, "dof")
    If dofVal <> "" Then ParseReturnStatus = statusVal & " (" & dofVal & ")" Else ParseReturnStatus = statusVal
End Function

Private Function JsonValue(ByVal jsonText As String, ByVal key As String) As String
    Dim pattern As String, startPos As Long, endPos As Long, ch As String, escaped As Boolean
    pattern = """" & key & """:"""
    startPos = InStr(1, jsonText, pattern, vbTextCompare)
    If startPos = 0 Then Exit Function
    startPos = startPos + Len(pattern)
    For endPos = startPos To Len(jsonText)
        ch = Mid$(jsonText, endPos, 1)
        If escaped Then escaped = False ElseIf ch = "\" Then escaped = True ElseIf ch = """" Then
            JsonValue = Mid$(jsonText, startPos, endPos - startPos)
            JsonValue = Replace(JsonValue, "\""", """")
            Exit Function
        End If
    Next endPos
End Function

#If Mac Then
Private Function CurlGet(ByVal url As String) As String
    On Error GoTo Fail
    CurlGet = MacScript("do shell script ""curl -sS -L --max-time 45 -H 'Accept: application/json' -H 'User-Agent: Mozilla/5.0' '" & Replace(url, "'", "'\''") & "'""")
    Exit Function
Fail: CurlGet = ""
End Function
Private Function CurlPostJson(ByVal url As String, ByVal jsonBody As String) As String
    On Error GoTo Fail
    Dim b As String: b = Replace(Replace(jsonBody, "'", "'\''"), """", "\""")
    CurlPostJson = MacScript("do shell script ""curl -sS -L --max-time 45 -X POST -H 'Content-Type: application/json' -d '" & b & "' '" & Replace(url, "'", "'\''") & "'""")
    Exit Function
Fail: CurlPostJson = ""
End Function
Private Sub OpenUrl(ByVal url As String)
    On Error Resume Next
    MacScript "do shell script ""open '" & Replace(url, "'", "'\''") & "'"""
End Sub
Private Sub SetClipboardText(ByVal value As String)
    On Error Resume Next
    MacScript "set the clipboard to """ & Replace(value, """", "\""") & """"
End Sub
Private Function DesktopPath() As String
    DesktopPath = MacScript("return POSIX path of (path to desktop folder)")
End Function
#Else
Private Function CurlGet(ByVal url As String) As String
    On Error GoTo Fail
    Dim http As Object: Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    http.Open "GET", url, False: http.setRequestHeader "Accept", "application/json": http.send
    If http.Status = 200 Then CurlGet = http.responseText
    Exit Function
Fail: CurlGet = ""
End Function
Private Function CurlPostJson(ByVal url As String, ByVal jsonBody As String) As String
    On Error GoTo Fail
    Dim http As Object: Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    http.Open "POST", url, False: http.setRequestHeader "Content-Type", "application/json": http.send jsonBody
    If http.Status = 200 Then CurlPostJson = http.responseText
    Exit Function
Fail: CurlPostJson = ""
End Function
Private Sub OpenUrl(ByVal url As String)
    CreateObject("WScript.Shell").Run url, 1, False
End Sub
Private Sub SetClipboardText(ByVal value As String)
    Dim d As Object: Set d = CreateObject("MSForms.DataObject"): d.SetText value: d.PutInClipboard
End Sub
Private Function DesktopPath() As String
    DesktopPath = Environ$("USERPROFILE") & "\Desktop"
End Function
#End If
