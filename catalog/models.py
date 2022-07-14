from django.db import models

from django.urls import reverse #Используется для создания URL-адресов путем изменения шаблонов URL-адресов.

class Genre(models.Model):
    """
    Модель представляет жанр книги (например Science Fiction, Non Fiction).
    """
    name = models.CharField(
        max_length=200,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)"
        )

    def __str__(self):
        """
        Строка для представления объекта Модели (В админке, например)
        """
        return self.name

class Language(models.Model):
    """Модель, представляющая язык (например, английский, французский, японский и т. д.)"""
    name = models.CharField(max_length=200,
                            help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    def __str__(self):
        """Строка для представления объекта модели (в админке и т. д.)"""
        return self.name

class Book(models.Model):
    """
    Модель представляет книгу (но не отдельную копию книги).
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # Foreign Key используется, потому что у книги может быть только один автор, но у авторов может быть несколько книг.
    # Author как строка, а не как объект, потому что он еще не объявлен в файле.
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    # ManyToManyField потому что жанр может содержать много книг. Книги могут охватывать множество жанров.
    # Genre класс уже определен, поэтому мы можем указать объект выше.
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['title', 'author']

    def display_genre(self):
        """Создает строку для жанра. Это необходимо для отображения жанра в Admin."""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])
        
    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        """
        Возвращает URL-адрес для доступа к определенному экземпляру книги.
        """
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        """
        Строка для представления объекта Модели.
        """
        return self.title

import uuid # Требуется для уникальных экземпляров книги.

from datetime import date

from django.contrib.auth.models import User  # Требуется для назначения Пользователя заемщиком.


class BookInstance(models.Model):
    """
    Модель, представляющая конкретный экземпляр книги (т. е. который можно взять в библиотеке).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        """Определяет, является ли книга просроченной, на основе даты выполнения и текущей даты."""
        return bool(self.due_back and date.today() > self.due_back)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Book availability')

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)


    def __str__(self):
        """
        Строка для представления объекта Модели.
        """
        return '{0} ({1})'.format (self.id, self.book.title)

class Author(models.Model):
    """
    Модель представляет автора.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """
        Возвращает URL-адрес для доступа к конкретному экземпляру автора.
        """
        return reverse('author-detail', args=[str(self.id)])


    def __str__(self):
        """
        Строка для представления объекта Модели.
        """
        return '{0} ({1})'.format (self.last_name, self.first_name)