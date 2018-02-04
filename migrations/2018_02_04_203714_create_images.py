from orator.migrations import Migration

class CreateImages(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('images') as table:
            table.increments('pk')
            table.timestamps()
            table.soft_deletes()

            table.string("name").unique()
            table.string("bucket")
            table.string("title").nullable()
            table.text("description").nullable()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('images')
