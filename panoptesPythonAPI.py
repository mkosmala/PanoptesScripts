#!/usr/bin/python

import urllib2 
import cookielib
import json
import re
import string
import requests
import csv

# Remote host set to the panoptes staging API
global host,hostapi
host = "https://panoptes-staging.zooniverse.org/"
hostapi = "https://panoptes-staging.zooniverse.org/api/"

def get_bearer_token(user_name,password):
    "Logs user in and gets a bearer token for the given user"

    # look like you're a zooniverse front end client
    app_client_id="535759b966935c297be11913acee7a9ca17c025f9f15520e7504728e71110a27"

    #0. Establish a cookie jar
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    #1. get the csrf token
    request = urllib2.Request(host+"users/sign_in",None)
    response = opener.open(request)
    body = response.read()

    # grep for csrf-token
    csrf_line = re.findall(".+csrf-token.+",body)[0]
    # and extract it
    first = string.find(csrf_line,'content="') + 8
    second = string.find(csrf_line,'"',first+1)
    csrf_token = csrf_line[first+1:second]

    #2. use the token to get a devise session via JSON stored in a cookie
    devise_login_data=("{\"user\": {\"display_name\":\""+user_name+"\",\"password\":\""+password+
                       "\"}, \"authenticity_token\": \""+csrf_token+"\"}")
    request = urllib2.Request(host+"users/sign_in",data=devise_login_data)
    request.add_header("Content-Type","application/json")
    request.add_header("Accept","application/json")

    try:
        response = opener.open(request)
    except urllib2.HTTPError as e:
        print 'In get_bearer_token, stage 2:'
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print 'Error response body: ', e.read()
    except urllib2.URLError as e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    else:
        # everything is fine
        body = response.read()

    #3. use the devise session to get a bearer token for API access
    bearer_req_data=("{\"grant_type\":\"password\",\"client_id\":\"" +
                     app_client_id + "\"}")
    request = urllib2.Request(host+"oauth/token",bearer_req_data)
    request.add_header("Content-Type","application/json")
    request.add_header("Accept","application/json")

    try:
        response = opener.open(request)
    except urllib2.HTTPError as e:
        print 'In get_bearer_token, stage 3:'
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print 'Error response body: ', e.read()
    except urllib2.URLError as e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    else:
        # everything is fine
        body = response.read()

    # extract the bearer token
    json_data = json.loads(body)
    bearer_token = json_data["access_token"]
    
    return bearer_token




def get_userid_from_username(user_name,token):
    "Gets a user's ID from a username; returns -1 if none"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.get(hostapi+'users?display_name='+user_name,headers=head)
 
    userid = -1
    data = response.json()
    if len(data["users"])>0:
        userid = data["users"][0]["id"]

    return userid

# depricated. Ooh la la requests, I think I'm in love...
def get_userid_from_username_old(user_name,token):
    "Gets a user's ID from a username; returns -1 if none"

    # info
    request = urllib2.Request(hostapi+"users?login="+user_name,None)
    request.add_header("Accept","application/vnd.api+json; version=1")
    request.add_header("Authorization","Bearer "+token)

    # request
    userid = -1
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        print 'In get_userid_from_username:'
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print 'Error response body: ', e.read()
    except urllib2.URLError as e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    else:
        # everything is fine
        body = response.read()

        # put it in json structure and extract id
        data = json.loads(body)
        if len(data["users"])>0:
            userid = data["users"][0]["id"]
    
    return userid

def get_groupid_from_groupname(group_name,token):
    "Gets a group's ID from a group name; returns -1 if none"

    # info
    request = urllib2.Request(hostapi+"groups?name="+group_name,None)
    request.add_header("Accept","application/vnd.api+json; version=1")
    request.add_header("Authorization","Bearer "+token)

    # request
    groupid = -1
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        print 'In get_groupid_from_groupname:'
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print 'Error response body: ', e.read()
    except urllib2.URLError as e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    else:
        # everything is fine
        body = response.read()

        # put it in json structure and extract id
        data = json.loads(body)
        if len(data["user_groups"])>0:
            groupid = data["user_groups"][0]["id"]
        
    return groupid

