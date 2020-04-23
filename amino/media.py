import requests

from amino.lib.util import exceptions


class NewBlog():
    def __init__(self, title, body, client):
        """
        Build a new blog
        This is still in progress, use SubClient.post_blog() instead in conjunction with MediaItems for any images
        """
        self.title = title,
        self.body = body
        self.media_list = []


class MediaItem():
    def __init__(self, client=None, replace_key=None, caption=None, filename=None,
                 source_file=None, source_url=None, uploaded=None):
        """
        Build the Media Item.
        client: client who owns this media item. Needed for uploading the data to Amino, but can be added later.
        replace_key: alphanumeric string (not separated by spaces, underscores, etc) that will be replaced with this media in an associated blog post.
                     if None, the image will be attached to a blog but not posted in the body. Defaults to None.
        caption: caption to give the media, or None for no caption. Defaults to None
        filename: alternate filename to give this media in a blog post. If None, the replace_key will be used, or if that's also none "file" will be used
        source_file: image filepath (relative to the file where this is imported) to use for the media image
        source_url: image url to use for the media image. This will take precedence over the source_file in the case in which both are provided.
        uploaded: image url that has already been uploaded to amino servers. This will take precedence over source_url
        """
        self.replace_key = replace_key
        self.caption = caption
        self.client = client
        self.fileName = filename if filename else replace_key if replace_key else "file"
        self._source_file = source_file
        self._source_url = source_url
        self._uploaded = uploaded

    @property
    def image(self):
        """
        Get an Amino instance of this media's image.
        will upload the image if it is not already and return that url, or it will return a previously uploaded url
        Returns a url to an Amino-hosted file that can be used in blog posts
        """
        if self._uploaded:
            return self._uploaded

        if self._source_url:
            response = requests.get(self._source_url)

            if response.status_code != 200:
                raise exceptions.CannotFetchImage

            type = response.headers["Content-Type"].split("/")[-1]
            self._uploaded = self.client.upload_image_raw(response.content, type)

        if self._source_file:
            self._uploaded = client.upload_image_path(self._source_file)

        return self._uploaded

    @property
    def media_list_item(self):
        """
        Get a representation of this media's mediaList item. useful for creating blogs
        Returns a list with media data
        """
        # TODO: I still don't know what that second to last field does
        return [100, self.image, self.caption, self.replace_key, None, {
            "fileName": self.fileName
        }]
