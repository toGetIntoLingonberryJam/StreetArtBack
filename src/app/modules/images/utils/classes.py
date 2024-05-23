import enum


class ImageModel(str, enum.Enum):
    IMAGE = "image"
    IMAGE_ARTWORK = "image_artwork"
    IMAGE_TICKET = "image_ticket"
