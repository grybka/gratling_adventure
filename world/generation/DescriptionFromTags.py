#This creates a room description from a set of tags
#The tags are sorted by sense, and the available senses are given during 
#the creation of descriptions
#There are also rules for what tags can be combined
#a tag is simply a string

#TODO No, the tags do not have to be sorted by sense, the tag to text mapping should be sort
#ed by sense.  If a production cannot be done, then it is just left out

from enum import Enum
import yaml

class Sense(Enum):
    SIGHT=1
    SOUND=2
    SMELL=3
    TEMPERATURE=4

class DescriptionTagInfo:
    def __init__(self):
        self.tag_sense_map={}
        #Example
        #self.tag_sense_map['red']=[Sense.SIGHT]
        self.exclusive_tag_sets=[]
        #Example
        #self.exclusive_tag_sets.append(set({'red','blue'}))

    def load_tag_info_file(self,filename):
        #This loads a yaml file that fills out tag_sense_map and exclusive_tag_sets
        #TODO Fix This
        with open(filename,'r') as file:
            data=yaml.load(file)
            self.tag_sense_map=data['tag_sense_map']
            self.exclusive_tag_sets=data['exclusive_tag_sets']


class DescriptionGenerator:
    def __init__(self):
        #This is a list of pairs (set of tags, description)
        self.tags_to_description_rules=[]
        self.tag_info=DescriptionTagInfo()

    def generate_description(self,tags,senses,seed=1):
        #Keep only tags that are relevant to the senses


