"""The TPRL program source code.

**DISCLAIMER: Please run this using "python tprl/__init__.py" and not using "cd tprl" and then followed by "python __init__.py"!**"""

import todo

from sys import argv
import sys
from abc import ABC, abstractmethod
from json import loads
from enum import Enum
from typing import Any, Union
import os
from msvcrt import getwch
import platform

MAIN_PAGE_PATH: str = 'main_page.tprl'

class Element:
    """A default class for all the elements in TPRL. """
    def __init__(self):
        """Method to initialize a TPRL element. """
        ...

    def render(self) -> str:
        """Method used to return a `str` to be rendered later. """
        ...

class Label(Element):
    """Class for an element `Label`, which works like a `<label>` element in HTML. """
    def __init__(self, text: str, args: dict[str, Any] = {}):
        """Label initializer. """
        self.text = text
        self.args = args

    def render(self) -> str:
        "Returning a `str` of a `Label` element to be rendered later. "
        return self.text

class ElementRegistry(Enum):
    """All registered elements. """
    LABEL = ('label', type(Label('label')))

    def __init__(self, refName: str, elementType: type[Element]):
        """Initializer for registered elements. """
        self.refName = refName
        self.elementType = elementType

class Page:
    """Class for the page. """
    def __init__(self, body: list[Element] = [], title: str = 'page'):
        """Page initializer. """
        if not title: # Makes sure that the title is not `None`
            title = 'page'

        self.body = body
        self.title = title

    def set_title(self, title: str):
        """Sets the title of a page. """
        if not title: # Makes sure that the title is not `None`
            title = 'page'

        if os.name == 'nt':  # For Windows
            os.system(f'title {title}')
        elif sys.platform in ['linux', 'darwin']:  # For Linux and macOS
            sys.stdout.write(f'\033]0;{title}\007')
            sys.stdout.flush()

    def render(self):
        """Renders all the elements and displays the title. """
        self.text_to_be_rendered = '' # Text that will be rendered

        for element in self.body: # Runs the `render()` function from all the elements
            self.text_to_be_rendered += element.render()

        print(self.text_to_be_rendered) # Actually renders all the elements

        self.set_title(self.title)

def load_file(filePath: str) -> dict:
    """Loads the `filePath` as a path to the file which is then turned into a `dict` object. """
    with open(filePath, 'r') as f:
        return loads(f.read())

def decode_element(encoded_element: list[Union[str, Any]]) -> Element:
    """Decodes a `list` to an `Element`. """
    for registeredElement in ElementRegistry:
        if encoded_element[0] == registeredElement.refName:
            if len(encoded_element) == 1:
                return registeredElement.elementType()
            elif len(encoded_element) == 2:
                return registeredElement.elementType(encoded_element[1])
            else:
                return registeredElement.elementType(encoded_element[1], encoded_element[2])

def main() -> None:
    """Main function. """
    if len(argv) > 1:
        page_dict: dict = load_file(argv[1]) # Loads a file from the argument
    else:
        page_dict: dict = load_file(MAIN_PAGE_PATH) # Loads the main page

    element_list: list[Element] = []

    for element in page_dict.get('body'): # identifies elements and converts them
        element_list.append(
            decode_element(element)
        )

    title: str | None = page_dict.get('title') # GEts the title

    page: Page = Page(element_list, title) # Makes a Page object
    page.render() # Render the page

    while True: # Page loop
        try:
            char: str = getwch()  # Get a char from the input
            if char == 'x':
                if platform.system() == 'Windows': # Clears the terminal
                    os.system('cls') # For Windows
                else:
                    os.system('clear') # Other
                print('Exited TPRL. ')
                break
        except KeyboardInterrupt: # Prevent <CTRL + C>
            ...

if __name__ == '__main__':
    main() # Starts the program
