from . import oauth2
from .bind import bind_method
from .models import Media, User, Tag, Comment

MEDIA_ACCEPT_PARAMETERS = ["count", "max_id"]
SEARCH_ACCEPT_PARAMETERS = ["q", "count"]

SUPPORTED_FORMATS = ['json']


class InstagramAPI(oauth2.OAuth2API):

    host = "api.instagram.com"
    base_path = "/v1"
    access_token_field = "access_token"
    authorize_url = "https://api.instagram.com/oauth/authorize"
    access_token_url = "https://api.instagram.com/oauth/access_token"
    protocol = "https"
    api_name = "Instagram"
    x_ratelimit_remaining  = None
    x_ratelimit = None

    def __init__(self, *args, **kwargs):
        format = kwargs.get('format', 'json')
        if format in SUPPORTED_FORMATS:
            self.format = format
        else:
            raise Exception("Unsupported format")
        super(InstagramAPI, self).__init__(**kwargs)

    media_likes = bind_method(
                path="/media/{media_id}/likes",
                accepts_parameters=['media_id'],
                root_class=User)

    like_media = bind_method(
                path="/media/{media_id}/likes",
                method="POST",
                signature=True,
                accepts_parameters=['media_id'],
                response_type="empty")

    unlike_media = bind_method(
                path="/media/{media_id}/likes",
                method="DELETE",
                signature=True,
                accepts_parameters=['media_id'],
                response_type="empty")

    create_media_comment = bind_method(
                path="/media/{media_id}/comments",
                method="POST",
                signature=True,
                accepts_parameters=['media_id', 'text'],
                response_type="empty",
                root_class=Comment)

    delete_comment = bind_method(
                path="/media/{media_id}/comments/{comment_id}",
                method="DELETE",
                signature=True,
                accepts_parameters=['media_id', 'comment_id'],
                response_type="empty")

    media_comments = bind_method(
                path="/media/{media_id}/comments",
                method="GET",
                accepts_parameters=['media_id'],
                response_type="list",
                root_class=Comment)

    media = bind_method(
                path="/media/{media_id}",
                accepts_parameters=['media_id'],
                response_type="entry",
                root_class=Media)

    user_recent_media = bind_method(
                path="/users/{user_id}/media/recent",
                accepts_parameters=MEDIA_ACCEPT_PARAMETERS + ['user_id', 'min_id', 'max_timestamp', 'min_timestamp'],
                root_class=Media,
                paginates=True)

    user_search = bind_method(
                path="/users/search",
                accepts_parameters=SEARCH_ACCEPT_PARAMETERS,
                root_class=User)

    user_follows = bind_method(
                path="/users/{user_id}/follows",
                accepts_parameters=["user_id"],
                paginates=True,
                root_class=User)

    user_followed_by = bind_method(
                path="/users/{user_id}/followed-by",
                accepts_parameters=["user_id"],
                paginates=True,
                root_class=User)

    user = bind_method(
                path="/users/{user_id}",
                accepts_parameters=["user_id"],
                root_class=User,
                response_type="entry")


    tag_recent_media = bind_method(
                path="/tags/{tag_name}/media/recent",
                accepts_parameters=['count', 'max_tag_id', 'tag_name'],
                root_class=Media,
                paginates=True)

    tag_search = bind_method(
                path="/tags/search",
                accepts_parameters=SEARCH_ACCEPT_PARAMETERS,
                root_class=Tag,
                paginates=True)

    tag = bind_method(
                path="/tags/{tag_name}",
                accepts_parameters=["tag_name"],
                root_class=Tag,
                response_type="entry")


