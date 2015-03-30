#!/usr/bin/python

import panoptesPythonAPI


# get token
token = panoptesPythonAPI.get_bearer_token("mkosmala","hard2guess")


#panoptesPythonAPI.dump_all_projects("mkosmala",token)

#panoptesPythonAPI.delete_project(153,token)


#panoptesPythonAPI.dump_project("Spotter14","mkosmala",token)
#for ind in range(379,388):
#    panoptesPythonAPI.dump_workflow(ind,token)
#for ind in range(627,638) :
#    panoptesPythonAPI.dump_subject_set(ind,token)

panoptesPythonAPI.dump_project_contents(186,token)

print "\n"
#panoptesPythonAPI.dump_project("Builder_2015_03_27","mkosmala",token)
#panoptesPythonAPI.dump_workflow(178,token)
#panoptesPythonAPI.dump_subject_set(399,token)
#panoptesPythonAPI.dump_subject_set(400,token)

panoptesPythonAPI.dump_project_contents(170,token)
