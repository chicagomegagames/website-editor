from orator.migrations import Migration


class CreateEvents(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('events') as table:
            table.increments('pk')
            table.timestamps()
            table.soft_deletes()

            table.string("name")
            table.date("date").default("now")
            table.string("location")

            table.text("markdown")

            table.string("time").nullable()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('events')
