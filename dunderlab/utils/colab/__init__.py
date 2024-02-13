import os
import sys
import logging
import subprocess
from typing import Optional, Callable

import ipywidgets as widgets
from IPython.display import display, HTML

try:
    from google.colab.userdata import get as get_secret
    WORKING_PATH: str = '/content'
    REPOSITORY_PATH: str = '/content/my_repository'
except:
    from ipython_secrets import get_secret
    WORKING_PATH: str = '.'
    REPOSITORY_PATH: str = './my_repository'


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
        self.layout = widgets.Layout(height='37px')

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
                 placeholder: str = '', validate: bool = False):
        """
        Initialize the CommandLayout with a text widget and a button.

        Args:
            description (str): The description for the text widget.
            button (str): The label for the button.
            callback (Callable, optional): The function to call when the button is clicked.
            placeholder (str): Placeholder text for the text widget.
            validate (bool): Whether to enable validation on the text widget.
        """
        self.button = CustomButton(description=button, button_style='danger', disabled=True)
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
        self.clone_layout = CommandLayout('Repository', 'Clone', callback=self.clone,
                                          placeholder='https://github.com/dunderlab/test-push-workflow.git',
                                          validate='https://github.com/')
        self.commit_layout = CommandLayout('Message', 'Commit', callback=self.commit,
                                           placeholder='Update', validate=True)

        self.status_button = CustomButton(description='Status', button_style='info', callback=self.status)
        self.pull_button = CustomButton(description='Pull', button_style='info', callback=self.pull)
        self.push_button = CustomButton(description='Push', button_style='warning', callback=self.push)

        self.button_layout = widgets.HBox([self.status_button, self.pull_button, self.push_button],
                                          layout=widgets.Layout(justify_content='flex-start', width='100%'))

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
        self.run_command(f"git commit -m '{self.commit_layout.text.strip()}'", path=REPOSITORY_PATH)
        self.commit_layout.text = ''

    # ----------------------------------------------------------------------
    def pull(self, evt: Optional[widgets.Button] = None) -> None:
        """Pulls the latest changes from the remote repository."""
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
        lab.clone_layout.layout,
        lab.commit_layout.layout,
        lab.button_layout,
        lab.logger
    ]

    # Apply CSS styles to the logger
    display(HTML('<style> .lab-logger { font-family: monospace; text-wrap: balance; } </style>'))

    # Create a GridspecLayout with the defined components
    grid = widgets.GridspecLayout(len(layouts), 1)
    for i, layout in enumerate(layouts):
        grid[i, 0] = layout

    return grid

