from zeep import Client
import json

########################## SETTINGS ########################################

CREDENTIALS = {
    "myplunet": {"BASE_URL": 'https://www.myplunet.com/', "users": {"apiuser": {"USERNAME": 'API USER', "PASSWORD": 'XXXXXX'}}}  # Please enter your API user here for all capitalized items
}

PROPERTIES = {
    "customer": ["Property Name English 1", "Property Name English 2"]  # Please enter the English names of your properties for customers here
}

SEARCH_FILTER_STATUS = [1, 2, 3]  # We are filtering for Active, Old and Contacted customers (please refer to the Enum CustomerStatus for more information)
ADDRESS_SELECTION = 1  # We want the Delivery address to be exported (please refer to the Enum AddressType for more information)

########################## FUNCTIONS ########################################

def get_endpoints():
    plunet_endpoints = {
        "PlunetAPI": Client(credentials.get("BASE_URL")+"PlunetAPI?wsdl").service,
        "Customer": Client(credentials.get("BASE_URL") + "DataCustomer30?wsdl").service,
        "Customer Address": Client(credentials.get("BASE_URL") + "DataCustomerAddress30?wsdl").service,
        "Custom Fields": Client(credentials.get("BASE_URL") + "DataCustomFields30?wsdl").service,
    }
    return plunet_endpoints


def login():
    endpoint = get_endpoints()
    user = credentials.get("users").get("apiuser")
    uuid_resp = endpoint["PlunetAPI"].login(user.get("USERNAME"), user.get("PASSWORD"))
    return endpoint, uuid_resp


def get_customer_address(customer_object):
    all_addresses = endpoints["Customer Address"].getAllAddresses(uuid, customer_object["customerID"]).data  # first we are getting all addresses for the customer
    for address in all_addresses:
        if endpoints["Customer Address"].getAddressType(uuid, address).data == ADDRESS_SELECTION:  # now we are filtering for the address type as selected up on top in this file
            city = endpoints["Customer Address"].getCity(uuid, address).data
            zipcode = endpoints["Customer Address"].getZip(uuid, address).data
            country = endpoints["Customer Address"].getCountry(uuid, address).data
            return city, zipcode, country
    return None, None, None  # if no address is found, return empty values


def find_customer_properties(customer_properties_obj_list, customer_object):
    # Building a separate table for Customer Properties
    customer_properties = {"Customer ID": customer_object["customerID"]}
    for prop in PROPERTIES.get("customer"):
        try:
            property_value_list = endpoints["Custom Fields"].getProperty(uuid, prop, 1, customer_object[
                "customerID"]).data.selectedPropertyValueList
            if len(property_value_list) == 0:
                customer_properties[prop] = "not set"
            else:
                values = []
                for prop_value_id in property_value_list:
                    values.append(endpoints["Custom Fields"].getPropertyValueText(uuid, prop, prop_value_id, "EN").data)
                customer_properties[prop] = values
        except:
            customer_properties[prop] = "not set"
    customer_properties_obj_list.append(customer_properties)
    return customer_properties_obj_list


def customer_retrieval():
    customer_objects_list = []
    customer_properties_obj_list = []

    for customer_status in SEARCH_FILTER_STATUS:  # Due to a current problem with filtering and lists in Python we are not using the endpoint getAllCustomerObjects2, instead we are iterating through the defined status
        for customer_object in endpoints["Customer"].getAllCustomerObjects(uuid, customer_status).data:  # This Call retrieves all existing customer objects for the defined status
            city, zipcode, country = get_customer_address(customer_object)  # We are also retrieving the address of the customer, in order to simplify the use case only City, ZIP and Country are retrieved
            if customer_status == 1:  # based on system Setup both contacted, and old are inactive customers in the example.
                customer_status_string = "Active"
            else:
                customer_status_string = "Inactive"

            customer_object_clean = {  # Building the customer object based on the data received
                "Customer ID": customer_object["customerID"],
                "Customer Name1": customer_object["name1"],
                "Customer Name2": customer_object["name2"],
                "Customer Status": customer_status_string,
                "Customer ZIP Code": str(zipcode),
                "Customer City": str(city),
                "Customer Country": str(country),
                "Customer Account Manager": endpoints["Customer"].getAccountManagerID(uuid, customer_object["customerID"]).data  # additional data from other endpoints can be added as well, please see DataCustomer30 Class for more information
            }
            customer_objects_list.append(customer_object_clean)  # each customer with their data is added to a list.
            customer_properties_obj_list = find_customer_properties(customer_properties_obj_list, customer_object)  # now, we also need to find properties that belong to our customer.
    return customer_properties_obj_list, customer_objects_list


def write_to_file(data_list, filename):
    with open(filename, 'w') as fp:
        fp.write(json.dumps(data_list, indent=4, default=str))
    return


credentials = CREDENTIALS.get("myplunet")
endpoints, uuid = login()
list_customer_properties, list_customer_objects = customer_retrieval()
write_to_file(list_customer_properties, 'PlunetCustomer_Properties.json')
write_to_file(list_customer_objects, 'PlunetCustomers.json')
