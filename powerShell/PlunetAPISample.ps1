$PlunetAPIHandler = [ServiceFactory]::new("https://mybmurl.plunet.com")
$plunetapiuser = "Plunet API"
$plunetapipassword = "<A good password goes here>"
#----------------------------------------------------------
# Login
#----------------------------------------------------------
$UUID = $PlunetAPIHandler.PlunetAPI.login($plunetapiuser, $plunetapipassword)
#----------------------------------------------------------
# Example: Getting all jobs from a project
#----------------------------------------------------------
$sampleProjectNr = "O-00057"
#-------------------------------------
# Step 1: Getting Order ID
#-------------------------------------
$orderIDIntegerResult = $PlunetAPIHandler.Orders.getOrderID($UUID, $sampleProjectNr)
$orderID = $orderIDIntegerResult.data
#-------------------------------------
# Step 2: Getting the items
#-------------------------------------
$itemIDIntegerListResult = $PlunetAPIHandler.Items.getAllItems($uuid, 3<#Project Type 3 = Order)#>, $orderID)
[Array]$itemIDList = $itemIDIntegerListResult.data
#-------------------------------------
# Step 3: Getting the jobs
#-------------------------------------
$Jobs = @{} #Initializing a new HashTable ("Associated Array")
foreach ($itemID in $itemIDList)
{

    $jobListResult = $PlunetAPIHandler.Jobs.getJobListOfItem_ForView($UUID, $itemID, 3<#Project Type 3 = Order)#>)
    foreach ($job in $jobListResult.data)
    {
        $jobDisplayNameStringResult = $PlunetAPIHandler.Jobs.getJobNumber($UUID, 3<#Project Type 3 = Order)#>, $job.jobid)
        $jobDisplayName  =$jobDisplayNameStringResult.data
        $Jobs.add($jobDisplayName, $job) # Add a new key-value pair.
    }
}
#-------------------------------------
# Step 4: Getting the project jobs
#-------------------------------------
$plunetversionStringResult  = $PlunetAPIHandler.PlunetAPI.getPlunetVersion()
$plunetversion = $plunetversionStringResult.data

[Array]$projectJobList = $null

if($plunetversion -lt 9)
{
    $languageIndependentItemID = 0
    $languageIndependentItemResult = $PlunetAPIHandler.Items.getLanguageIndependentItemObject($UUID, 3<#Project Type 3 = Order)#>, $orderID, 1 <# System currency#>)
    if($languageIndependentItemResult.statusCode -eq "-37")
    {
        #In Plunet 8 and older this only works if the language independent item is explicitly existing!
        try
        {
            $itemIN = New-Object Microsoft.PowerShell.Commands.NewWebserviceProxy.AutogeneratedTypes.WebServiceProxy35a29_plunet_com_DataItem30_wsdl.ItemIN # The web service proxy Id is set randomly!
            $itemIN.projectID = $orderID
            $itemIN.briefDescription = "Language independent item"
            $itemIN.projectType = 3
            $itemInsertResult = $PlunetAPIHandler.Items.insertLanguageIndependentItem($UUID, $itemIN)
            $languageIndependentItemID = $itemInsertResult.data
        }
        catch
        {
            #Error handling goes here
        }
    }
    else
    {
        $languageIndependentItemID = $languageIndependentItemResult.data
    }

    $projectJobListResult = $PlunetAPIHandler.Jobs.getJobListOfItem_ForView($UUID, $languageIndependentItemID, 3<#Project Type 3 = Order)#>)

}
else
{
    $projectJobListResult = $PlunetAPIHandler.Jobs.getItemIndependentJobs($UUID,  3 <#Project Type 3 = Order)#>, $orderID)
}

$projectJobList=$projectJobListResult.data
foreach ($projectJob in $projectJobList)
{
    $jobDisplayNameStringResult = $PlunetAPIHandler.Jobs.getJobNumber($UUID, 3<#Project Type 3 = Order)#>, $projectJob.jobid)
    $jobDisplayName  =$jobDisplayNameStringResult.data
    $Jobs.add($jobDisplayName, $job) # Add a new key-value pair.
}

#-------------------------------------
# Step 5: Output
#-------------------------------------
$Jobs.values | Out-GridView #Out-Gridview will display a table window populated with the data of the passed object


#----------------------------------------------------------
# Logout (best practice to always log out at this step to ensure functionality)
#----------------------------------------------------------
$PlunetAPIHandler.PlunetAPI.logout($UUID)
