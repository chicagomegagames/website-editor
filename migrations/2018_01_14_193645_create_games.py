from orator.migrations import Migration


class CreateGames(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('games') as table:
            table.increments('pk')
            table.timestamps()
            table.soft_deletes()

            table.string("name").unique()
            table.boolean("show_quick_facts").default(False)
            table.boolean("hidden").default(True)
            table.string("layout").default("game.html")

            table.string("slug").unique()

            table.text("markdown")

            table.text("blurb").nullable()
            table.string("control_count").nullable()
            table.text("credits").nullable()
            table.string("game_length").nullable()
            table.string("hero_image").nullable()
            table.string("logo_image").nullable()
            table.string("player_count").nullable()
            table.string("preview_image").nullable()
            table.string("subtitle").nullable()


    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('games')