def create_group(group_name,token):
    "Create a user group with just a group name"

    values = """
        {
            "user_groups": {
                "name": \"""" + group_name + """\"
            }
        }
        """
    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.post(hostapi+'groups',headers=head,data=values)
    
    data = response.json()
    groupid = data["user_groups"][0]["id"]

    return groupid


# depricated
def create_group_old(group_name,token):
    "Create a user group with just a group name"
    
    values = """
        {
            "user_groups": {
                "name": \"""" + group_name + """\"
            }
        }
        """
    request = urllib2.Request(hostapi+"groups",values)

    # add headers
    request.add_header("Content-Type","application/json")
    request.add_header("Accept","application/vnd.api+json; version=1")
    request.add_header("Authorization","Bearer "+token)
    
   # request
    groupid = -1
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print 'Error response body: ', e.read()
    except urllib2.URLError as e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    else:
        # everything is fine
        body = response.read()

        # put it in json structure and extract id
        data = json.loads(body)
        groupid = data["user_groups"][0]["id"]

    return groupid

def add_user_to_group(groupid,userid,token):
    "Add the given user to the given group"

    values = """
      {
        "users": [
          \"""" + str(userid) + """\"
        ]
      }
    """

    request = urllib2.Request(hostapi+"groups/"+str(groupid)+
                              "/links/users", data=values)

    # add headers
    request.add_header("Content-Type","application/json")
    request.add_header("Accept","application/vnd.api+json; version=1")
    request.add_header("Authorization","Bearer "+token)

    # request
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print 'Error response body: ', e.read()
    except urllib2.URLError as e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    else:
        # everything is fine
        body = response.read()

    return

def get_group_info(groupid,token):
    "Get all the data for a group given its ID"

    request = urllib2.Request(hostapi+"groups/"+str(groupid),None)
    request.add_header("Accept","application/vnd.api+json; version=1")
    request.add_header("Authorization","Bearer "+token)

    # request
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print 'Error response body: ', e.read()
    except urllib2.URLError as e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    else:
        # everything is fine
        body = response.read()

    # put it in json structure and extract id
    data = json.loads(body)
  
    return data

def get_membership_info(memid,token):
    "Get membership info for one user in one group"

    request = urllib2.Request(hostapi+"memberships/"+str(memid),None)
    request.add_header("Accept","application/vnd.api+json; version=1")
    request.add_header("Authorization","Bearer "+token)

    # request
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print 'Error response body: ', e.read()
    except urllib2.URLError as e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    else:
        # everything is fine
        body = response.read()

    # put it in json structure and extract id
    data = json.loads(body)
  
    return data    

def get_membership_info_for_group(groupid,token):
    "Get membership information for all group members"

    groupinfo = get_group_info(groupid,token)
    mems = groupinfo["user_groups"][0]["links"]["memberships"]

    mem_info = []
    for mem in mems:
        print mem
        info = get_membership_info(mem,token)
        print info
        mem_info.append(info["memberships"][0])

    return mem_info

def create_group_project(groupid,projname,projdesc,token):
    "Create a project owned by a group"

    # project request
    values = """
    {
        "projects": {
            "name": \"""" + projname + """\",
            "description": \"""" + projdesc + """\",
            "primary_language": "en-us",
            "links": {
                "owner": {
                    "id": \""""+ str(groupid) + """\",
                    "type": "user_groups"
                }
            }
        }
    }"""

    request = urllib2.Request(hostapi+"projects",data=values)

    request.add_header("Content-Type","application/json")
    request.add_header("Accept","application/vnd.api+json; version=1")
    request.add_header("Authorization","Bearer "+token)

    # request
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
        print 'Error response body: ', e.read()
    except urllib2.URLError as e:
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    else:
        # everything is fine
        body = response.read()

    # put it in json structure and extract id
    data = json.loads(body)

    projid = data["projects"][0]["id"]
     
    return projid    



def get_projectid_from_projectname(project_name,owner_name,token):
    "Gets a project's ID from a project name; returns -1 if none"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.get(hostapi+'projects?owner='+owner_name+
                            "&display_name="+project_name,
                            headers=head)

    projid = -1
    data = response.json()
    
    if len(data["projects"])>0:
        projid = data["projects"][0]["id"]
    
    return projid






