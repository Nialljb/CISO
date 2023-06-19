import os
import flywheel
import json

# Get the API key from the environment
api_key = os.environ.get('FW_CLI_API_KEY')
client = flywheel.Client(api_key=api_key)

def find_files():
    # Read config.json file
    p = open('/flywheel/v0/config.json')
    config = json.loads(p.read())

    # Get the input file id
    input_file_id = (config['inputs']['axi']['hierarchy']['id'])

    # Get the file object container
    file_object_container = client.get(input_file_id)

    # Get the list of files in the container
    files = file_object_container.files

    # Loop through the list of files and get the file object information & download the file
    for n in range(len(files)):
        # Get the full file object information:
        file = files[n]
        if file['type'] == 'nifti' and 'T2' in file.name:
            print(file.name)
            if 'SAG' in file.name:
                sag = file
                print("sag is : ", sag.name)
                download_dir = ('/flywheel/v0/input/sag')
                download_path = download_dir + '/' + sag.name
                sag.download(download_path)
                
            elif 'COR' in file.name:
                cor = file
                print("cor is : ", cor.name) 
                download_dir = ('/flywheel/v0/input/cor')
                download_path = download_dir + '/' + cor.name
                cor.download(download_path)
    




