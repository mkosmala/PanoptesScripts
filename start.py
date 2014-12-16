#!/usr/bin/python

import panoptesPythonAPI
import csv

#group = "project_seasons"

group = "silly_group5"
project = "Fuzzy project"

# get token
token = panoptesPythonAPI.get_bearer_token("mkosmala","hard2guess")

# get user ids
#mkid = panoptesPythonAPI.get_userid_from_username("mkosmala",token)
#rcid = panoptesPythonAPI.get_userid_from_username("rcheng",token)

# get the group
#grpid = panoptesPythonAPI.get_groupid_from_groupname(group,token)

# if the group doesn't exist, create it and add RC
#if grpid==-1:
#    grpid = panoptesPythonAPI.create_group(group,token)
#    panoptesPythonAPI.add_user_to_group(grpid,rcid,token)
        
# get the membership info for everyone in the group
# NOT YET
#meminfo = panoptesPythonAPI.get_membership_info_for_group(grpid,token)
#print meminfo

# see if project already exists and get project id
# NOT YET
#projid = panoptesPythonAPI.get_projectid_from_projectname(project,token)
projid = 64

# if the group project doesn't exist, create it
#if projid==-1:
#    projid = panoptesPythonAPI.create_group_project(grpid,
#                                                    project,
#                                                    "A crazy and silly project",
#                                                    token)

# if the user project doesn't exist, create it
if projid==-1:
    projid = panoptesPythonAPI.create_user_project(project,
                                                "A crazy and silly project",
                                                token)


# create a workflow
# NOT YET
#workflowid = panoptesPythonAPI.create_workflow(token)

# create a subject
meta = """  "Site": "Harvard Forest",
            "Vegetation": "Deciduous Broadleaf Forest",
            "Latitude": "42.5378",
            "Longitude": "-72.1715",
            "Elevation": "340",
            "Camera": "StarDot NetCam SC",
            "Date": "2014-06-03",
            "Time": "12:01:38" """
#subjid = panoptesPythonAPI.create_subject(projid,meta,"test.jpg",token)
#print subjid

# create a subject set
disp_name = "DBF images for Simple tasks Single images workflow"
img_path = "../"
manifest_name = "deciduous_manifest.csv"
#subj_set_id = panoptesPythonAPI.create_subject_set_from_manifest(
#    projid,disp_name,img_path,manifest_name,token)
#print subj_set_id                               

subj_set_id = 41


# now let's create a workflow
workflow = """
{
    "workflows": {
        "display_name": "Flowers",
        "tasks": {
            "valid_image": {
                "type": "single",
                "question": "Can you see any vegetation in this image?",
                "answers": [
                    {"value": "yes", "label": "Yes", "next": "flowers"},
                    {"value": "no", "lable": "No", "next": null}
                ],
                "required": "1"
            },
            "flowers": {
                "type": "single",
                "question": "Are there flowers visible?",
                "answers": [
                    {"value": "yes", "label": "Yes"},
                    {"value": "no", "lable": "No"}
                ],
                "required": "1"
            }
        },
        "first_task": "valid_image",
        "primary_language": "en-us",
        "links": {
            "project": \"""" + str(projid) + """\",
            "subject_sets": [\"""" + str(subj_set_id) + """\"]
        }
    }
}"""

workflow_id = panoptesPythonAPI.create_workflow(workflow,token)

print workflow_id

    

        


