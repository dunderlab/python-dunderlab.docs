import os
import sys
import shutil
from pathlib import Path
import logging
import subprocess
from typing import Optional, Callable

import ipywidgets as widgets
from IPython.display import display, HTML

try:
    from google.colab.userdata import get as get_secret
    WORKING_PATH: Path = Path('/').joinpath('content').resolve()
    REPOSITORY_PATH: Path = Path('/').joinpath('content', 'my_repository').resolve()
except:
    from ipython_secrets import get_secret
    WORKING_PATH: Path = Path('.').resolve()
    REPOSITORY_PATH: Path = Path('.').joinpath('my_repository').resolve()

WORKFLOW_DIR = REPOSITORY_PATH / '.github' / 'workflows'
CURRENT_DIR = Path(__file__).parent


########################################################################
class ValidateText(widgets.Text):
    """
    A custom widget class that extends ipywidgets.Text to include validation functionality.

    Attributes:
        button (widgets.Button): A button widget that changes based on the validation.

    Methods:
        _update_style(change): Updates the button style based on validation conditions.
    """

    # ----------------------------------------------------------------------
    def __init__(self, **kwargs):
        """
        Initialize the ValidateText widget.

        Args:
            validate (bool): A flag to activate validation.
            button (widgets.Button): A button widget linked to this text widget.
        """
        super().__init__(**kwargs)
        self.validate: bool = kwargs.get('validate', False)
        self.button: widgets.Button = kwargs.get('button', None)

        if self.validate:
            self.observe(self._update_style, names='value')

    # ----------------------------------------------------------------------
    def _update_style(self, change: dict) -> None:
        """
        Update the style of the associated button based on the validation condition.

        Args:
            change (dict): A dictionary containing the change details.
        """
        new_value = change['new']
        cond = bool(new_value) if self.validate is True else new_value.startswith(self.validate)

        self.button.button_style = 'success' if cond else 'danger'
        self.button.disabled = not cond


########################################################################
class CustomButton(widgets.Button):
    """
    A custom button widget with predefined layout and optional callback functionality.

    Methods:
        __init__(callback): Initializes the custom button with a callback function.
    """

    # ----------------------------------------------------------------------
    def __init__(self, callback: Optional[Callable] = None, **kwargs):
        """
        Initialize the CustomButton widget.

        Args:
            callback (Callable, optional): The function to call when the button is clicked.
        """
        super().__init__(**kwargs)
        self.layout = widgets.Layout(height='37px', width=kwargs.get('width', 'none'))

        if callback:
            self.on_click(callback)


########################################################################
class CommandLayout:
    """
    A layout class combining a text widget with a custom button for command inputs.

    Methods:
        __init__(description, button, callback, placeholder, validate): Initializes the command layout.
        layout: Returns the widget layout.
        text: Gets or sets the text value of the text widget.
    """

    # ----------------------------------------------------------------------
    def __init__(self, description: str, button: str, callback: Optional[Callable] = None,
                 placeholder: str = '', validate: bool = False, tooltip: str = ''):
        """
        Initialize the CommandLayout with a text widget and a button.

        Args:
            description (str): The description for the text widget.
            button (str): The label for the button.
            callback (Callable, optional): The function to call when the button is clicked.
            placeholder (str): Placeholder text for the text widget.
            validate (bool): Whether to enable validation on the text widget.
        """
        self.button = CustomButton(description=button, button_style='danger', disabled=True, tooltip=tooltip)
        self.validate_text = ValidateText(
            placeholder=placeholder,
            description=description,
            disabled=False,
            validate=validate,
            button=self.button,
            layout=widgets.Layout(width='100%', padding='5px')
        )

        if callback:
            self.button.on_click(callback)

    # ----------------------------------------------------------------------
    @property
    def layout(self) -> widgets.AppLayout:
        """
        Get the widget layout for the command layout.

        Returns:
            widgets.AppLayout: The layout combining the text widget and the button.
        """
        return widgets.AppLayout(center=self.validate_text, right_sidebar=self.button)

    # ----------------------------------------------------------------------
    @property
    def text(self) -> str:
        """
        Get the current text value of the text widget.

        Returns:
            str: The current text value.
        """
        return self.validate_text.value

    # ----------------------------------------------------------------------
    @text.setter
    def text(self, value: str) -> None:
        """
        Set the text value of the text widget.

        Args:
            value (str): The text value to set.
        """
        self.validate_text.value = value


