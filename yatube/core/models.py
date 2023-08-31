from django.db import models


class CreatedModel(models.Model):
    """Abstract model. Adds the creation date."""
    created = models.DateTimeField(
        'Creation date',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
