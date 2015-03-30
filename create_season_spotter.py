#!/usr/bin/python

import panoptesPythonAPI
import csv
import os


# TO DO
# create Season Spotter project under my userid
# create Workflows
# create Subjects and SubjectSets and assign to workflows
#    (A SubjectSet belongs to one Workflow, while a single Workflow may have many SubjectSets.)
# add science text (in Markdown)
# add other users after they have created accounts

# this file contains all the images and relevent metadata,
# including the subject set to which they each belong
manifestfile = "beta_manifest_short.csv"
workflow_dir = "workflows/"
linkfile = "subjectsets_and_workflows.csv"



#project = "Season Spotter"
project = "Spotter16"


byline = "default byline"
introduction = "default introduction"
science = "default science case"
education = "useful for education"
faq = "frequently asked questions"
guide = "spot the seasons"
results = "no results yet"



# vegetation type lookup
veg_lookup = { "AG":"Agriculture",
               "DB":"Deciduous Broadleaf Forest",
               "DN":"Deciduous Needle-leaf Forest",
               "EB":"Evergreen Broadleaf Forest",
               "EN":"Evergreen Needle-leaf Forest",
               "GR":"Grassland",
               "MX":"Mixed Forest",
               "SH":"Shrubland",
               "TN":"Tundra",
               "WL":"Wetland" }

# subject sets that should get split into simple and complex workflows
use_twice = [ "DB_year","EB_year","SH_year","DN_year","EN_year","GR_year",
              "WL_year","AG_year" ]





#---
# Create the workflows
#---
def create_workflows(projid,token):
    workflows = os.listdir(workflow_dir)

    # load in each workflow
    for wf in workflows:

        wf_path = workflow_dir + wf
        with open(wf_path,'r') as wffile:
            workflow = wffile.read().replace('\n', '')

            wfname = wf.split('.')[0]

            # and build it
            print "Building workflow: " + wfname
            panoptesPythonAPI.create_workflow(projid,wfname,workflow,token)

    return

# ---
# Create subject sets and upload the images
# ---
def create_subject_sets_and_subjects(projid,token):
    # read the manifest
    with open(manifestfile,'r') as mfile:

        # discard header and get csv object
        mfile.readline()
    
        # for each image
        mreader = csv.reader(mfile,delimiter=',',quotechar='\"')
        for row in mreader:
            image = row[0]
            subjset = row[1]
            site = row[2]
            vegabbr = row[3]
            loc = row[4]
            lat = row[5]
            lon = row[6]
            ele = row[7]

            # look up the vegetation type
            if vegabbr in veg_lookup:
                vegtype = veg_lookup[vegabbr]
            else:
                vegtype = vegabbr

            # check to see if the subject set exists; create it if not
            subjsetnum = panoptesPythonAPI.get_subject_set(projid,subjset,token)
            if subjsetnum == -1:
                print "Building SubjectSet: " + subjset 
                subjsetnum = panoptesPythonAPI.create_empty_subject_set(projid,subjset,token)

            # create the metadata object
            meta = """ "Camera": \"""" + site + """\",
                       "Location": \"""" + loc + """\",
                       "Vegetation": \"""" + vegtype + """\",
                       "Latitute": \"""" + lat + """\",
                       "Longitude": \"""" + lon + """\",
                       "Elevation": \"""" + ele + """\" """

            # create the subject
            print "Adding Subject: " + image
            subjid = panoptesPythonAPI.create_subject(projid,meta,image,token)

            # add it to the subject set(s)
            print "Linking Subject: " + image
            panoptesPythonAPI.add_subject_to_subject_set(subjsetnum,subjid,token)

    return



# ---
# Link SubjectSets to Workflows
# ---
def link_subject_sets_and_workflows(projid,token):

    # initialize the link list
    linklist = []

    # read in the link file
    with open(linkfile,'r') as lfile:

        # ignore header line
        lfile.readline()

        # read in all the pairs
        lreader = csv.reader(lfile,delimiter=',')
        for row in lreader:
            linklist.append(row)

    # get all the subject sets in this project
    subjsetids = panoptesPythonAPI.get_project_subject_sets(projid,token)

    # for each one, link to workflow(s)
    for ssid in subjsetids:

        # get the subjectset name
        ssname = panoptesPythonAPI.get_subject_set_name(projid,ssid,token)

        # look through the links for matches
        for eachpair in linklist:

            # and link the matches
            if eachpair[1] == ssname:

                # get the workflow id
                wfid = panoptesPythonAPI.get_workflow(projid,eachpair[0],token)

                # link
                print "Linking subject set " + ssname + " to workflow " + eachpair[0]
                panoptesPythonAPI.link_subject_set_and_workflow(ssid,wfid,token)

    return
    


########
# MAIN #
########

# get token
token = panoptesPythonAPI.get_bearer_token("mkosmala","hard2guess")

# create the project under my ID
# check to see if it's already created. if not, create it
projid = panoptesPythonAPI.get_projectid_from_projectname(project,"mkosmala",token)
if projid==-1:
    print "Creating project: " + project
    project_info = [project,byline,introduction,science,education,faq,results]
    projid = panoptesPythonAPI.create_user_project(project_info,token)
print "   ID: " + projid + "\n"

# add collaborators

# add project contents
#create_project_contents(projid,token)

# add workflows
create_workflows(projid,token)

# add subject sets
create_subject_sets_and_subjects(projid,token)

# link the subject sets and workflows
link_subject_sets_and_workflows(projid,token)


    


