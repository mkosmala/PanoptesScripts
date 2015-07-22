#!/usr/bin/python

import panoptesPythonAPI
import csv
import os
import json


# TO DO
# add other users after they have created accounts

# ------------------
# FILES WITH CONTENT
# ------------------

manifestfile = "beta_manifest.csv"
#manifestfile = "beta_manifest_mini.csv"
workflow_dir = "workflows/"
linkfile = "subjectsets_and_workflows.csv"
auth = "authentication.txt"

byline_simple = "metatext/byline_simple.txt"
byline_complex = "metatext/byline_complex.txt"
introduction_simple = "metatext/introduction_simple.txt"
introduction_complex = "metatext/introduction_complex.txt"
science = "metatext/science_case.txt"
faq = "metatext/faq.txt"
education = "metatext/education_content.txt"
results = "metatext/results.txt"

logo = "https://raw.githubusercontent.com/mkosmala/SeasonSpotterLanding/gh-pages/projectimages/SeasonSpotter_logo_small.png"
background = "https://raw.githubusercontent.com/mkosmala/SeasonSpotterLanding/gh-pages/projectimages/tamaracks_fall_RNC_cropped_1024x768.jpg"


# ------------------------------
# PROJECT NAME AND COLLABORATORS
# ------------------------------

project_simple = "Season Spotter BASIC Beta1"
project_complex = "Season Spotter DETAILS Beta1"
collaborators = ["imaginaryfriend"]

# -----------
# DEFINITIONS
# -----------

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



#---
# Add collaborators
#---
def add_collaborators(projids,token):

    # add each collaborator
    for coll in collaborators:

        # look up their ID
        collid = panoptesPythonAPI.get_userid_from_username(coll,token)
        if collid == -1:
            print "Warning! User \"" + coll + "\" does not exist. Cannot add as collaborator."

        else:
            print "Adding collaborator: " + coll + ", ID: " + str(collid)
            for projid in projids:
                panoptesPythonAPI.add_collaborator(projid,collid,token)

    return


#---
# Create the workflows
#---
def create_workflows(projids,token):
    #workflows = os.listdir(workflow_dir)
    with open(linkfile,'r') as lfile:

        # discard header
        lfile.readline()

        # keep track of workflows already done
        donewf = []

        # go through each line
        lreader = csv.reader(lfile,delimiter=',',quotechar='\"')
        for row in lreader:

            wfname = row[0]
            wfset = row[2]

            # do new workflows
            if wfname not in donewf:

                wf_path = workflow_dir + wfname + ".txt"
                with open(wf_path,'r') as wffile:
                    workflow = wffile.read().replace('\n', '')

                # add this workflow to the correct project
                wfproj = projids[0]
                if wfset == "complex":
                    wfproj = projids[1]
                        
                # and build it
                print "Building workflow " + wfname + " in project " + wfproj
                wfid = panoptesPythonAPI.create_workflow(wfproj,wfname,workflow,token)
                print "   ID: " + wfid

                # record that we've done this workflow
                donewf.append(wfname)

    return

# ---
# Create subject sets and upload the images
# ---
def create_subject_sets_and_subjects(projids,token):

    # create a dictionary of which project to use for each subject set
    ssproj = {}
    with open(linkfile,'r') as lfile:
        
        # discard header
        lfile.readline()

        # go through each line and add to dictionary
        lreader = csv.reader(lfile,delimiter=',',quotechar='\"')
        for row in lreader:
            ssproj[row[1]] = projids[0]
            if row[2]=="complex":
                ssproj[row[1]] = projids[1]
    
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

            # check to see if the subject set(s) exists; create it if not
            subjsetnum = panoptesPythonAPI.get_subject_set(ssproj[subjset],subjset,token)
            if subjsetnum == -1:
                print "Building SubjectSet: " + subjset
                subjsetnum = panoptesPythonAPI.create_empty_subject_set(ssproj[subjset],subjset,token)
                
            # create the metadata object
            meta = """ "Camera": \"""" + site + """\",
                       "Location": \"""" + loc + """\",
                       "Vegetation": \"""" + vegtype + """\",
                       "Latitute": \"""" + lat + """\",
                       "Longitude": \"""" + lon + """\",
                       "Elevation": \"""" + ele + """\" """

            # create the subject
            print "Adding Subject: " + image
            subjid = panoptesPythonAPI.create_subject(ssproj[subjset],meta,image,token)

            # add it to the subject set(s)
            print "Linking Subject " + image + " to Subject Set " + subjset
            panoptesPythonAPI.add_subject_to_subject_set(subjsetnum,subjid,token)
        
    return



