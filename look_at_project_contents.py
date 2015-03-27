#!/usr/bin/python

import panoptesPythonAPI


# get token
token = panoptesPythonAPI.get_bearer_token("mkosmala","hard2guess")



#panoptesPythonAPI.dump_project("Spotter5","mkosmala",token)
#panoptesPythonAPI.dump_workflow(193,token)
panoptesPythonAPI.dump_subject_set(417,token)

print "\n"
#panoptesPythonAPI.dump_project("Builder_2015_03_27","mkosmala",token)
#panoptesPythonAPI.dump_workflow(178,token)
panoptesPythonAPI.dump_subject_set(399,token)
