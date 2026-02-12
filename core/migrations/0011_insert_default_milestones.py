from django.db import migrations

def insert_milestones(apps, schema_editor):
    Milestone = apps.get_model('core', 'Milestone')
    Child = apps.get_model('core', 'Child')
    ChildMilestone = apps.get_model('core', 'ChildMilestone')

    milestones_data = [
        {"category": "Motor Skills", "description": "Lift head while on tummy", "typical_age": "0-3 months"},
        {"category": "Motor Skills", "description": "Roll over from back to front", "typical_age": "3-6 months"},
        {"category": "Motor Skills", "description": "Sit without support", "typical_age": "6-9 months"},
        {"category": "Motor Skills", "description": "Crawl on hands and knees", "typical_age": "7-10 months"},
        {"category": "Motor Skills", "description": "Stand holding furniture", "typical_age": "8-12 months"},
        {"category": "Motor Skills", "description": "Walk with support", "typical_age": "9-12 months"},
        {"category": "Motor Skills", "description": "Walk independently", "typical_age": "12-15 months"},
        {"category": "Motor Skills", "description": "Run without falling", "typical_age": "18-24 months"},
        {"category": "Language", "description": "Cooing and gurgling", "typical_age": "0-3 months"},
        {"category": "Language", "description": "Babbling begins", "typical_age": "4-6 months"},
        {"category": "Language", "description": "Responds to name", "typical_age": "6-9 months"},
        {"category": "Language", "description": "First words", "typical_age": "10-12 months"},
        {"category": "Language", "description": "Two-word phrases", "typical_age": "18-24 months"},
        {"category": "Language", "description": "Simple sentences", "typical_age": "24-36 months"},
        {"category": "Language", "description": "Uses pronouns (I, me, you)", "typical_age": "24-36 months"},
        {"category": "Social Skills", "description": "Smiles at familiar faces", "typical_age": "2-3 months"},
        {"category": "Social Skills", "description": "Recognizes caregivers", "typical_age": "4-6 months"},
        {"category": "Social Skills", "description": "Plays peek-a-boo", "typical_age": "6-9 months"},
        {"category": "Social Skills", "description": "Shows empathy", "typical_age": "12-18 months"},
        {"category": "Social Skills", "description": "Parallel play with other children", "typical_age": "18-24 months"},
        {"category": "Social Skills", "description": "Engages in cooperative play", "typical_age": "24-36 months"},
        {"category": "Cognitive", "description": "Follows moving objects with eyes", "typical_age": "0-3 months"},
        {"category": "Cognitive", "description": "Explores objects with hands and mouth", "typical_age": "3-6 months"},
        {"category": "Cognitive", "description": "Object permanence understanding", "typical_age": "6-9 months"},
        {"category": "Cognitive", "description": "Points to objects of interest", "typical_age": "12-15 months"},
        {"category": "Cognitive", "description": "Simple problem solving (stacking blocks)", "typical_age": "15-18 months"},
        {"category": "Cognitive", "description": "Recognizes familiar pictures", "typical_age": "18-24 months"},
        {"category": "Cognitive", "description": "Can sort shapes and colors", "typical_age": "24-36 months"},
        {"category": "Cognitive", "description": "Can follow 2-step instructions", "typical_age": "24-36 months"},
        {"category": "Cognitive", "description": "Begins imaginative play", "typical_age": "24-36 months"},
    ]

    for data in milestones_data:
        milestone, created = Milestone.objects.get_or_create(
            description=data['description'],
            defaults={'category': data['category'], 'typical_age': data['typical_age']}
        )
        if not created:
             milestone.category = data['category']
             milestone.typical_age = data['typical_age']
             milestone.save()

    # Now create ChildMilestone entries for all existing children
    all_milestones = Milestone.objects.all()
    all_children = Child.objects.all()

    for child in all_children:
        for milestone in all_milestones:
            ChildMilestone.objects.get_or_create(
                child=child,
                milestone=milestone,
                defaults={'status': 'pending'}
            )

def reverse_insert(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_daycarereview"),
    ]

    operations = [
        migrations.RunPython(insert_milestones, reverse_insert),
    ]