## THIS METHOD IS UNFINISHED
def get_user_projects(user,token):
    "Gets the ids for all a user's projects"
 
    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
   
    response = requests.get(hostapi+'projects?owner='+user,headers=head)   
    
    data = response.json()

    print data

    return


def create_workflow(projid,wfname,tasks,token):
    "Create a Workflow"

    # pull out the first task (after first quotes) (ugly, but works)
    first_task = tasks.split('\"')[1]  

    values = """
        {
            "workflows": {
                "display_name": \"""" + wfname + """\",
                "first_task": \"""" + first_task + """\",
                "tasks": """ + tasks + """,
                "primary_language": "en-us",
                "links": {
                    "project": """ + projid + """
                }
            }
        }
        """

    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}

    response = requests.post(hostapi+'workflows',headers=head,data=values)
    
    data = response.json()    
    workflowid = data["workflows"][0]["id"]

    return workflowid

    


def create_subject(project_id,meta,filename,token):
    "Create a subject and return its ID"

    values = """
    {
        "subjects": {
            "locations": [
                "image/jpeg"
            ],
            "metadata": {
            """ + meta + """
            },
            "links": {
                "project": \"""" + str(project_id) + """\"
            }
        }
    }"""
    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.post(hostapi+'subjects',headers=head,data=values)

    # put it in json structure and extract id
    data = response.json()
    subjid = data["subjects"][0]["id"]
    signed_urls = data["subjects"][0]["locations"][0]["image/jpeg"]

    # -----------
    # now that we have the signed URL, we can upload the file
    # -----------

    head = {'Content-Type':'image/jpeg'}
    with open(filename,'rb') as fp:
        response = requests.put(signed_urls,headers=head,data=fp)
    
    return subjid



def create_subject_set_from_manifest(project_id,display_name,
                                     img_path,manifest_name,token):
    "Create a Subject Set from a manifest of images and metadata"

    # list of ids
    subject_list = []

    # read in from a file a set of subjects
    with open(img_path+manifest_name,'rb') as csvfile:
        freader = csv.reader(csvfile,delimiter=',')
        # header row
        headrow = freader.next()
        for row in freader:
            # file is first
            image_file = img_path+row[0]
            # rest is metadata
            meta_temp = ""
            for label,meta in zip(headrow[1:],row[1:]):
                meta_temp = meta_temp+"\""+label+"\":\""+meta+"\","
            # remove last comma
            meta_str = meta_temp[:-1]

            # create the subject, upload the image, and save the id
            subjid = create_subject(project_id,meta_str,image_file,token)
            subject_list.append(int(subjid))
    
            print "uploaded: "+image_file

    # now we have a list of subject ids; create the subject set
    subj_set_id = create_subject_set(project_id,display_name,subject_list,token)
    return subj_set_id


# OLD                  
#def create_workflow(workflow,token):
#    "Create a Workflow, given the json content"
#    
#    head = {'Content-Type':'application/json',
#            'Accept':'application/vnd.api+json; version=1',
#            'Authorization':'Bearer '+token}
#   
#    response = requests.post(hostapi+'workflows',headers=head,data=workflow)   #
#
#    print "----"
#    print response.request.headers
#    print workflow
#    print "----"
#    print response
#    print response.status_code
#    print response.text
#    print "----"
#    
#    data = response.json()
#
#    workflowid = data["workflows"][0]["id"]
#
#    return workflowid
               



def create_user_project(proj,token):
    "Create a project owned by self"

    info = json.dumps(proj)

    projectinfo = """
        {
            "projects": """ + info + """
        }
        """

    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}

    response = requests.post(hostapi+'projects',headers=head,data=projectinfo)

    print projectinfo
    #print "----"
    #print response.request.headers
    #print "----"
    #print response
    #print response.status_code
    #print response.text
    #print "----"
    
    data = response.json()
    
    projid = data["projects"][0]["id"]

    return projid