# ---
# Link SubjectSets to Workflows
# ---
def link_subject_sets_and_workflows(projids,token):

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

    # for both projects
    for projid in projids:

        # get all the subject sets in this project
        subjsetids = panoptesPythonAPI.get_project_subject_sets(projid,token)

        # for each subject set, link to workflow(s)
        for ssid in subjsetids:

            #print "\nssid = " + str(ssid)

            # get the subjectset name
            ssname = panoptesPythonAPI.get_subject_set_name(projid,ssid,token)

            #print "   " + ssname

            #foundmatch = False
            # look through the links for workflow matches
            for eachpair in linklist:

                filewf = eachpair[0]
                filess = eachpair[1]

                # and link the matches
                if filess == ssname:

                    # get the workflow id
                    wfid = panoptesPythonAPI.get_workflow(projid,filewf,token)

                    # link
                    print "Linking subject set " + ssname + " to workflow " + filewf
                    panoptesPythonAPI.link_subject_set_and_workflow(ssid,wfid,token)
            
                    #foundmatch = True    

           #if not foundmatch:
           #     print "   no matching workflow found for subjectset: " + ssname

    return
    

def build_project_info(projtype):

    info = {}
    
    # simple
    if projtype == "simple":
        
        info["display_name"] = project_simple

        with open (byline_simple, "r") as infile:
            info["description"] = infile.read()

        with open (introduction_simple, "r") as infile:
            info["introduction"] = infile.read()

    # complex
    else:
        
        info["display_name"] = project_complex

        with open (byline_complex, "r") as infile:
            info["description"] = infile.read()

        with open (introduction_complex, "r") as infile:
            info["introduction"] = infile.read()
        

    with open (science, "r") as infile:
        info["science_case"] = infile.read()

    with open (faq, "r") as infile:
        info["faq"] = infile.read()

    with open (education, "r") as infile:
        info["education_content"] = infile.read()

    #with open (results, "r") as infile:
    #    info["result"] = infile.read()

    info["avatar"] = logo
    info["background_image"] = background
    info["primary_language"] = "en-us"
    info["private"] = False
    #info["beta"] = True
    #info["live"] = True

    # for testing
    #info["configuration"] = {'user_chooses_workflow':True}

    # for production
    info["configuration"] = {'user_chooses_workflow':False}

    return info


########
# MAIN #
########

# get token
with open(auth,'r') as authfile:
    areader = csv.reader(authfile,delimiter=',')
    row = areader.next()
    username = row[0]
    password = row[1]

token = panoptesPythonAPI.get_bearer_token(username,password)

# create a project for simple workflows
# check to see if it's already created. if not, create it
projid_simp = panoptesPythonAPI.get_projectid_from_projectname(project_simple,username,token)
if projid_simp==-1:
    print "Creating project: " + project_simple
    project_info = build_project_info("simple")
    projid_simp = panoptesPythonAPI.create_user_project(project_info,token)
else:
    print "Project already exists: " + project_simple
    exit(0)    
print "   ID: " + projid_simp

# create a project for complex workflows
# check to see if it's already created. if not, create it
projid_comp = panoptesPythonAPI.get_projectid_from_projectname(project_complex,username,token)
if projid_comp==-1:
    print "Creating project: " + project_complex
    project_info = build_project_info("complex")
    projid_comp = panoptesPythonAPI.create_user_project(project_info,token)
else:
    print "Project already exists: " + project_complex
    exit(0)    
print "   ID: " + projid_comp

# put the project ids together
projids = (projid_simp,projid_comp)

# add collaborators
#add_collaborators(projids,token)

# add workflows
create_workflows(projids,token)

# add subject sets
create_subject_sets_and_subjects(projids,token)

# link the subject sets and workflows
link_subject_sets_and_workflows(projids,token)


    


