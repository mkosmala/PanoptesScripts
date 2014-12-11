#!/usr/bin/python

import panoptesPythonAPI

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

subjid = panoptesPythonAPI.create_subject(projid,meta,token)
print subjid

