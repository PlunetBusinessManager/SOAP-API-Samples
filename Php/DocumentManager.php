<?php 

	/**
	 * @author Alexander Schüßler
	 * @copyright 2016 Plunet GmbH / Plunet Inc.
	 */
	class PlunetDocumentManager
	{			
		/*
		 * Allowed folder types
		 */
		const FOLDER_REQUEST_REF 		= 1;
		const FOLDER_REQUEST_SOURCE 	= 2;
		const FOLDER_QUOTE_REF 			= 3;
		const FOLDER_QUOTE_SOURCE		= 4;
		const FOLDER_ORDER_REF			= 5;
		const FOLDER_ORDER_SOURCE		= 6;
				
		/**
		 * @var 	string 		Holds the current PlunetAPI session token
		 * @access 	private
		 */
		private $uuid ="";
		
		/**
		 * @var 	SoapClient 	A reference to the current SOAP instance 
		 * @access 	private
		 */
		private $soaphandler = null;
		
		/**
		 * Constructor - Connects to a DataDocument30 endpoint of a Plunet Business Manager installation
		 * @param string $uuid The current API session token to store as private property
		 * @param array $options Options being used to construct the SoapClient instance - see http://php.net/manual/de/soapclient.soapclient.php
		 * @access public
		 * @return void
		 */
		public function __construct($uuid, $options)
		{
			$this->uuid= $uuid;
			$endpoint = buildclassURL('DataDocument30');
			$this->soaphandler = new DataDocument30($options, $endpoint);
			
		}
		
		/**
		 * Lists all existing files within a project folder
		 * @param int 	$projectid		The main id of the project (do not mix up with display name)
		 * @param int 	$foldertype		The folder type to be seeked
		 * @throws RuntimeException if a non-supported folder type is passed
		 * @access public
		 * @example $PlunetDocumentManager->getFileList(28, PlunetDocumentManager::FOLDER_REQUEST_REF)
		 * @return StringArrayResult
		 */
		public function getFileList($projectid, $foldertype)
		{
			if(!$this->folderType_exists($foldertype))
			{
				throw new RuntimeException("The folder type you specified does not exist.");				
			}
			
			try {
				
				$filelist = $this->soaphandler->getFileList($this->uuid, $projectid, $foldertype);
				return $filelist->data;		
				
			}
			
			catch (SoapFault $fault)
			{
				echo "<pre>\n -- fault -- \n";
				var_dump($fault);
				echo "\n -- fault code/string --\n";
				echo "SOAP Fault: (faultcode: {$fault->faultcode}, faultstring: {$fault->faultstring})";
				echo "\n -- request --\n";
				echo "REQUEST:\n" . htmlentities($soap->__getLastRequest()) . "\n";
				echo "\n -- response --\n";
				echo "Response:\n" . $soap->__getLastResponse() . "\n";
				echo "\n</pre>";
				return $null;
			}
			
		}

		/**
		 * Uploads a file to a project
		 * @param 	string 		$sourcepath 		The absolute path of file to be uploaded
		 * @param 	string 		$targetfilename		The (new) file name at target folder
		 * @param 	int 		$projectid			The main id of the project (do not mix up with display name)
		 * @param 	int			$foldertype			The folder type the file should be uploaded to
		 * @throws 	RuntimeException if a non-supported folder type is passed
		 * @throws 	Exception if the file that should be uploaded does not exist
		 * @access 	public
		 * @example	$PlunetDocumentManager->uploadFile('C:mypath\myfile.xxx', 'myfile.xxx',28, PlunetDocumentManager::FOLDER_REQUEST_REF);
		 * @return 	boolean
		 */
		public function uploadFile($sourcepath, $targetfilename, $projectid, $foldertype)
		{
				if(!$this->folderType_exists($foldertype))
				{
					throw new RuntimeException("The folder type you specified does not exist.");
				}		
			
				if(!file_exists($sourcepath))
				{
					throw new Exception ("The file you specified does not exist or is not accesable.");	
				}
				
				$bytes = file_get_contents($sourcepath);
				$filesize = filesize($sourcepath);			
				$fileargs = array(
						
					'UUID'			=>	$this->uuid,	
					'MainID'		=>	$projectid,
					'FolderType'	=>	$foldertype,
					'FileByteStream'=>	$bytes,
					'FilePathName'	=>	$targetfilename,
					'FileSize'		=>	$filesize										
				);
				
				echo var_dump($fileargs);
				try
				{
					$result = $this->soaphandler->upload_Document
					(	$fileargs['UUID'], 
						$fileargs['MainID'], 
						$fileargs['FolderType'], 
						$fileargs['FileByteStream'], 
						$fileargs['FilePathName'], 
						$fileargs['FileSize']
					);
					
					if(0 === $result->statusCode)
						return true;
						else
							return false;
				}
				catch (SoapFault $fault)
							{
								echo "<pre>\n -- fault -- \n";
								var_dump($fault);
								echo "\n -- fault code/string --\n";
								echo "SOAP Fault: (faultcode: {$fault->faultcode}, faultstring: {$fault->faultstring})";
								echo "\n -- request --\n";
								echo "REQUEST:\n" . htmlentities($soap->__getLastRequest()) . "\n";
								echo "\n -- response --\n";
								echo "Response:\n" . $soap->__getLastResponse() . "\n";
								echo "\n</pre>";
								return false;
							}									


			
		}
		
		/**
		 * Downloads file from a project folder
		 * @param 	string 		$sourcepath		The filename to be downloaded from the project		
		 * @param 	string 		$targetfilename	The absolute path to the destination and its file name
		 * @param 	int 		$projectid		The main id of the project (do not mix up with display name)
		 * @param 	int 		$foldertype		The folder type the file should be downloaded from
		 * @param 	bool 		$force			If specified, the method will try to delete the existing file with same name and replace it with the downloaded one
		 * @access	public		
		 * @example	$PlunetDocumentManager->downloadFile('/myfile.xxx', 'C:mypath\myfile.xxx', 28, PlunetDocumentManager::FOLDER_REQUEST_REF);
		 * @return boolean
		 */
		public function downloadFile($sourcepath, $targetfilename, $projectid, $foldertype, $force = false)
		{
			if(!$this->folderType_exists($foldertype))
			{
					throw new RuntimeException("The folder type you specified does not exist.");
			}		
			
			$fileargs = array(
				'UUID'			=>		$this->uuid,
				'MainID'		=>		$projectid,
				'FolderType'	=>		$foldertype,
				'FilePathName'	=>		$sourcepath					
			);

			try {
					$fileresult = $this->soaphandler->download_Document
					(		$fileargs['UUID'], 
							$fileargs['MainID'], 
							$fileargs['FolderType'],
							$fileargs['FilePathName']
					);
						if(!$fileresult->statusCode === 0)
						return false;
						
					
					if(is_file($targetfilename) && isset($force))
					{
						try {
							unlink($targetfilename);
							
						}
							catch (Exception $e){}
					}
					
					if(! (bool) file_put_contents($targetfilename, $fileresult->fileContent, LOCK_EX))
					{
						throw new RuntimeException("Can't write to specified path");
					}	
					return true;
			}
				catch (SoapFault $fault)
				{
					echo "<pre>\n -- fault -- \n";
					var_dump($fault);
					echo "\n -- fault code/string --\n";
					echo "SOAP Fault: (faultcode: {$fault->faultcode}, faultstring: {$fault->faultstring})";
					echo "\n -- request --\n";
					echo "REQUEST:\n" . htmlentities($soap->__getLastRequest()) . "\n";
					echo "\n -- response --\n";
					echo "Response:\n" . $soap->__getLastResponse() . "\n";
					echo "\n</pre>";
					return false;
				}
				catch (Exception $e)
				{
					echo $e->getMessage();
				}
			
		}
		
		/**
		 * Loads all files from a project folder and tries to create a .zip file containing the project files
		 * @param 	int 		$projectid		The main id of the project (do not mix up with display name)
		 * @param 	int 		$foldertype		The folder type to receive files from
		 * @param 	string 		$targetpath		The absolute path of target folder on the downloading host
		 * @param 	string 		$zipname		The name of the downloaded folder (default: "Download")
		 * @param 	bool 		$force			Specifies whether a file that yet exists should be replaced
		 * @throws 	RuntimeException if a non-supported folder type is passed
		 * @access 	public
		 * @example	$PlunetDocumentManager->getAllFilesFromProjectFolder(28,PlunetDocumentManager::FOLDER_REQUEST_REF, 'C:mypath\', 'R-12345_files');
		 * @return 	NULL|boolean true when files have been downloaded, else null
		 */
		public function getAllFilesFromProjectFolder($projectid, $foldertype, $targetpath, $zipname = "Download")
		{
			if(!$this->folderType_exists($foldertype))
			{
				throw new RuntimeException("The folder type you specified does not exist.");
			}
			
			$files = $this->getFileList($projectid, $foldertype);
			
			if(!is_array($files))
			{
				return null;
			}
			
			if(!is_dir($targetpath . '\\' . $zipname))
			{
				try {
					mkdir($targetpath . '\\' . $zipname);

				}
				catch(Exception $e){}
			}
			
			$zip = new ZipArchive();
			$zippath = $targetpath . '\\' . $zipname;
			
			if($zip->open($zippath . '.zip', ZipArchive::CREATE)!== TRUE)
			{	
				trigger_error("Can't create zip archive. Download files to usual folder.", E_USER_WARNING);
			}
	
			foreach ($files as $file)
			{				
				
				$purefilename = str_replace('\\', '', $file);
				$targetfilename = $targetpath . '\\' . $zipname . '\\' .  $purefilename;
				
				$download = $this->downloadFile($file, $targetfilename, $projectid, $foldertype, $zipname);	
				if(!$download)
				{
					continue;
				}
				$zip->addFile($targetfilename, $purefilename);
							
			}
			
			if($zip)
				$zip->close();
			
				return true;
		}
		
		/**
		 * Checks if a valid folder type has been passed to a DataDocument30 method
		 * @param int 	$foldertype 	The folder type to be used with DataDocument30 method
		 * @access protected
		 * @return boolean
		 */
		protected function folderType_exists($foldertype)
		{
			switch ($foldertype)
			{
				case self::FOLDER_REQUEST_REF:
				case 1:
				case self::FOLDER_REQUEST_SOURCE:
				case 2:
				case self::FOLDER_QUOTE_REF:
				case 3:
				case self::FOLDER_QUOTE_SOURCE:
				case 4:
				case self::FOLDER_ORDER_REF:
				case 5:
				case self::FOLDER_ORDER_SOURCE:
				case 6:
					return true; break;
				default: return false;					
				
			}
			
		}
		
	}

?>
