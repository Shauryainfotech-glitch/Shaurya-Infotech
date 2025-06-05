import os

def convert_to_utf8_no_bom(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    bom = b'\xef\xbb\xbf'
    if content.startswith(bom):
        content = content[len(bom):]
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content.decode('utf-8', errors='replace'))

def convert_all_xml_files(root_dir):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(subdir, file)
                print(f"Converting {file_path}")
                convert_to_utf8_no_bom(file_path)

if __name__ == "__main__":
    module_dir = "customs/addons/solar_installation_final_module"
    convert_all_xml_files(module_dir)
    print("All XML files converted to UTF-8 without BOM.")
