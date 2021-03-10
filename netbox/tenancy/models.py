from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

from extras.utils import extras_features
from netbox.models import NestedGroupModel, PrimaryModel
from utilities.mptt import TreeManager
from utilities.querysets import RestrictedQuerySet


__all__ = (
    'Tenant',
    'TenantGroup',
)


@extras_features('custom_fields', 'export_templates', 'webhooks')
class TenantGroup(NestedGroupModel):
    """
    An arbitrary collection of Tenants.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = TreeManager()

    csv_headers = ['name', 'slug', 'parent', 'description']

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return "{}?group={}".format(reverse('tenancy:tenant_list'), self.slug)

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.parent.name if self.parent else '',
            self.description,
        )


@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class Tenant(PrimaryModel):
    """
    A Tenant represents an organization served by the NetBox owner. This is typically a customer or an internal
    department.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    group = models.ForeignKey(
        to='tenancy.TenantGroup',
        on_delete=models.SET_NULL,
        related_name='tenants',
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['name', 'slug', 'group', 'description', 'comments']
    clone_fields = [
        'group', 'description',
    ]

    class Meta:
        ordering = ['group', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:tenant', args=[self.pk])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.group.name if self.group else None,
            self.description,
            self.comments,
        )
