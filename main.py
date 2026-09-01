from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import subprocess


def list_projects(root: str, filter: str):
    projects = []

    # allow one additional sublevel
    search_command = (
        "find "
        + root
        + " -mindepth 2 -maxdepth 3 -type d -name .git -prune -exec dirname \{} \; | rev | cut -d'/' -f1 | rev"
    )

    if filter:
        search_command += f" | grep {filter}"
    try:
        result = subprocess.run(
            ["sh", "-c", search_command], capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()
        if output:
            projects = output.split("\n")
    except subprocess.CalledProcessError as e:
        output = f"Error: {e.stderr.strip()}"
    except FileNotFoundError:
        output = "Error: Script not found"

    return projects


def list_ws(root: str, filter: str):
    ws = []

    # allow one additional sublevel
    search_command = "find " + root + " -mindepth 0 -maxdepth 3 -name *.code-workspace"

    if filter:
        search_command += f" | grep {filter}"
    try:
        result = subprocess.run(
            ["sh", "-c", search_command], capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()
        if output:
            ws = output.split("\n")
    except subprocess.CalledProcessError as e:
        output = f"Error: {e.stderr.strip()}"
    except FileNotFoundError:
        output = "Error: Script not found"

    return ws


class CodeGitExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        code_command = extension.preferences["code_command"]
        root_folder = extension.preferences["root_folder"]

        projects = []
        ws = []
        projects = list_projects(root_folder, event.get_argument())
        ws = list_ws(root_folder, event.get_argument())
        items = []

        for w in ws:
            if w:  # Ensure the project name is not empty
                items.append(
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name=w,
                        description=f"Workspace: {w}",
                        on_enter=RunScriptAction(f"{code_command} {w}"),
                    )
                )

        # Populate items with project names
        for project in projects:
            if project:  # Ensure the project name is not empty
                items.append(
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name=project,
                        description=f"Project: {project}",
                        on_enter=RunScriptAction(
                            f"{code_command} {root_folder}/{project}"
                        ),
                    )
                )

        if len(items) > 10:
            items = items[:10]

        if len(items) == 0:
            items.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="No projects found",
                    description="No projects found in the root folder",
                    on_enter=HideWindowAction(),
                )
            )

        return RenderResultListAction(items)


if __name__ == "__main__":
    CodeGitExtension().run()
