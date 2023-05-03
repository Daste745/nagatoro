from discord.ui import Button, View

from nagatoro.extensions.anilist.models import Media


class MediaButtonsView(View):
    def __init__(self, media: Media) -> None:
        super().__init__()

        if media_url := media.site_url:
            self.add_item(Button(url=media_url, label="Open on AniList"))
            characters_url = f"{media_url}/characters"
            self.add_item(Button(url=characters_url, label="Characters"))
