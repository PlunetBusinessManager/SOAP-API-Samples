#################
# Configuration #
#################

$systemurl = ""  # Enter URL to Plunet without the last /

$apiuser = "" # Enter API user login name

$apiuserpassword = "" #Enter API user password


#################
# Main script   #
#################

function Test-APILogin()
{

    param(
            [Parameter(Mandatory=$true)]
            [System.String]$URL,
            [Parameter(Mandatory=$true)]
            [System.String]$user,
            [Parameter(Mandatory=$true)]
            [System.String]$password
    )

    begin
    {
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
        if($url -like "https://*")
        {

            Write-Warning "Secured connection detected. Disabling Certification check"      
            [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
        }
    }

    process
    {
        $apiurl = $url + "/PlunetAPI?wsdl"
        
        try
        {   
            
 
            $client = New-WebServiceProxy -Uri $apiurl
            
            if (!$client)
            {
                throw "Connection to API endpoint failed"

        }

         $sessionid = $client.login($user, $password)

         if($sessionid -eq "refused")
         {
                throw "Access to API denied. Please check your credentials."

         }
         else
         {
                Write-Host "Login to API succeeded. Your session token is $sessionid" -ForegroundColor Green
                
         }

         return $sessionid
        
       }
       catch
       {

            Write-Error $_
       }


       finally
       {
           # [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$null}
       }


    }


}


$uuid = Test-APILogin -URL $systemurl -user $apiuser -password $apiuserpassword

