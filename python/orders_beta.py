from zeep import Client
from decimal import Decimal
from datetime import datetime
import json

########################## SETTINGS ########################################

CREDENTIALS = {
    "qa3": {"BASE_URL": 'https://linktoyourplunet.com/', "users": {"apiuser": {"USERNAME": 'API USER', "PASSWORD": 'XXXXXX'}}}  # Please enter your API user here for all capitalized items
}

PROPERTIES = {
    "order": ["Property Name English 1", "Property Name English 2"],  # Please enter the English names of your properties for orders here
    "item": ["Property Name English 1", "Property Name English 2"]
}

########################## FUNCTIONS ########################################


def get_endpoints():
    plunet_endpoints = {
        "PlunetAPI": Client(credentials.get("BASE_URL") + "PlunetAPI?wsdl").service,
        "Item": Client(credentials.get("BASE_URL") + "DataItem30?wsdl").service,
        "Custom Fields": Client(credentials.get("BASE_URL") + "DataCustomFields30?wsdl").service,
        "Order": Client(credentials.get("BASE_URL") + "DataOrder30?wsdl").service,
        "Customer": Client(credentials.get("BASE_URL") + "DataCustomer30?wsdl").service,
        "Resource": Client(credentials.get("BASE_URL") + "DataResource30?wsdl").service,
    }
    return plunet_endpoints


def login():
    endpoint = get_endpoints()
    user = credentials.get("users").get("apiuser")
    uuid_resp = endpoint["PlunetAPI"].login(user.get("USERNAME"), user.get("PASSWORD"))
    return endpoint, uuid_resp


def write_to_file(data_list, filename):
    with open(filename, 'w') as fp:
        fp.write(json.dumps(data_list, indent=4, default=str))
    return


def get_all_orders():  # SEARCHING FOR ORDERS BY FILTER
    timeframe = {
        "dateFrom": "2003-01-01",
        "dateRelation": 2,
        "dateTo": datetime.today().strftime('%Y-%m-%d'),
    }

    searchfilter = {
        "languageCode": "EN",
        "orderStatus": -1,
        "customerID": -1,
        "projectType": -1,
        "statusProjectFileArchiving": -1,
        "timeFrame": timeframe

    }
    list_result = endpoints["Order"].search(uuid, searchfilter).data
    return list_result


def get_properties_o(order_object):
    for prop in PROPERTIES["order"]:
        try:
            property_id = endpoints["Custom Fields"].getProperty(uuid, prop, 6,
                                                                 order_object["Order ID"]).data.selectedPropertyValueID
            order_object[prop] = endpoints["Custom Fields"].getPropertyValueText(uuid, prop, property_id, "EN").data
        except:
            order_object[prop] = None
    return order_object


def get_properties_i(item_object):
    for prop in PROPERTIES["item"]:
        try:
            property_id = endpoints["Custom Fields"].getProperty(uuid, prop, 10,
                                                                 item_object["Item ID"]).data.selectedPropertyValueID
            item_object[prop] = endpoints["Custom Fields"].getPropertyValueText(uuid, prop, property_id, "EN").data
        except:
            item_object[prop] = None
    return item_object


def get_order_details(order_id):
    order_object = endpoints["Order"].getOrderObject(uuid, order_id).data
    order_object_1 = {
        "Retrieval Date": datetime.today().strftime('%Y-%m-%d'),
        "Order ID": int(order_object["orderID"]),
        "Order Number": str(order_object["orderDisplayName"]),
        "Order Date": order_object["orderDate"],
        "Connected Order IDs": order_object["orderID"],
        "Project Name": str(order_object["projectName"]),
        "Project Subject": str(order_object["subject"]),
        "Archive Status": endpoints["Order"].getProjectStatus(uuid, order_id).data,
        "Creation Date": endpoints["Order"].getCreationDate(uuid, order_id).data,
        "Category": endpoints["Order"].getProjectCategory(uuid, "EN", order_id).data,
        "Customer": order_object["customerID"],
        "Project Manager": order_object["projectManagerID"],
        "Currency": order_object["currency"],
        "Conversion Rate": order_object["rate"]
    }
    order_object_final = get_properties_o(order_object_1)

    return order_object_final


