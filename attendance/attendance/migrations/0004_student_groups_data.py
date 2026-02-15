# Generated manually for data migration

from django.db import migrations, models
import django.db.models.deletion


def migrate_students_to_groups(apps, schema_editor):
    """Create one group per class and assign existing students to it."""
    Class = apps.get_model('attendance', 'Class')
    Group = apps.get_model('attendance', 'Group')
    Student = apps.get_model('attendance', 'Student')
    for c in Class.objects.all():
        code = f"{c.code}-1"
        # avoid duplicate code if migration is re-run
        if not Group.objects.filter(code=code).exists():
            g = Group.objects.create(code=code, name=c.name or "", class_enrolled=c)
            Student.objects.filter(class_enrolled=c).update(group=g)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_add_groups'),
    ]

    operations = [
        migrations.RunPython(migrate_students_to_groups, noop),
        migrations.RemoveField(
            model_name='student',
            name='class_enrolled',
        ),
        migrations.AlterField(
            model_name='student',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='attendance.group'),
        ),
    ]
