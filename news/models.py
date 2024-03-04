from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models import Sum
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.contrib.auth.forms import UserCreationForm
from django import forms
from allauth.account.forms import SignupForm
from django.core.cache import cache


class Author(models.Model):
    # Модель, содержащая объекты всех авторов.
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def update_rating(self):
        postRat = self.post_set
        pRat = 0
        print(postRat, pRat)
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set
        cRat = 0
        print(commentRat, cRat)
        cRat += commentRat.get('commentRating')

        self.ratingAuthor = pRat * 3 + cRat
        self.save()

        author_posts = Post.objects.filter(author=self.id)
        author_posts_rating = 0
        author_posts_comments_rating = 0
        for i in author_posts:
            author_posts_rating += i.rating * 3
            for j in Comment.objects.filter(post=i.id):
                author_posts_comments_rating += j.rating
        author_comments = Comment.objects.filter(author=self.id)
        author_comments_rating = 0
        for i in author_comments:
            author_comments_rating += i.rating
        self.rating = author_posts_rating + author_posts_comments_rating + author_comments_rating
        self.save()

    def __str__(self):
        return f'{self.authorUser.username}'


class Category(models.Model):
    # Категории новостей/статей — темы, которые они отражают (спорт, политика, образование и т. д.)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOISES = (
        (NEWS, 'Новость'),
        (ARTICLE, "Статья"),
    )
    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOISES, default=ARTICLE)
    # автоматически добавляемая дата и время создания
    dateCreation = models.DateTimeField(auto_now_add=True)
    # связь «многие ко многим» с моделью Category - добавить (с дополнительной моделью PostCategory)
    postCategory = models.ManyToManyField(Category, through="PostCategory")
    # доработать может не тот тип заголовок статьи/новости
    title = models.CharField(max_length=255)
    # доработать текст статьи/новости
    text = models.TextField()
    # доработать рейтинг статьи/новости
    rating = models.SmallIntegerField(default=0)


    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + '...'

    def __str__(self):
        return self.title.title()

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

# Под каждой новостью/статьёй можно оставлять комментарии, поэтому необходимо организовать их способ хранения тоже.
class PostCategory (models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.postThrough.title}: {self.categoryThrough.name}'

class AuthorCategory(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment (models.Model):
    # связь «один ко многим» с моделью Post
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    # добавить комментарии может оставить любой пользователь, необязательно автор
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    # доработать
    text = models.TextField()
    # дата и время создания комментария
    dateCreations = models.DateTimeField(auto_now_add=True)
    # рейтинг комментария
    rating = models.SmallIntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'{self.text}'

class Subscriber(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    category = models.ForeignKey(
        to=Category,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )

class CategorySubscribers(models.Model):
    """ Модель ПОДПИСКИ на КАТЕОРИЮ """
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, verbose_name='Категория')
    subscriber_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, verbose_name='Подписчик')
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    # subscriber_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Подписчик')

    def __str__(self):
        # return f"Подписка на категорию: {self.category}, {self.subscriber_user}"
        return f'{self.subscriber_user} подписан на категорию {self.category}'

    class Meta:
        verbose_name = 'Категория подписки'
        verbose_name_plural = 'Категории подписок'

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class MySignupForm(SignupForm):

    def save(self, request):
        user = super(MySignupForm, self).save(request)
        common_group = get(name='common')
        common_group.user_set.add(user)
        return user