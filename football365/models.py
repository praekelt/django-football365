from django.db import models


class Call(models.Model):
    title = models.CharField(
        max_length=256,
        help_text="A short descriptive title for your reference.",
    )
    call_type = models.CharField(
        max_length=32,
        choices=(
            ('table', 'Table'),
            ('fixtures', 'Fixtures'),
            ('results', 'Results'),
            ('live', 'Live scores')
        )
    )
    football365_service_id = models.PositiveIntegerField(
        help_text="Internal service identifier used by Football365"
    )
    client_id = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text="Override the account name in settings on a per-call basis"
    )

    class Meta:
        ordering = ('title',)

    def __unicode__(self):
        return self.title

