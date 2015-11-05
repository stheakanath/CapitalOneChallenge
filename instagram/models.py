'''
Kuriakose Sony Theakanath - models.py
Capital One Challenge
October 13, 2015

The models.py class represents the objects in instagram, ranging from  
comments, tags, users, images and videos. This class was created to 
organize the objects better 
'''

import six
from datetime import datetime

'''
Creates a Model object from each described below.
'''
class ApiModel(object):
    @classmethod
    def object_from_dictionary(cls, entry):
        if entry is None: return ""
        entry_str_dict = dict([(str(key), value) for key, value in entry.items()])
        return cls(**entry_str_dict)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if six.PY3:
            return self.__unicode__()
        return unicode(self).encode('utf-8')

'''
Image or Video object to distinguish between both
'''
class Image(ApiModel):
    def __init__(self, url, width, height):
        self.url = url
        self.height = height
        self.width = width

    def __unicode__(self):
        return "Image: %s" % self.url

class Video(Image):
    def __unicode__(self):
        return "Video: %s" % self.url

'''
Represents either a Video or Image object. Think of this as the superclass.
'''
class Media(ApiModel):
    def __init__(self, id=None, **kwargs):
        self.id = id
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    def get_low_resolution_url(self):
        if self.type == 'image':
            return self.images['low_resolution'].url
        else:
            return self.videos['low_resolution'].url

    def __unicode__(self):
        return "Media: %s" % self.id

    @classmethod
    def object_from_dictionary(cls, entry):
        new_media = Media(id=entry['id'])
        new_media.type = entry['type']
        new_media.user = User.object_from_dictionary(entry['user'])

        new_media.images = {}
        for version, version_info in six.iteritems(entry['images']):
            new_media.images[version] = Image.object_from_dictionary(version_info)

        if new_media.type == 'video':
            new_media.videos = {}
            for version, version_info in six.iteritems(entry['videos']):
                new_media.videos[version] = Video.object_from_dictionary(version_info)

        if 'user_has_liked' in entry:
            new_media.user_has_liked = entry['user_has_liked']
        new_media.like_count = entry['likes']['count']
        new_media.likes = []
        if 'data' in entry['likes']:
            for like in entry['likes']['data']:
                new_media.likes.append(User.object_from_dictionary(like))

        new_media.comment_count = entry['comments']['count']
        new_media.comments = []
        for comment in entry['comments']['data']:
            new_media.comments.append(Comment.object_from_dictionary(comment))

        new_media.created_time = timestamp_to_datetime(entry['created_time'])

        new_media.caption = None
        if entry['caption']:
            new_media.caption = Comment.object_from_dictionary(entry['caption'])
        
        new_media.tags = []
        if entry['tags']:
            for tag in entry['tags']:
                new_media.tags.append(Tag.object_from_dictionary({'name': tag}))

        new_media.link = entry['link']
        new_media.filter = entry.get('filter')
        return new_media

'''
Represents the hashtags in Instagram
'''
class Tag(ApiModel):
    def __init__(self, name, **kwargs):
        self.name = name
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    def __unicode__(self):
        return "Tag: %s" % self.name

'''
Represents the captions.
'''
class Comment(ApiModel):
    def __init__(self, *args, **kwargs):
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classmethod
    def object_from_dictionary(cls, entry):
        user = User.object_from_dictionary(entry['from'])
        text = entry['text']
        created_at = timestamp_to_datetime(entry['created_time'])
        id = entry['id']
        return Comment(id=id, user=user, text=text, created_at=created_at)

    def __unicode__(self):
        return "Comment: %s said \"%s\"" % (self.user.username, self.text)

'''
Represents the user in Instagram.
'''
class User(ApiModel):
    def __init__(self, id, *args, **kwargs):
        self.id = id
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    def __unicode__(self):
        return "User: %s" % self.username

'''
Helper methods.
'''
def timestamp_to_datetime(ts):
    return datetime.utcfromtimestamp(float(ts))

def datetime_to_timestamp(dt):
    return calendar.timegm(dt.timetuple())

