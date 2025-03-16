import re

connection_string = "HostName=anemoiahub.azure-devices.net;DeviceId=testidevice;SharedAccessKey=ar/pbGoqZe47Qs5uLhZgDEuO+AFwLyLM0tlmyVKQRqg="
match = re.search(r'DeviceId=([^;]+);', connection_string)
device_id = match.group(1) if match else "Not found"

print(device_id)  # Output: asdsaoskdja


