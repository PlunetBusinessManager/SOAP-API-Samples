from zeep import Client
from decimal import Decimal
import json

# SETTINGS

CREDENTIALS = {
    "qa3": {"BASE_URL": 'https://qa3.plunet.com/', "users": {"apiuser": {"USERNAME": 'API USER', "PASSWORD": 'XXXXXX'}}},  # Please enter your API user here for all capitalized items
}

PROPERTIES = {
    "Quote": ["Property Name English 1", "Property Name English 2"]  # Please enter the English names of your properties for quotes here
}

# FUNCTIONS


def get_endpoints():
    plunet_endpoints = {
        "PlunetAPI": Client(credentials.get("BASE_URL") + "PlunetAPI?wsdl").service,
        "Item": Client(credentials.get("BASE_URL") + "DataItem30?wsdl").service,
        "Custom Fields": Client(credentials.get("BASE_URL") + "DataCustomFields30?wsdl").service,
        "Quote": Client(credentials.get("BASE_URL") + "DataQuote30?wsdl").service,
        "Customer": Client(credentials.get("BASE_URL") + "DataCustomer30?wsdl").service,
        "Resource": Client(credentials.get("BASE_URL") + "DataResource30?wsdl").service,
    }
    return plunet_endpoints


def login():
    endpoint = get_endpoints()
    user = credentials.get("users").get("apiuser")
    uuid_resp = endpoint["PlunetAPI"].login(user.get("USERNAME"), user.get("PASSWORD"))
    return endpoint, uuid_resp


def find_quotes_based_on_searchfilter():
    searchfilter = {  # Search Filter can be customized, please refer to the Class SearchFilter_Quote for more information
        "languageCode": "EN",
        "quoteStatus": 9  # For this example, we are only looking at currently pending quotes. Please refer to the Enum QuoteStatusType for more details
    }
    search_result = endpoints["Quote"].search(uuid, searchfilter).data
    return search_result  # returns a list of quotes matching the search filters


def get_properties(quote_object):
    for prop in PROPERTIES["Quote"]:
        try:
            property_id = endpoints["Custom Fields"].getProperty(uuid, prop, 5, quote_object["Quote ID"]).data.selectedPropertyValueID
            quote_object[prop] = endpoints["Custom Fields"].getPropertyValueText(uuid, prop, property_id, "EN").data
        except:
            quote_object[prop] = "not set"

    return quote_object


def get_quote_details(quote_id):
    quote_object = {
        "Quote ID": quote_id,
        "Quote Number": endpoints["Quote"].getQuoteNo_for_View(uuid, quote_id).data,
        "Quote Version": int(endpoints["Quote"].getQuoteNo_for_View(uuid, quote_id).data[-2:]),
        "Creation Date": endpoints["Quote"].getCreationDate(uuid, quote_id).data,
        "Project Name": endpoints["Quote"].getProjectName(uuid, quote_id).data,
        "Subject": endpoints["Quote"].getSubject(uuid, quote_id).data,
        "Category": endpoints["Quote"].getProjectCategory(uuid, "EN", quote_id).data,
        "Customer": endpoints["Customer"].getName1(uuid, endpoints["Quote"].getCustomerID(uuid, quote_id).data).data,  # for the sake of this example, we do not only retrieve the customer id but instead the actual customer name
        "Project Manager": endpoints["Resource"].getName1(uuid, endpoints["Quote"].getProjectmanagerID(uuid, quote_id).data).data,  # for the sake of this example, we do not only retrieve the resource id for the PM but instead the actual name
        "Project Status": endpoints["Quote"].getProjectStatus(uuid, quote_id).data,
        "Quote Status": endpoints["Quote"].getStatus(uuid, quote_id).data,
        "Currency": endpoints["Quote"].getCurrency(uuid, quote_id).data,
        "Conversion Rate": Decimal(endpoints["Quote"].getRate(uuid, quote_id).data)
    }
    quote_object = get_properties(quote_object)  # We will also get the quote properties
    return quote_object


def get_item_details(item_id, quote_id):
    item_object = {
        "Quote ID": quote_id,
        "Item ID": item_id,
        "Brief Description": endpoints["Item"].getBriefDescription(uuid, 1, item_id).data,
        "Item Status ID": endpoints["Item"].getStatus(uuid, 1, item_id).data,
        "Delivery Deadline": endpoints["Item"].getDeliveryDeadline(uuid, 1, item_id).data,
        "Total Price": Decimal(endpoints["Item"].getTotalPrice(uuid, 1, item_id).data),
        "Total Price in Home Currency": Decimal(endpoints["Item"].getTotalPriceByCurrencyType(uuid, 1, item_id, 2).data)
    }
    return item_object


def get_prices(iid):
    pricelines = endpoints["Item"].getPriceLine_ListByCurrency(uuid, iid, 1, 2).data  # for Quotes (parameter=1) and in system currency (parameter=2)
    for entry in pricelines:
        try:
            price_name = endpoints["Item"].getPriceUnit(uuid, entry.priceUnitID, "EN").data.description,
        except:
            price_name = "not available"
        try:
            price_service = str(endpoints["Item"].getPriceUnit(uuid, entry.priceUnitID, "EN").data.service),
        except:
            price_service = "not available"
        price_object = {
            "Item ID": iid,
            "PriceLine ID": entry.priceLineID,
            "Price Unit ID": entry.priceUnitID,
            "Price Unit Name": price_name,
            "Service": price_service,
            "Amount": Decimal(entry.amount),
            "Unit Price": Decimal(entry.unit_price),
            "Total Price": Decimal(entry.unit_price * entry.amount),
            "Tax Type": entry.taxType
        }
        priceline_list.append(price_object)
    return


def retrieve_quote_data():
    quotes_object_list = []
    for quote_id in list_of_quotes:
        quotes_object_list.append(get_quote_details(quote_id))
    return quotes_object_list


def retrieve_item_data():
    items_list = []
    for quote_id in list_of_quotes:
        list_of_items = endpoints["Item"].getAllItems(uuid, 1, quote_id).data
        for item_id in list_of_items:
            items_list.append(get_item_details(item_id, quote_id))
            get_prices(item_id)

    return items_list, priceline_list


def write_to_file(data_list, filename):
    with open(filename, 'w') as fp:
        fp.write(json.dumps(data_list, indent=4, default=str))
    return


priceline_list = []
credentials = CREDENTIALS.get("8144")
endpoints, uuid = login()
list_of_quotes = find_quotes_based_on_searchfilter()
quote_content = retrieve_quote_data()
items_content, prices_content = retrieve_item_data()
write_to_file(quote_content, 'quotes.json')
write_to_file(items_content, 'quote_items.json')
write_to_file(prices_content, 'quote_prices.json')
