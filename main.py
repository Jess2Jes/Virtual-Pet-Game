import sys
from repositories.save_manager import SaveManager
from utils.game_facade import GameFacade
from utils.ports import FileContentLoader
from utils.main_view import MainView


class Main:
    """Application entry point that wires dependencies and runs the console UI."""

    def __init__(self):
        save_repo = SaveManager.get_instance()
        content_loader = FileContentLoader()
        facade = GameFacade(save_repo=save_repo, content_loader=content_loader)
        self.view = MainView(facade=facade, exit_fn=self._exit_game)

    def _exit_game(self) -> None:
        """Terminate the process with a final message."""
        from constants.configs import UIConfig as UIC

        print(UIC.LINE)
        sys.exit("Thank you for playing!".upper().center(len(UIC.LINE)) + "\n")

    def run(self) -> None:
        """Run the application loop."""
        self.view.run()


if __name__ == "__main__":
    app = Main()
    print("Starting UI...")
    app.run()