def create_subject_set(project_id,display_name,subject_list,token):
    "Create a Subject Set given a list of subject IDs"

    values = """
        {
            "subject_sets": {
                "display_name": \"""" + display_name + """\",
                "links": {
                    "project": \"""" + str(project_id) + """\",
                    "subjects": """ + str(subject_list) + """
                }
            }
        }
        """
    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
   
    response = requests.post(hostapi+'subject_sets',headers=head,data=values)   
    data = response.json()
    subsetid = data["subject_sets"][0]["id"]

    return subsetid


def create_empty_subject_set(project_id,display_name,token):
    "Create an empty Subject Set"

    values = """
        {
            "subject_sets": {
                "display_name": \"""" + display_name + """\",
                "links": {
                    "project": \"""" + str(project_id) + """\" 
                }
            }
        }
        """
    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
   
    response = requests.post(hostapi+'subject_sets',headers=head,data=values)   
    data = response.json() 
    subsetid = data["subject_sets"][0]["id"]

    return subsetid

def get_subject_set(project_id,display_name,token):
    "Get the requested Subject Set or return -1"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    
    response = requests.get(hostapi+"subject_sets?" +
                            "page_size=50" +
                            "&project_id="+project_id+
                            "&display_name="+display_name,
                            headers=head)

    subjsetid = -1
    data = response.json()

    if len(data["subject_sets"])>0:

        # check each one until can filter by display_name
        for ss in data["subject_sets"]:
            if ss["display_name"] == display_name:
                subjsetid = ss["id"]

    return subjsetid




#def add_subject_to_subject_set(subject_set_id,subject_id,token):
#    "Add a given Subject to a given SubjectSet"
#
#    values = """
#        {
#            "subjects": [ """ + subject_id + """ ]
#        }
#        """
#    head = {'Content-Type':'application/json',
#            'Accept':'application/vnd.api+json; version=1',
#            'Authorization':'Bearer '+token}
#   
#    response = requests.post(hostapi+'subject_sets/'+subject_set_id+'/links/subject',
#                             headers=head,data=values)
#
#
#    print "trying to add subject " + subject_id + " to subject set " + subject_set_id + "\n"
#    print response
#    
#    data = response.json()
#    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
#    exit(1)
#    
#    return


def add_subject_to_subject_set(subject_set_id,subject_id,token):
    "Add a given Subject to a given SubjectSet"

    values = """
        {
            "set_member_subjects": {
                "links": {
                    "subject": """ + subject_id + """,
                    "subject_set": """ + subject_set_id + """
                }
            }
        }
        """
    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
   
    response = requests.post(hostapi+'set_member_subjects',headers=head,data=values)

#    print "trying to add subject " + subject_id + " to subject set " + subject_set_id + "\n"    
#    data = response.json()
#    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
#    print "\n\nSubjectSet:\n"
#    dump_subject_set(subject_set_id,token)
#    exit(1)
    
    return


def get_project_subject_sets(projid,token):
    "Return all the subject set IDs for this project"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    
    response = requests.get(hostapi+'subject_sets?page_size=50' +
                            '&project_id='+projid,
                            headers=head)
    data = response.json()

    # initialize the return list
    toret = []

    if len(data["subject_sets"])>0:

        # add all the IDs
        for ss in data["subject_sets"]:
            toret.append(ss["id"])

    return toret


def get_subject_set_name(projid,ssid,token):
    "Return the subject set name given its ID"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    
    response = requests.get(hostapi+'subject_sets?project_id='+projid+
                            "&id="+ssid,
                            headers=head)

    data = response.json()

    # check each one until can filter by id
    for ss in data["subject_sets"]:
        if ss["id"] == ssid:
            ssname = ss["display_name"]

    return ssname
    

def get_workflow(projid,wfname,token):
    "Return the workflow ID given its name. Return -1 if it doesn't exist"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    
    response = requests.get(hostapi+'workflows?project_id='+projid+
                            "&display_name="+wfname,
                            headers=head)

    workflowid = -1
    data = response.json()

    if len(data["workflows"])>0:

        # check each one until can filter by display_name
        for wf in data["workflows"]:
            if wf["display_name"] == wfname:
                workflowid = wf["id"]

    return workflowid
    

def link_subject_set_and_workflow(ssid,wfid,token):
    "Link the given subject set to the given workflow"

    values = """
        {
            "subject_sets": [ \"""" + ssid + """\" ]
        }
        """
    
    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
   
    response = requests.post(hostapi+'workflows/'+str(wfid)+'/links/subject_sets',
                             headers=head,data=values)   

    return


