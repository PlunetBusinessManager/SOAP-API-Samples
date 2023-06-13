#requires -version 5.0
#------------------------------------------------------------------------------------------------------------
# Plunet API Demo Script
# Author: Alexander Schüßler
# Note: This test script is used internally for demos and contains some magic strings / integers
# which may differ in your system. The script below should just show the business logic.
#------------------------------------------------------------------------------------------------------------
using namespace System.IO

#----------------------------------------------------------
# Initialize our toolbox
#----------------------------------------------------------
#$PlunetAPI = [ServiceFactory]::new("https://qa29.plunet.com")

#----------------------------------------------------------
# Log into Plunet API - acquire session token
#----------------------------------------------------------
$UUID = $PlunetAPI.PlunetAPI.login($APIUser, $APIPassword)

if($UUID -eq "refused"){
    Write-Error "Login to Plunet API failed"
    return
}

#----------------------------------------------------------
# Create a new request with two language combinations
#----------------------------------------------------------
$requestInsertResult = $PlunetAPI.Requests.insert($UUID)
if($requestInsertResult.statusMessage -eq "OK"){
    $requestID = $requestInsertResult.data
}
else{
    Write-Error "Can not create request"
    return
}

[void]$PlunetAPI.Requests.setBriefDescription($UUID, "Test with prospect $(Get-Date)", $requestID)
[void]$PlunetAPI.Requests.setCustomerID($UUID, 3, <#= Lucky Luke#> $requestID)
[void]$PlunetAPI.Requests.addLanguageCombination($UUID, "English (UK)", "German", $requestID)
[void]$PlunetAPI.Requests.addLanguageCombination($UUID, "English (UK)", "French", $requestID)

#----------------------------------------------------------
# Convert the request into a project based on universal 
# order template
#----------------------------------------------------------
$orderInsertResult = $PlunetAPI.Requests.orderRequest_byTemplate($UUID, $requestID, 7 <#= The universal template for API#>)
$orderID = $orderInsertResult.data

#----------------------------------------------------------
# Upload a source file
#----------------------------------------------------------
$testfilePath = "C:\Plunet\Test Files\Source\to translate.docx"
$testFileAsByteArray = [File]::ReadAllBytes($testfilePath)

[void]$PlunetAPI.Files.upload_Document($UUID, $orderID, 6 <# = order source folder#>, $testFileAsByteArray, "to translate.docx", $testFileAsByteArray.length)

#----------------------------------------------------------
# Apply a CAT analysis file
#----------------------------------------------------------
$testAnalysisPath = "C:\Plunet\Test Files\CAT\MemoQ\Analysis.csv"
$testAnalysisAsByteArray= [File]::ReadAllBytes($testAnalysisPath)

#---------------------------
# We need the item IDs...
#---------------------------
$itemListResult = $PlunetAPI.Items.getAllItems($UUID, 3,<#Project type = Order#> $orderID)
$firstItemID = $itemListResult.data[0]

[void]$PlunetAPI.Items.
setCatReport2($UUID, $testAnalysisAsByteArray, "Analysis.csv", $testAnalysisAsByteArray.Length, $true, 
                    4, <#CATType = MemoQ#> 3, <#Project type = Order#> $true, $firstItemID)


#----------------------------------------------------------
# Good boys log out gracefully....
#----------------------------------------------------------
[void]$PlunetAPI.PlunetAPI.logout($UUID)
