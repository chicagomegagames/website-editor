from orator.migrations import Migration


class CreatePages(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('pages') as table:
            table.increments('pk')
            table.timestamps()
            table.soft_deletes()

            table.string("name").unique()
            table.string("slug").unique()
            table.string("layout")

            table.text("markdown")

            table.string("hero_image").nullable()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('pages')
