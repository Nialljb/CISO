"""Parser module to parse gear config.json."""

from typing import Tuple
from flywheel_gear_toolkit import GearToolkitContext

def findAge(file_obj):
    file_obj = file_obj.reload()
    # print("file_obj: ", file_obj)
    sessionID = file_obj.parents['session']
    session = fw.get(sessionID)
    print("session: ", session.label)

    if 'PatientBirthDate' in file_obj.info:
        # Get dates from dicom header
        dob = file_obj.info['PatientBirthDate']
        seriesDate = file_obj.info['SeriesDate']
        # Calculate age at scan
        age = (datetime.strptime(seriesDate, '%Y%m%d')) - (datetime.strptime(dob, '%Y%m%d'))
        age = age.days
    elif 'PatientAge' in file_obj.info:
        print("No DOB in dicom header! Trying PatientAge...")
        age = file_obj.info['PatientAge']
        # Need to drop the 'D' from the age and convert to int
        age = re.sub('\D', '', age)
        age = int(age)
    elif session.age != None:
        print("No DOB or age in dicom header! Checking session infomation label...")
        age = int(session.age / 365 / 24 / 60 / 60) # This is in seconds
    else:
        print("No age at scan in session info label! Ask PI...")
        age = 0
    # Make sure age is positive
    if age < 0:
        age = age * -1

    return age

def parse_config(
    gear_context: GearToolkitContext,
) -> Tuple[str]:
    """Parses the config info.
    Args:
        gear_context: Context.

    Returns:
        Tuple of target_template

    """
    target_template = gear_context.config.get("target_template")
    if target_template is None:
        print("target_template is not defined in config.")
        
        findAge(file_obj)












    return target_template