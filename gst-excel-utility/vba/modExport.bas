Attribute VB_Name = "modExport"
Option Explicit

Public Sub ExportClientDataToExcel()
    Dim exportPath As String
    Dim fileName As String
    Dim newWb As Workbook
    Dim srcWs As Worksheet
    Dim dstWs As Worksheet
    Dim lastRow As Long

    Set srcWs = ThisWorkbook.Worksheets(SHEET_CLIENTS)
    lastRow = srcWs.Cells(srcWs.Rows.Count, COL_GSTIN).End(xlUp).Row
    If lastRow < CLIENT_FIRST_DATA_ROW Then
        MsgBox "No client data to export.", vbExclamation, APP_NAME
        Exit Sub
    End If

    fileName = "GST_Clients_Export_" & Format$(Now, "yyyymmdd_hhnnss") & ".xlsx"
    exportPath = ThisWorkbook.Path
    If exportPath = "" Then exportPath = MacDesktopPath()
    exportPath = exportPath & Application.PathSeparator & fileName

    Set newWb = Workbooks.Add(xlWBATWorksheet)
    Set dstWs = newWb.Worksheets(1)
    dstWs.Name = "Client Export"

    srcWs.Range("A" & CLIENT_HEADER_ROW & ":K" & lastRow).Copy Destination:=dstWs.Range("A1")
    Application.CutCopyMode = False

    dstWs.Columns("A:K").AutoFit
    newWb.SaveAs Filename:=exportPath, FileFormat:=xlOpenXMLWorkbook
    newWb.Close SaveChanges:=False

    MsgBox "Client data exported to:" & vbCrLf & exportPath, vbInformation, APP_NAME
End Sub

Public Sub ExportCredentialsSheet()
    Dim exportPath As String
    Dim fileName As String
    Dim newWb As Workbook
    Dim srcWs As Worksheet
    Dim dstWs As Worksheet
    Dim lastRow As Long
    Dim r As Long

    Set srcWs = ThisWorkbook.Worksheets(SHEET_CLIENTS)
    lastRow = srcWs.Cells(srcWs.Rows.Count, COL_GSTIN).End(xlUp).Row
    If lastRow < CLIENT_FIRST_DATA_ROW Then
        MsgBox "No credentials to export.", vbExclamation, APP_NAME
        Exit Sub
    End If

    fileName = "GST_Login_Credentials_" & Format$(Now, "yyyymmdd_hhnnss") & ".xlsx"
    exportPath = ThisWorkbook.Path
    If exportPath = "" Then exportPath = MacDesktopPath()
    exportPath = exportPath & Application.PathSeparator & fileName

    Set newWb = Workbooks.Add(xlWBATWorksheet)
    Set dstWs = newWb.Worksheets(1)
    dstWs.Name = "Login Credentials"

    dstWs.Range("A1:E1").Value = Array("Client ID", "Client Name", "GSTIN", "Username", "Password")
    For r = CLIENT_FIRST_DATA_ROW To lastRow
        If Trim$(CStr(srcWs.Cells(r, COL_GSTIN).Value)) <> "" Then
            dstWs.Cells(r - CLIENT_HEADER_ROW + 1, 1).Value = srcWs.Cells(r, COL_CLIENT_ID).Value
            dstWs.Cells(r - CLIENT_HEADER_ROW + 1, 2).Value = srcWs.Cells(r, COL_CLIENT_NAME).Value
            dstWs.Cells(r - CLIENT_HEADER_ROW + 1, 3).Value = srcWs.Cells(r, COL_GSTIN).Value
            dstWs.Cells(r - CLIENT_HEADER_ROW + 1, 4).Value = srcWs.Cells(r, COL_USERNAME).Value
            dstWs.Cells(r - CLIENT_HEADER_ROW + 1, 5).Value = srcWs.Cells(r, COL_PASSWORD).Value
        End If
    Next r

    dstWs.Columns("A:E").AutoFit
    newWb.SaveAs Filename:=exportPath, FileFormat:=xlOpenXMLWorkbook
    newWb.Close SaveChanges:=False

    MsgBox "Login credentials exported to:" & vbCrLf & exportPath & vbCrLf & vbCrLf & _
           "Store this file securely.", vbInformation, APP_NAME
End Sub

Private Function MacDesktopPath() As String
    #If Mac Then
        MacDesktopPath = MacScript("return POSIX path of (path to desktop folder)")
    #Else
        MacDesktopPath = Environ$("USERPROFILE") & "\Desktop"
    #End If
End Function