########################################################################
class GitHubLazy:
    """
    A class for managing GitHub operations within a Jupyter notebook environment using ipywidgets.

    This class provides functionalities to clone, commit, pull, push, and check the status of a GitHub repository.
    """

    GITHUB_PAT: Optional[str] = get_secret('GITHUB_PAT')
    GITHUB_NAME: Optional[str] = get_secret('GITHUB_NAME')
    GITHUB_EMAIL: Optional[str] = get_secret('GITHUB_EMAIL')

    logger: widgets.Label = widgets.Label('', layout=widgets.Layout(font_family='monospace', font_size='20px'))
    logger.add_class('lab-logger')

    # ----------------------------------------------------------------------
    def __init__(self):
        """Initializes the GitHubLazy interface with necessary widgets and configurations."""

        self.github_title = widgets.Label("GitHub Integration for Jupyter: Simplified Management")
        self.github_title.add_class('title-size')

        self.github_header = widgets.Label("This tool is an integrated system for managing GitHub repositories within a Jupyter Notebook environment. It offers a user-friendly graphical interface that simplifies common Git operations, making them more accessible to users of all skill levels.",
                                           # layout=widgets.Layout(height='100px'),
                                           )
        self.github_header.add_class('text-wrap')

        self.clone_layout = CommandLayout('Repository', 'Clone', callback=self.clone,
                                          placeholder='https://github.com/<organization|user>/<repository>.git',
                                          validate='https://github.com/',
                                          tooltip="Creates a local copy of a remote repository. This command is used to download existing source code from a remote repository to a local machine.",
                                          )
        self.commit_layout = CommandLayout('Message', 'Commit', callback=self.commit,
                                           placeholder='Update',
                                           validate=True,
                                           tooltip="Records changes made to files in a local repository. A commit saves a snapshot of the project's currently staged changes.",
                                           )

        self.status_button = CustomButton(description='Status', button_style='info', callback=self.status,
                                          tooltip="Displays the state of the working directory and the staging area. It shows which changes have been staged, which haven't, and which files aren't being tracked by Git.")
        self.pull_button = CustomButton(description='Pull', button_style='info', callback=self.pull,
                                        tooltip="Fetches changes from a remote repository and merges them into the local branch. This is used to update the local code with changes from others.")
        self.push_button = CustomButton(description='Push', button_style='warning', callback=self.push,
                                        tooltip="Updates the remote repository with any commits made locally to a branch. It's a way to share your changes with others.")

        self.github_button_layout = widgets.HBox([self.status_button, self.pull_button, self.push_button],
                                                 layout=widgets.Layout(justify_content='flex-start', width='100%'))

        yml_files = []
        for yml_file in CURRENT_DIR.glob('*.yml'):
            checkbox = widgets.Checkbox(value=(WORKFLOW_DIR / yml_file.name).exists(),
                                        description=yml_file.name,
                                        disabled=False,
                                        indent=True,
                                        layout=widgets.Layout(width='90%'),
                                        )
            checkbox.observe(lambda evt, yml_file=yml_file: self.copy_workflow(yml_file), names='value')
            yml_files.append(checkbox)

        if yml_files:
            self.webhooks_title = widgets.Label("Automated Workflow Creation for GitHub Repositories")
            self.webhooks_title.add_class('title-size')
            self.right_button_layout = widgets.VBox(yml_files, layout=widgets.Layout(justify_content='flex-start', width='100%'))

        self.run_command(f'git config --global user.name "{self.GITHUB_NAME}"', silent=True)
        self.run_command(f'git config --global user.email "{self.GITHUB_EMAIL}"', silent=True)

    # ----------------------------------------------------------------------
    def run_command(self, command: str, path: str = '.', silent: bool = True) -> None:
        """
        Executes a given shell command in the specified directory path.

        Args:
            command (str): The shell command to execute.
            path (str): The directory path where the command is to be executed.
            silent (bool): If True, suppresses the logging output.
        """
        original_dir = os.getcwd()
        os.chdir(path)

        if not silent:
            logging.warning(f'Original directory: {original_dir}')
            logging.warning(f'Moving to {path}')
            logging.warning(f'Running command: {command}')

        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        stdout, stderr = result.stdout, result.stderr
        self.logger.value = f'{stdout}\n{stderr}'

        os.chdir(original_dir)

        if not silent:
            logging.warning(f'Back again to {original_dir}')

    # ----------------------------------------------------------------------
    def clone(self, evt: Optional[widgets.Button] = None) -> None:
        """Clones a GitHub repository based on the URL provided in the clone_layout text widget."""
        repository_url = self.clone_layout.text.removeprefix('https://')
        self.run_command(f"git clone https://{self.GITHUB_PAT}@{repository_url} my_repository", path=WORKING_PATH)
        self.run_command('git config pull.rebase true', silent=True)
        self.run_command('git config --global credential.helper cache', silent=True)
        sys.path.append(REPOSITORY_PATH)

    # ----------------------------------------------------------------------
    def commit(self, evt: Optional[widgets.Button] = None) -> None:
        """Commits changes to the local repository with the message provided in the commit_layout text widget."""
        self.run_command("git add .", path=REPOSITORY_PATH)
        self.run_command("git add -f .github", path=REPOSITORY_PATH)
        self.run_command(f"git commit -m '{self.commit_layout.text.strip()}'", path=REPOSITORY_PATH)
        self.commit_layout.text = ''

    # ----------------------------------------------------------------------
    def pull(self, evt: Optional[widgets.Button] = None) -> None:
        """Pulls the latest changes from the remote repository."""
        self.run_command('git config pull.rebase true', silent=True)
        self.run_command("git pull", path=REPOSITORY_PATH)

    # ----------------------------------------------------------------------
    def status(self, evt: Optional[widgets.Button] = None) -> None:
        """Checks the current status of the local repository."""
        self.run_command("git status", path=REPOSITORY_PATH)

    # ----------------------------------------------------------------------
    def push(self, evt: Optional[widgets.Button] = None) -> None:
        """Pushes local commits to the remote repository."""
        self.run_command("git push", path=REPOSITORY_PATH)

    # ----------------------------------------------------------------------
    def copy_workflow(self, workflow):
        """"""
        os.makedirs(WORKFLOW_DIR, exist_ok=True)
        workflow_docs_dst = REPOSITORY_PATH / '.github' / 'workflows' / workflow.name
        if workflow_docs_dst.exists():
            os.remove(workflow_docs_dst)
        else:
            shutil.copyfile(workflow, workflow_docs_dst)


