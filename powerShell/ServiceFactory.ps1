using namespace System.Net

class ServiceFactory
{
    hidden[Hashtable]$_webservicesLookup =@{
        PlunetAPI               = "PlunetAPI";
        CustomFields            = "DataCustomFields30";
        Admin                   = "DataAdmin30";
        CreditNotes             = "DataCreditNote30";
        Customers               = "DataCustomer30";
        Customer_Addresses      = "DataCustomerAddress30";
        Customer_Contacts       = "DataCustomerContact30";
        Files                   = "DataDocument30";
        Items                   = "DataItem30";
        Jobs                    = "DataJob30";
        Rounds                  = "DataJobRound30";
        Orders                  = "DataOrder30";
        Receivables             = "DataOutgoingInvoice30";
        Payables                = "DataPayable30";
        Quotes                  = "DataQuote30";
        Requests                = "DataRequest30";
        Resources               = "DataResource30";
        Resource_Addresses      = "DataResourceAddress30";
        Resource_Contacts       = "DataResourceContact30";
        Users                   = "DataUser30";
        CustomerSearch          = "ReportCustomer30";
        JobSearch               = "ReportJob30";
        RequestDocuments        = "RequestDocText30";
    }

    static ServiceFactory()
    {


    }

    ServiceFactory($baseURL)
    {
        $this._build($baseURL)
    }

    hidden _build($baseURL)
    {
            if($baseURl -like "https://*")
        {
            [ServicePointManager]::SecurityProtocol = [SecurityProtocolType]::Tls12
            Write-Warning "Secured connection detected. Disabling Certification check"      
            [ServicePointManager]::ServerCertificateValidationCallback = {$true}
        }
       foreach ($entry in $this._webservicesLookup.GetEnumerator())
       {
            try
            {
           
            $this | Add-Member -Name $entry.key -MemberType NoteProperty -Value (New-WebServiceProxy -Uri "$($baseURL)/$($entry.value)?wsdl" ) 
            Write-Information -MessageData ("Webservice $($entry.value) successfully loaded.")
            }
            catch
            {
            Write-Host $_
            }
       }
    }
}
