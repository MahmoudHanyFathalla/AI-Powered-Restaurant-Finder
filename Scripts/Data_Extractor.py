import pandas as pd
import json

# Load the CSV file
file_path = 'restaurantmenuchanges.csv'  # Replace with the actual path to your CSV file
data = pd.read_csv(file_path, on_bad_lines='warn', engine='python')

# Process the data
output = {}

# Group by restaurantName
for restaurant, group in data.groupby("restaurantName"):
    # Extract restaurant details (address and description)
    restaurant_info = {
        "address": group["restaurantAddress"].drop_duplicates().tolist(),
        "description": group["restaurantDescription"].drop_duplicates().tolist(),
        "menu": []
    }
    
    # Extract unique menu items and their details
    for _, row in group.iterrows():
        menu_item = {
            "name": row["menuItemName"],
            "description": row["menuItemDescription"],
            "category": row["menuItemCategory"],
            "price": row["menuItemCurrentPrice"]
        }
        if menu_item not in restaurant_info["menu"]:
            restaurant_info["menu"].append(menu_item)
    
    # Add to output
    output[restaurant] = restaurant_info

# Save as JSON
json_file_path = 'restaurants_data.json'
with open(json_file_path, 'w') as json_file:
    json.dump(output, json_file, indent=4)

# Save as TXT
txt_file_path = 'restaurants_data.txt'
with open(txt_file_path, 'w',encoding='utf-8') as txt_file:
    for restaurant, details in output.items():
        txt_file.write(f"Restaurant: {restaurant}\n")
        txt_file.write(f"Address: {', '.join(details['address'])}\n")
        txt_file.write(f"Description: {', '.join(details['description'])}\n")
        txt_file.write("Menu:\n")
        for menu_item in details['menu']:
            txt_file.write(f"  - Name: {menu_item['name']}\n")
            txt_file.write(f"    Description: {menu_item['description']}\n")
            txt_file.write(f"    Category: {menu_item['category']}\n")
            txt_file.write(f"    Price: {menu_item['price']}\n")
        txt_file.write("\n")

print(f"Data has been saved as JSON in '{json_file_path}' and as TXT in '{txt_file_path}'.")