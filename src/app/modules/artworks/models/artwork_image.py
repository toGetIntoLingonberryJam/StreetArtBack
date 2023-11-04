from datetime import datetime

import pytz
from PIL import Image

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db import Base
from config import settings


class ArtworkImage(Base):
    __tablename__ = "artwork_images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String)
    thumbnail_url = Column(String)  # URL миниатюры
    # is_thumbnail = Column(Boolean, default=False)

    # Отношение к объекту Artwork
    artwork_id = Column(Integer, ForeignKey("artworks.id"))
    artwork = relationship("Artwork", back_populates="images")

    # # Отношение к объекту ArtworkAdditions, через который можно будет обратиться напрямуюк Artwork
    # additions_id = Column(Integer, ForeignKey("artwork_additions.id"))
    # additions = relationship("ArtworkAdditions", back_populates="images")

    created_at = Column(DateTime(timezone=True), default=datetime.now(tz=pytz.UTC), server_default=func.now())

    # def create_thumbnail(self, thumbnail_image_url):
    #     # Позже добавить логику создания миниатюры из исходного изображения
    #     self.thumbnail_url = thumbnail_image_url

    def generate_thumbnail_url(self):

        image_file_name = self.image_url.split(settings.STATIC_IMAGE_FOLDER)[1] # сплит для получения имени файла

        # Открываем большое изображение
        big_image = Image.open(settings.STATIC_IMAGE_FOLDER + image_file_name)

        # Устанавливаем желаемый размер маленького изображения
        small_size = (100, 100)  # Укажите ширину и высоту в пикселях

        # Изменяем размер изображения
        small_image = big_image.resize(small_size)

        small_file_name = "small_" + image_file_name

        # Сохраняем маленькое изображение
        small_image.save(settings.STATIC_IMAGE_FOLDER + small_file_name)

        self.thumbnail_url = settings.BACKEND_URL + settings.STATIC_IMAGE_FOLDER + small_file_name
        return self.thumbnail_url
    # @property
    # def thumbnail_url(self):
    #     if self.thumbnail_url is not None:
    #         return self.thumbnail_url
    #     # Если thumbnail_url пуст, вы можете добавить здесь логику для его автоматического создания
    #     else:
    #         return self.generate_thumbnail_url()
    #
    # @thumbnail_url.setter
    # def thumbnail_url(self, value):
    #     # Если вы хотите сохранить значение в базе данных, раскомментируйте эту часть и замените None на value
    #     # self.thumbnail_url = value
    #     pass
    #
    # def generate_thumbnail_url(self):
    #     pass
        # Здесь вы можете добавить логику для создания миниатюры из исходного изображения и возвращения URL
        # Например:
        # thumbnail_image_url = generate_thumbnail(self.image_url)
        # self.thumbnail_url = thumbnail_image_url
        # return thumbnail_image_url