def get_item_details(order_id, item_id):
    item_object = endpoints["Item"].getItemObject(uuid, 3, item_id).data

    item_object_1 = {
        "Retrieval Date": datetime.today().strftime('%Y-%m-%d'),
        "Order ID": order_id,
        "Item ID": item_id,
        "Brief Description": item_object["briefDescription"],
        "Item Status ID": item_object["status"],
        "Delivery Deadline": item_object["deliveryDeadline"],
        "Delivery Date": endpoints["Item"].getDeliveryDate(uuid, item_id).data,
        "Total Price": item_object["totalPrice"],
        "Total Price in Home Currency": Decimal(endpoints["Item"].getTotalPriceByCurrencyType(uuid, 1, item_id, 2).data)
    }
    item_object_final = get_properties_i(item_object_1)

    #  Getting the pricelist for an item with recurring stuff
    item_set_pricelist = endpoints["Item"].getPricelist(uuid, item_id, 3).data
    if item_set_pricelist is not None:
        item_set_pricelist_prices = endpoints["Item"].getPricelistEntry_List(uuid, item_set_pricelist["pricelistID"], "French", "English").data

        recurring_item_pricelist = {
            "Item ID": item_id,
            "Pricelist ID": item_set_pricelist["pricelistID"],
            "Pricelist Name": item_set_pricelist["PricelistNameEN"],
            "Pricelist Currency": item_set_pricelist["currency"],
            "Prices": item_set_pricelist_prices
            }
    else:
        recurring_item_pricelist = {
            "Item ID": item_id,
            "Pricelist ID": None
        }

    return item_object_final, recurring_item_pricelist


def get_prices(item_id, price_id):
    try:
        price_name = endpoints["Item"].getPriceUnit(uuid, price_id.priceUnitID, "EN").data.description
    except:
        price_name = "not available"
    try:
        price_service = str(endpoints["Item"].getPriceUnit(uuid, price_id.priceUnitID, "EN").data.service)
    except:
        price_service = "not available"

    price_object = {
        "Retrieval Date": datetime.today().strftime('%Y-%m-%d'),
        "Item ID": item_id,
        "PriceLine ID": price_id.priceLineID,
        "Price Unit ID": price_id.priceUnitID,
        "Price Unit Name": price_name,
        "Service": price_service,
        "Amount": Decimal(price_id.amount),
        "Unit Price": round(Decimal(price_id.unit_price), 2),
        "Tax Type": price_id["taxType"]
    }

    return price_object


def new_order_factory():
    i = 0
    list_order_objects = []
    list_item_objects = []
    list_priceline_objects = []
    list_pricelist_objects = []

    orderlist = get_all_orders()  # Running to get all the orders
    for o_id in orderlist:  # Getting the Order Data
        i += 1
        list_order_objects.append(get_order_details(o_id))
        print("Orders:", i, "/", len(orderlist))
    write_to_file(list_order_objects, "orders.json")

    i = 0
    for o_id in orderlist:  # Running to get all the items for each order
        i += 1
        for i_id in endpoints["Item"].getAllItems(uuid, 3, o_id).data:
            i_objects, pricelist_objects = get_item_details(o_id, i_id)
            list_item_objects.append(i_objects)
            list_pricelist_objects.append(pricelist_objects)
        print("Orders (Items):", i, "/", len(orderlist))
    write_to_file(list_item_objects, "order_items.json")  # Writing the data to file
    write_to_file(list_pricelist_objects, "order_items_pricelist.json")

    i = 0
    itemlist = list((s_object["Item ID"] for s_object in list_item_objects))  # getting all the items
    for i_id in itemlist:  # Running to get all the pricelines for each item
        i += 1
        for p_id in endpoints["Item"].getPriceLine_List(uuid, i_id, 3).data:  # for Orders (parameter=3) and in system currency (parameter=2)
            list_priceline_objects.append(get_prices(i_id, p_id))
        print("Items (Prices):", i, "/", len(orderlist))
    write_to_file(list_priceline_objects, "order_items_prices.json")


credentials = CREDENTIALS.get("qa3")
endpoints, uuid = login()
new_order_factory()
