Attribute VB_Name = "modClientMaster"
Option Explicit

Public Sub RefreshClientDashboard()
    Dim wsDash As Worksheet
    Dim wsClients As Worksheet
    Dim lastRow As Long
    Dim r As Long
    Dim outRow As Long

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

Public Sub AddSampleClientRow()
    Dim ws As Worksheet
    Dim nextRow As Long
    Set ws = ThisWorkbook.Worksheets(SHEET_CLIENTS)
    nextRow = ws.Cells(ws.Rows.Count, COL_GSTIN).End(xlUp).Row + 1
    If nextRow < CLIENT_FIRST_DATA_ROW Then nextRow = CLIENT_FIRST_DATA_ROW

    ws.Cells(nextRow, COL_CLIENT_ID).Value = "C" & Format$(nextRow - CLIENT_FIRST_DATA_ROW + 1, "000")
    ws.Cells(nextRow, COL_CLIENT_NAME).Value = "Sample Client Pvt Ltd"
    ws.Cells(nextRow, COL_GSTIN).Value = "27AAAAA0000A1Z5"
    ws.Cells(nextRow, COL_USERNAME).Value = "sample.user"
    ws.Cells(nextRow, COL_PASSWORD).Value = "change-me"
    ws.Cells(nextRow, COL_EMAIL).Value = "client@example.com"
    ws.Cells(nextRow, COL_CONTACT).Value = "9876543210"
    ws.Cells(nextRow, COL_FILER_TYPE).Value = "Monthly"
    ws.Cells(nextRow, COL_ACTIVE).Value = "Yes"
    ws.Cells(nextRow, COL_NOTES).Value = "Replace with real client data"
End Sub

Public Function GetClientField(ByVal rowNum As Long, ByVal colNum As Long) As String
    GetClientField = Trim$(CStr(ThisWorkbook.Worksheets(SHEET_CLIENTS).Cells(rowNum, colNum).Value))
End Function

Public Sub MarkClientLogin(ByVal rowNum As Long)
    ThisWorkbook.Worksheets(SHEET_CLIENTS).Cells(rowNum, COL_LAST_LOGIN).Value = Now
End Sub
