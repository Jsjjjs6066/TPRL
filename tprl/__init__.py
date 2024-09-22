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

class Nothing(Element):
    """Element `Nothing` is _nothing_.

    **FOR DEBUGGING PURPOSES ONLY!**"""
    def __init__(self):
        """An initializer for `Nothing`.  """
        super().__init__()
    def render(self) -> str:
        """Renders `Nothing`, an empty `str`. """
        return ''

class Para(Label):
    """Paragraph element, just like the `<p>` element in HTML. """
    def __init__(self, text: str, args: dict[str, Any] = {}):
        """Paragraph initializer. """
        super().__init__(text, args)
    def render(self) -> str:
        """Render method. """
        return super().render() + '\n' # `Label` + '\n'

class Line(Element):
    """Line element. """
    def __init__(self, char: str, args: dict[str, Any] = {}):
        """Line initializer. """
        self.char = char
    def render(self) -> str:
        """Line renderer. """
        return self.char[-1] * os.get_terminal_size().columns

class NL(Element):
    """New line element. """
    def __init__(self, args: dict[str, Any] = {}):
        """New line initializer. """
        pass
    def render(self) -> str:
        """New line renderer. """
        return '\n'

class ElementRegistry(Enum):
    """All registered elements. """
    LABEL = ('label', type(Label('label')))
    PARA = ('para', type(Para('para')))
    LINE = ('line', type(Line('-')))
    NL = ('nl', type(NL()))

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

        self.set_title(self.title) # Set the title

def load_file(filePath: str) -> dict:
    """Loads the `filePath` as a path to the file which is then turned into a `dict` object. """
    with open(filePath, 'r') as f:
        return loads(f.read())

def decode_element(encoded_element: list[Union[str, Any]]) -> Element:
    """Decodes a `list` to an `Element`. """
    for registeredElement in ElementRegistry: # Checking every element
        if encoded_element[0] == registeredElement.refName: # Checks if the names match
            try:
                if len(encoded_element) == 1:
                    return registeredElement.elementType() # No args
                elif len(encoded_element) == 2:
                    return registeredElement.elementType(encoded_element[1]) # 1 arg
                else:
                    return registeredElement.elementType(encoded_element[1], encoded_element[2]) # 2 args
            except:
                return Nothing()
    return Nothing()

def clear() -> None:
    """Clears the terminal. """
    if platform.system() == 'Windows':  # Clears the terminal
        os.system('cls')  # For Windows
    else:
        os.system('clear')  # Other

def action_confirmation(action: str, pageObject: Page) -> bool:
    """Ask the user to confirm an action. """
    clear() # Clear the terminal
    print(f'Please confirm this action: {action}')
    print('Press Y to confirm, or any other key to not confirm.')
    if getwch().lower() == 'y': # Ask for a char
        clear()
        print(pageObject.text_to_be_rendered)
        return True # Pressed `y`
    else:
        clear()
        print(pageObject.text_to_be_rendered)
        return False # Pressed anything other then `y`

def operate_file(filePath: str) -> None:
    """Main function. """
    if len(argv) > 1:
        try:
            page_dict: dict = load_file(filePath) # Loads a file from the argument
        except:
            print('There was an error loading this file. Press... ')
            print('<M> to go to the main page')
            print('or'.center(os.get_terminal_size().columns, '-'))
            print('<X> or <ESC> to exit')
            print('<R> to reload')
            while True: # Check loop
                try:
                    char: str = getwch()  # Get a char from the input
                    if char.lower() == 'm':
                        page_dict: dict = load_file(MAIN_PAGE_PATH)  # Loads the main page
                        break # Stop the loop
                    if char.lower() == 'x' or char == '\x1b':
                        clear() # Clear the terminal
                        print('Exited TPRL. ')
                        exit() # Stop the program
                    elif char.lower() == 'r':
                        clear() # Clear the terminal
                        main() # Load again
                        break
                except KeyboardInterrupt: # Prevent <CTRL + C>
                    pass
    else:
        page_dict: dict = load_file(MAIN_PAGE_PATH) # Loads the main page

    element_list: list[Element] = []

    for element in page_dict.get('body'): # identifies elements and converts them
        element_list.append(
            decode_element(element)
        )

    title: str | None = page_dict.get('title') # GEts the title

    page: Page = Page(element_list, title) # Makes a Page object
    clear() # Clear the terminal
    page.render() # Render the page

    while True: # Page loop
        try:
            char: str = getwch()  # Get a char from the input
            if char.lower() == 'x' or char.lower() == '\x1b':
                if action_confirmation('exit', page):
                    clear() # Clear the terminal
                    print('Exited TPRL. ')
                    break # Stop the loop
            elif char.lower() == 'r':
                if action_confirmation('refresh', page):
                    clear() # Clear the terminal
                    main() # Load again
                    break
        except KeyboardInterrupt: # Prevent <CTRL + C>
            pass

if __name__ == '__main__':
    main() # Starts the program
