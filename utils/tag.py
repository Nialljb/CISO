import flywheel
import os
from datetime import datetime

api_key = os.environ.get('FW_CLI_API_KEY')
fw = flywheel.Client(api_key=api_key)

group_name = "global_map"
project_name = "UCT-Khula-Hyperfine"
project = fw.lookup(f"{group_name}/{project_name}")
ciso_gear =  fw.lookup('gears/circumference')

 # Initialize gear_job_list
job_list = list()

# Loop through all the subjects in the project
for subject in project.subjects.iter():
    # The only way to get to acquisitions is to go through the sessions
    inputs = {}
    for session in subject.sessions.iter():
        session = session.reload()
        print("parsing... ", subject.label, session.label)
        # Get the acquisitions for the session
        acquisitions = session.acquisitions()
        for acquisition in acquisitions:
            # Get the files for the acquisition
            files = acquisition.files
            for file in files:
                # Check if the file is a nifti file
                if file.type == 'nifti' and 'T2' in file.name and 'QC-failed' not in file.tags:
                    print("QC-passed file is : ", file.name)
                else:
                    print("QC-failed file is : ", file.name)





    # # Get the parent id from inputs in config file
    # input_container_type = config.get("inputs", {}).get("axi", {}).get("hierarchy", {}).get("type")
    # if input_container_type == 'session':
    #         session_id = config.get("inputs", {}).get("axi", {}).get("hierarchy", {}).get("id")
    #         session_container = fw.get(session_id)
    #         print("running from session level...")
    #         print("session_container is : ", session_container.label)
    # else:
    #     parent_id = config.get("inputs", {}).get("axi", {}).get("hierarchy", {}).get("id")
    #     parent = fw.get(parent_id)
    #     print(parent.parents)
    #     # get the session id from the parent
    #     session_id = parent.parents.session
    #     session_container = fw.get(session_id)
    #     print("session_container is : ", session_container.label)

    # # --- fast vs slow --- #
    # speed = 'standard'
    # for file in os.listdir('/flywheel/v0/input/axi/'):
    #     if fnmatch.fnmatch(file, '*Fast*'):
    #         speed = 'Fast'
    #     else:
    #         speed = 'standard'

    # if speed == 'Fast':
    #     # get the acquisition from the session
    #     for acq in session_container.acquisitions.iter():
    #         if 'T2' in acq.label: # restrict to T2 acquisitions
    #             for file in acq.files: # get the files in the acquisition
    #                 # Screen file object information & download the desired file
    #                 if file['type'] == 'nifti' and 'T2' in file.name and 'Fast' in file.name:
    #                     if 'SAG' in file.name:
    #                         sag = file
    #                         print("sag is : ", sag.name)
    #                         download_dir = ('/flywheel/v0/input/sag')
    #                         if not os.path.exists(download_dir):
    #                             os.mkdir(download_dir)
    #                         download_path = download_dir + '/' + sag.name
    #                         sag.download(download_path)

    #                     elif 'COR' in file.name:
    #                         cor = file
    #                         print("cor is : ", cor.name) 
    #                         download_dir = ('/flywheel/v0/input/cor')
    #                         if not os.path.exists(download_dir):
    #                             os.mkdir(download_dir)
    #                         download_path = download_dir + '/' + cor.name
    #                         cor.download(download_path)

    # elif speed == 'standard':
    #     # get the acquisition from the session
    #     for acq in session_container.acquisitions.iter():
    #         if 'T2' in acq.label: # restrict to T2 acquisitions
    #             for file in acq.files: # get the files in the acquisition
    #                 # Screen file object information & download the desired file
    #                 if file['type'] == 'nifti' and 'T2' in file.name and 'Fast' not in file.name:
    #                     if 'SAG' in file.name:
    #                         sag = file
    #                         print("sag is : ", sag.name)
    #                         download_dir = ('/flywheel/v0/input/sag')
    #                         if not os.path.exists(download_dir):
    #                             os.mkdir(download_dir)
    #                         download_path = download_dir + '/' + sag.name
    #                         sag.download(download_path)

    #                     elif 'COR' in file.name:
    #                         cor = file
    #                         print("cor is : ", cor.name) 
    #                         download_dir = ('/flywheel/v0/input/cor')
    #                         if not os.path.exists(download_dir):
    #                             os.mkdir(download_dir)
    #                         download_path = download_dir + '/' + cor.name
    #                         cor.download(download_path)
                    