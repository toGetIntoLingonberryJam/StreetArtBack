from datetime import datetime
from PIL import Image

import pytz
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db import Base


class ArtworkImage(Base):
    __tablename__ = "artwork_images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String)
    thumbnail_url = Column(String, nullable=True)  # URL миниатюры
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
        # Открываем большое изображение
        big_image = Image.open("static/shakal.jpg")

        # Устанавливаем желаемый размер маленького изображения
        small_size = (100, 100)  # Укажите ширину и высоту в пикселях

        # Изменяем размер изображения
        small_image = big_image.resize(small_size)

        # Сохраняем маленькое изображение
        small_image.save("static/small_shakal.jpg")

        self.thumbnail_url = "http://localhost:8000/static/small_shakal.jpg"
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