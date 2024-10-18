import flywheel
import json


def get_demo():
    PatientSex = "NA"
    age = 0

    # Read config.json file
    p = open('/flywheel/v0/config.json')
    config = json.loads(p.read())

    # Read API key in config file
    api_key = (config['inputs']['api-key']['key'])
    fw = flywheel.Client(api_key=api_key)
    
    # Get the input file id
    input_file_id = (config['inputs']['axi']['hierarchy']['id'])
    print("input_file_id is : ", input_file_id)
    input_container = fw.get(input_file_id)

    # Get the session id from the input file id
    # & extract the session container
    session_id = input_container.parents['session']
    session_container = fw.get(session_id)
    session = session_container.reload()
    print("subject label: ", session.subject.label)
    print("session label: ", session.label)
    session_label = session.label
    subject_label = session.subject.label

    print("Demographics: ", subject_label, session_label, age, PatientSex)
    return subject_label, session_label