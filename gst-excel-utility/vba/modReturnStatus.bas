Attribute VB_Name = "modReturnStatus"
Option Explicit

Private Type ReturnRecord
    ReturnType As String
    Period As String
    Status As String
    DateOfFiling As String
    Arn As String
End Type

Public Sub CheckReturnStatusAllClients()
    Dim wsClients As Worksheet
    Dim wsStatus As Worksheet
    Dim lastRow As Long
    Dim r As Long
    Dim outRow As Long
    Dim fy As String
    Dim gstin As String
    Dim clientName As String
    Dim tpJson As String
    Dim legalName As String

    Set wsClients = ThisWorkbook.Worksheets(SHEET_CLIENTS)
    Set wsStatus = ThisWorkbook.Worksheets(SHEET_STATUS)
    fy = SelectedFinancialYear

    wsStatus.Range("Status_Data").ClearContents
    wsStatus.Range("FY_Display").Value = fy
    wsStatus.Range("Status_Last_Check").Value = Now

    lastRow = wsClients.Cells(wsClients.Rows.Count, COL_GSTIN).End(xlUp).Row
    outRow = 6

    Application.ScreenUpdating = False
    For r = CLIENT_FIRST_DATA_ROW To lastRow
        gstin = GetClientField(r, COL_GSTIN)
        clientName = GetClientField(r, COL_CLIENT_NAME)
        If gstin <> "" And UCase$(GetClientField(r, COL_ACTIVE)) <> "NO" Then
            tpJson = CurlGet(GST_TP_SEARCH_URL & "?gstin=" & gstin)
            legalName = JsonValue(tpJson, "lgnm")
            If legalName = "" Then legalName = JsonValue(tpJson, "tradeNam")

            WriteStatusSummary wsStatus, outRow, clientName, gstin, fy, tpJson, legalName
            outRow = outRow + 1
            DoEvents
        End If
    Next r
    Application.ScreenUpdating = True

    MsgBox "Return status check completed for financial year " & fy & ".", vbInformation, APP_NAME
End Sub

Public Sub CheckReturnStatusSelectedClient()
    Dim rowNum As Long
    Dim wsStatus As Worksheet
    Dim fy As String
    Dim gstin As String
    Dim clientName As String
    Dim tpJson As String
    Dim legalName As String

    rowNum = SelectedClientRow
    gstin = GetClientField(rowNum, COL_GSTIN)
    clientName = GetClientField(rowNum, COL_CLIENT_NAME)
    fy = SelectedFinancialYear

    If gstin = "" Then
        MsgBox "No GSTIN on selected row.", vbExclamation, APP_NAME
        Exit Sub
    End If

    Set wsStatus = ThisWorkbook.Worksheets(SHEET_STATUS)
    wsStatus.Range("Status_Data").ClearContents
    wsStatus.Range("FY_Display").Value = fy
    wsStatus.Range("Status_Last_Check").Value = Now

    tpJson = CurlGet(GST_TP_SEARCH_URL & "?gstin=" & gstin)
    legalName = JsonValue(tpJson, "lgnm")
    If legalName = "" Then legalName = JsonValue(tpJson, "tradeNam")

    WriteStatusSummary wsStatus, 6, clientName, gstin, fy, tpJson, legalName
    MsgBox "Status updated for " & clientName & " (" & gstin & ").", vbInformation, APP_NAME
End Sub

Private Sub WriteStatusSummary(ByVal ws As Worksheet, ByVal outRow As Long, _
    ByVal clientName As String, ByVal gstin As String, ByVal fy As String, _
    ByVal tpJson As String, ByVal legalName As String)

    Dim statusText As String
    Dim gstr1Status As String
    Dim gstr3bStatus As String
    Dim filingJson As String

    ws.Cells(outRow, 1).Value = clientName
    ws.Cells(outRow, 2).Value = gstin
    ws.Cells(outRow, 3).Value = legalName
    ws.Cells(outRow, 4).Value = fy

    If tpJson = "" Then
        ws.Cells(outRow, 5).Value = "Offline / No response"
        ws.Cells(outRow, 6).Value = "Check manually"
        ws.Cells(outRow, 7).Value = "Check manually"
        ws.Cells(outRow, 8).Value = "Open portal"
        Exit Sub
    End If

    statusText = JsonValue(tpJson, "sts")
    If statusText = "" Then statusText = "Unknown"
    ws.Cells(outRow, 5).Value = statusText

    filingJson = FetchReturnFilingHints(gstin, fy)
    gstr1Status = ParseLatestReturnStatus(filingJson, "GSTR1")
    gstr3bStatus = ParseLatestReturnStatus(filingJson, "GSTR3B")

    If gstr1Status = "" Then gstr1Status = InferReturnStatusFromTaxpayer(tpJson, "GSTR-1")
    If gstr3bStatus = "" Then gstr3bStatus = InferReturnStatusFromTaxpayer(tpJson, "GSTR-3B")

    ws.Cells(outRow, 6).Value = gstr1Status
    ws.Cells(outRow, 7).Value = gstr3bStatus
    ws.Cells(outRow, 8).Value = Format$(Now, "dd-mmm-yyyy hh:nn")
End Sub

Private Function FetchReturnFilingHints(ByVal gstin As String, ByVal fy As String) As String
    Dim body As String
    body = "{""gstin"":""" & gstin & """,""fy"":""" & fy & """}"
    FetchReturnFilingHints = CurlPostJson("https://services.gst.gov.in/services/api/search/taxpayerReturnDetails", body)
    If FetchReturnFilingHints = "" Then
        FetchReturnFilingHints = CurlGet("https://publicservices.gst.gov.in/publicservices/auth/api/search/taxpayerReturnDetails?gstin=" & gstin & "&fy=" & fy)
    End If
End Function

Private Function ParseLatestReturnStatus(ByVal jsonText As String, ByVal returnType As String) As String
    Dim searchKey As String
    Dim pos As Long
    Dim slice As String
    Dim statusVal As String
    Dim dofVal As String

    If jsonText = "" Then Exit Function
    searchKey = """rtntype"":""" & returnType & """"
    pos = InStr(1, jsonText, searchKey, vbTextCompare)
    If pos = 0 Then Exit Function

    slice = Mid$(jsonText, pos, 250)
    statusVal = JsonValue(slice, "status")
    dofVal = JsonValue(slice, "dof")
    If statusVal = "" And dofVal = "" Then Exit Function
    If dofVal <> "" Then
        ParseLatestReturnStatus = statusVal & " (" & dofVal & ")"
    Else
        ParseLatestReturnStatus = statusVal
    End If
End Function

Private Function InferReturnStatusFromTaxpayer(ByVal tpJson As String, ByVal returnLabel As String) As String
    If InStr(1, tpJson, "error", vbTextCompare) > 0 Then
        InferReturnStatusFromTaxpayer = "Verify on portal"
        Exit Function
    End If
    InferReturnStatusFromTaxpayer = "Use portal checker"
End Function

Public Sub OpenReturnStatusOnPortal()
    Dim gstin As String
    gstin = GetClientField(SelectedClientRow, COL_GSTIN)
    If gstin = "" Then
        MsgBox "Select a client with a valid GSTIN first.", vbExclamation, APP_NAME
        Exit Sub
    End If
    OpenUrl GST_RETURN_STATUS_URL
    SetClipboardText gstin
    MsgBox "Return status page opened. GSTIN copied to clipboard.", vbInformation, APP_NAME
End Sub
