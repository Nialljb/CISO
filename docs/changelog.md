# Changelog
28/03/2023
Add in new templates

19/06/2023
Addapting to take a single required input and find the other two acquistions throuhg the SDK

21/09/2023
Discussion on down/up sampling
https://sourceforge.net/p/advants/discussion/840261/thread/045b1a1d/
- Hyperfine input images are no greater than 1.5mm so could upsample the high res template to this to improve spead. 


24/10/2023
"version": "0.2.1"
- remove unused config options
- Update to include phantom flag

27/10/2023
"version": "0.2.3"
- Updated self-reference phantom processing
- BETA brain self-reference processing
- nifti reader function for voxel dimensions (not called)

10/01/2024
"version": "0.2.5"
- Try to catch and process when there is not three acquisitions
- Add in catch for Fast & standard aquisition