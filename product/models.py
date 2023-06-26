from django.db import models
from accounts.models import User
from core.models import Team
from django.utils.text import slugify


# Create your models here.


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProductArea(TimeStamp):
    name = models.CharField(default='Product Area', max_length=512)
    slug = models.SlugField(null=True, blank=True)

    product_area_creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='product_area_creator')
    product_area_lead = models.ForeignKey(User, on_delete=models.PROTECT, related_name='product_area_lead')

    teams = models.ManyToManyField(Team, through='ProductAreaTeams')
    members = models.ManyToManyField(User, through='ProductAreaMembers')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(ProductArea, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class ProductAreaTeams(TimeStamp):
    Team = models.ForeignKey(Team, on_delete=models.CASCADE)
    Product_Area = models.ForeignKey(ProductArea, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.Team} / {self.Product_Area}'

    class Meta:
        unique_together = ('Team', 'Product_Area')


class ProductAreaMembers(TimeStamp):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Product_Area = models.ForeignKey(ProductArea, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.User} / {self.Product_Area}'

    class Meta:
        unique_together = ('User', 'Product_Area')


class Product(TimeStamp):
    name = models.CharField(default='Product', max_length=512)
    slug = models.SlugField(null=True, blank=True)

    product_creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='product_creator')
    product_lead = models.ForeignKey(User, on_delete=models.PROTECT, related_name='product_lead')

    product_areas = models.ManyToManyField(ProductArea, through='ProductTeams')
    members = models.ManyToManyField(User, through='ProductMembers')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class ProductTeams(TimeStamp):
    Product_Area = models.ForeignKey(ProductArea, on_delete=models.CASCADE)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.Product_Area} / {self.Product}'

    class Meta:
        unique_together = ('Product_Area', 'Product')


class ProductMembers(TimeStamp):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.User} / {self.Product}'

    class Meta:
        unique_together = ('User', 'Product')


class Enterprise(TimeStamp):
    owner = models.OneToOneField(User, on_delete=models.PROTECT, related_name='Enterprise')
    products = models.ManyToManyField(Product, through='EnterpriseProducts')

    def __str__(self):
        return f'{self.owner} / {self.products.all()}'


class EnterpriseProducts(TimeStamp):
    Enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.Enterprise} / {self.Product}'

    class Meta:
        unique_together = ('Enterprise', 'Product')
