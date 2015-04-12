Feature: can load dynamic components using path of setting file

	Scenario: Load a components defition py file and check the loaded components
		Given we have a dynamic loader module
		 when i say load components definition file "sampleComponents"
		 then we find component "name" is "test components 1"
		 and we find component "url" is "www.abc.xyz.com"

	Scenario: Load a components which use values from current environment
		Given we have a dynamic loader module
		 and variable "WELCOME_MESSAGE" has value "welcome to dynamic loading"
		 and there exists definition file "sampleComponentsVar" which uses variable "WELCOME_MESSAGE"
		 when i say load given components definition file
		 then we find component "msg" has value "Received : welcome to dynamic loading"
		 
		 
		
