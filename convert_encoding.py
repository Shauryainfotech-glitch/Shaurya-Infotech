import os

def convert_to_utf8_no_bom(file_path):
    # Read the file with any encoding and remove BOM if present
    with open(file_path, 'rb') as f:
        content = f.read()
    # Remove BOM if present
    bom = b'\xef\xbb\xbf'
    if content.startswith(bom):
        content = content[len(bom):]
    # Write back with UTF-8 encoding without BOM
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content.decode('utf-8', errors='replace'))

if __name__ == "__main__":
    # Specify the file to convert
    file_to_convert = "customs/addons/solar_installation_final_module/views/solar_product_views.xml"
    if os.path.exists(file_to_convert):
        convert_to_utf8_no_bom(file_to_convert)
        print(f"Converted {file_to_convert} to UTF-8 without BOM.")
    else:
        print(f"File {file_to_convert} does not exist.")