# ----------------------------------------------------------------------
def __lab__() -> widgets.GridspecLayout:
    """
    Creates and displays a GitHub management interface using ipywidgets.

    This function initializes the GitHubLazy class and arranges its components into a GridspecLayout for display.

    Returns:
        widgets.GridspecLayout: A grid layout containing the GitHubLazy interface components.
    """

    lab = GitHubLazy()

    # Define the layout components
    layouts = [
        lab.github_title,
        lab.github_header,
    ]

    if not REPOSITORY_PATH.exists():
        layouts.append(lab.clone_layout.layout)
    else:
        layouts.extend([
            lab.commit_layout.layout,
            lab.github_button_layout,
        ])

    layouts.extend([
        lab.webhooks_title,
        lab.right_button_layout,
        lab.logger,
    ])

    # Apply CSS styles to the logger
    display(HTML('<style> .lab-logger { font-family: monospace; text-wrap: pretty; height: auto !important } </style>'))
    display(HTML('<style> .text-wrap { text-wrap: pretty; line-height: 130%; height: auto !important; } </style>'))
    display(HTML('<style> .title-size { font-size: 150%; margin-top: 20px; } </style>'))

    grid = widgets.VBox(layouts, layout=widgets.Layout(justify_content='flex-start', width='100%'))
    return grid
