import app.models as models
from orator.orm import Factory

factory = Factory()

@factory.define(models.Game)
def game_factory(faker):
    return {
        'name': faker.sentence(),
        'markdown': faker.text(),
    }

@factory.define(models.Page)
def page_factory(faker):
    return {
        'name': faker.sentence(),
        'markdown': faker.text(),
        'slug': faker.slug(),
        'layout': 'page.html',
    }

@factory.define(models.Event)
def event_factory(faker):
    return {
        'name': faker.sentence(),
        'date': faker.date(),
        'location': faker.city(),
        'markdown': faker.text(),
    }

@factory.define(models.Image)
def image_factory(faker):
    return {
        'bucket': 'test_bucket',
    }