# NOT FINISHED
def duplicate_subject_set(ssid,token):
    "Create a duplicate subject set for the same project and return its ID"

    # get the passsed subject set
    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.get(hostapi+'subject_sets?id='+str(ssid),
                            headers=head)
    data = response.json()
    oldname = data["subject_sets"][0]["display_name"]
    proj_id = data["subject_sets"][0]["links"]["project"]
    #!!! Should copy retirement rules, too, but not ready for that yet

    # increment the name
    if len(oldname) > 7 and oldname[-6:-1]=="_copy":
        ind = int(oldname[-1])
        ind = ind + 1
        newname = oldname[0:-1] + str(ind)
    else:
        newname = oldname + "_copy1"
        
    # get the linked subjects to the passed subject set
    # issue of many, many subjects... and per_page
    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.get(hostapi+'set_member_subjects?subject_set_id='+str(ssid),
                            headers=head)
    data = response.json()
    
    return
       
    


def debug_response(values,response):
    "For debugging"
    
    print "URL: " + response.url + "\n"
    print "Payload: " + values + "\n"
    print "Headers: " + str(response.request.headers) + "\n"
    print "Status code: " + str(response.status_code) + "\n"
    print "Response headers: " + str(response.headers) + "\n"
    print "Response text: " + response.text + "\n"
    return    


# OBSOLETE
def set_science_case(projid,science_case,token):
    "Add or change the science case"

    values = """
        {
            "projects": {
                "science_case": \"""" + science_case + """\"
            }
        }
        """
    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}

    response = requests.post(hostapi+'projects/'+projid,headers=head,data=values)

    debug_response(values,response)
    
    return 
    

# OBSOLETE
def set_introduction(projid,intro,token):
    "Add or change the introduction"

    values = """
        {
            "project_contents": {
                "introduction": \"""" + intro + """\"
            }
        }
        """
    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}

    response = requests.post(hostapi+'project_contents/'+projid,headers=head,data=values)

    debug_response(values,response)
    
    return 

def add_collaborator(projid,person_id,token):
    "Add a collaborator to the given project"

    values = """
        {
            "project_roles": {
                "roles": ["collaborator"],
                "links": {
                    "project": \"""" + str(projid) + """\",
                    "user": \"""" + str(person_id) + """\"
                }
            }
        }
        """
    head = {'Content-Type':'application/json',
            'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}

    response = requests.post(hostapi+'project_roles',headers=head,data=values)

    #data = response.json()
    #print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    #debug_response(values,response)
    
    return

def dump_project(project_name,owner_name,token):
    "Print all the content from a project"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.get(hostapi+'projects?owner='+owner_name+
                            "&display_name="+project_name,
                            headers=head)

    data = response.json()

    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    return 
    
def dump_workflow(workflow_id,token):
    "Print all the content from a workflow"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.get(hostapi+'workflows?id='+str(workflow_id),
                            headers=head)

    data = response.json()

    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    return 


def dump_subject_set(subjectset_id,token):
    "Print all the content from a subject set"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.get(hostapi+'subject_sets?id='+str(subjectset_id),
                            headers=head)

    data = response.json()

    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    return 



def dump_all_projects(owner_name,token):
    "Print the id and name of all the projects owned by owner"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.get(hostapi+'projects?per_page=50&owner='+owner_name,
                            headers=head)

    data = response.json()

    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    for proj in data["projects"]:
        print proj["id"] + ": " + proj["display_name"]
    
    return 

def dump_project_contents(proj_id,token):
    "Print all the contents of a project"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token}
    response = requests.get(hostapi+'project_contents?id='+str(proj_id),
                            headers=head)

    data = response.json()

    print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    return 
    


def delete_project(proj_id,token):
    "Delete the project with the given ID"

    head = {'Accept':'application/vnd.api+json; version=1',
            'Authorization':'Bearer '+token,
            'If-Match':str(proj_id)}
    response = requests.delete(hostapi+'projects/'+str(proj_id),
                               headers=head)

    print response.json()    

    return    


    
