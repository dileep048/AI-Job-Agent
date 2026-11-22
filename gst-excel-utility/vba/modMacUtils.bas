Attribute VB_Name = "modMacUtils"
Option Explicit

#If Mac Then

Public Function CurlGet(ByVal url As String) As String
    On Error GoTo Fail
    Dim safeUrl As String
    safeUrl = Replace(url, "'", "'\''")
    CurlGet = MacScript("do shell script ""curl -sS -L --max-time 45 -H 'Accept: application/json' -H 'User-Agent: Mozilla/5.0' '" & safeUrl & "'""")
    Exit Function
Fail:
    CurlGet = ""
End Function

Public Function CurlPostJson(ByVal url As String, ByVal jsonBody As String) As String
    On Error GoTo Fail
    Dim safeUrl As String
    Dim safeBody As String
    safeUrl = Replace(url, "'", "'\''")
    safeBody = Replace(jsonBody, "'", "'\''")
    safeBody = Replace(safeBody, """", "\""")
    CurlPostJson = MacScript("do shell script ""curl -sS -L --max-time 45 -X POST -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'User-Agent: Mozilla/5.0' -d '" & safeBody & "' '" & safeUrl & "'""")
    Exit Function
Fail:
    CurlPostJson = ""
End Function

Public Sub OpenUrl(ByVal url As String)
    On Error Resume Next
    Dim safeUrl As String
    safeUrl = Replace(url, "'", "'\''")
    MacScript "do shell script ""open '" & safeUrl & "'"""
End Sub

Public Sub SetClipboardText(ByVal value As String)
    On Error Resume Next
    MacScript "set the clipboard to """ & Replace(value, """", "\""") & """"
End Sub

#Else

Public Function CurlGet(ByVal url As String) As String
    On Error GoTo Fail
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    http.Open "GET", url, False
    http.setRequestHeader "Accept", "application/json"
    http.setRequestHeader "User-Agent", "Mozilla/5.0"
    http.send
    If http.Status = 200 Then
        CurlGet = http.responseText
    Else
        CurlGet = ""
    End If
    Exit Function
Fail:
    CurlGet = ""
End Function

Public Function CurlPostJson(ByVal url As String, ByVal jsonBody As String) As String
    On Error GoTo Fail
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP.6.0")
    http.Open "POST", url, False
    http.setRequestHeader "Content-Type", "application/json"
    http.setRequestHeader "Accept", "application/json"
    http.setRequestHeader "User-Agent", "Mozilla/5.0"
    http.send jsonBody
    If http.Status = 200 Then
        CurlPostJson = http.responseText
    Else
        CurlPostJson = ""
    End If
    Exit Function
Fail:
    CurlPostJson = ""
End Function

Public Sub OpenUrl(ByVal url As String)
    On Error Resume Next
    CreateObject("WScript.Shell").Run url, 1, False
End Sub

Public Sub SetClipboardText(ByVal value As String)
    On Error Resume Next
    Dim dataObj As Object
    Set dataObj = CreateObject("MSForms.DataObject")
    dataObj.SetText value
    dataObj.PutInClipboard
End Sub

#End If

Public Function JsonValue(ByVal jsonText As String, ByVal key As String) As String
    Dim pattern As String
    Dim startPos As Long
    Dim endPos As Long
    Dim ch As String
    Dim escaped As Boolean

    pattern = """" & key & """:"""
    startPos = InStr(1, jsonText, pattern, vbTextCompare)
    If startPos = 0 Then Exit Function
    startPos = startPos + Len(pattern)

    For endPos = startPos To Len(jsonText)
        ch = Mid$(jsonText, endPos, 1)
        If escaped Then
            escaped = False
        ElseIf ch = "\" Then
            escaped = True
        ElseIf ch = """" Then
            JsonValue = Mid$(jsonText, startPos, endPos - startPos)
            JsonValue = Replace(JsonValue, "\""", """")
            JsonValue = Replace(JsonValue, "\/", "/")
            Exit Function
        End If
    Next endPos
End Function

Public Function ValidateGSTIN(ByVal gstin As String) As Boolean
    Dim cleaned As String
    cleaned = UCase$(Trim$(gstin))
    If Len(cleaned) <> 15 Then Exit Function
    ValidateGSTIN = (cleaned Like "[0-9][0-9][A-Z][A-Z][A-Z][A-Z][A-Z][0-9][0-9][A-Z][0-9][Z][A-Z0-9][A-Z0-9]")
End Function

Public Function SelectedFinancialYear() As String
    SelectedFinancialYear = Trim$(CStr(ThisWorkbook.Worksheets(SHEET_DASHBOARD).Range("FY_Selected").Value))
    If SelectedFinancialYear = "" Then SelectedFinancialYear = FY_2026_27
End Function

Public Function SelectedClientRow() As Long
    Dim ws As Worksheet
    Dim selectedRow As Long
    Set ws = ThisWorkbook.Worksheets(SHEET_DASHBOARD)
    selectedRow = CLng(Val(ws.Range("Selected_Client_Row").Value))
    If selectedRow < CLIENT_FIRST_DATA_ROW Then selectedRow = CLIENT_FIRST_DATA_ROW
    SelectedClientRow = selectedRow
End Function
