''' Module for handling bitmap fonts

Bitmap font is defined by picture and json definition. Picture needs to be in
non-data-loss format (png/bmp). All characters are on one row and are delimited
by pixel on the first row that is in specified color (separator_color). The JSON
definition of the font specifies information needed for font initiation and
rendering, i.e.

    - font_image - Specifies path to the bitmap picture with the font

    - font_color - Specifies the color of the font. It is used when the user
        wants to change the color of the font (substitute font_color by other
        color)

    - colorkey - Specifies the background color of the font. It is needed for
        keying-out the color in the font image.

    - separator_color - Specifies the color of the pixel that is used to separate
        individual font characters in the font_image file.

    - character_order - Specifies list of characters in the same order that those
        are present in the font_image file

    - spacing - Specifies space between text characters in pixels (horizontal/vertical)

Example of JSON font file is below:

    {
        "font_image" : "experiments/bitmap_font/red_gradient_capital_font.png",
        "font_color" : "#FF0000",
        "colorkey" : "#000000",
        "separator_color" : "#7F7F7F",
        "character_order" : ["Aa", "Bb", "Cc", "Dd", "Ee", "Ff", "Gg", "Hh", "Ii", "Jj", "Kk", "Ll", "Mm", "Nn", "Oo", "Pp", "Qq", "Rr", "Ss", "Tt", "Uu", "Vv", "Ww", "Xx", "Yy", "Zz", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "!", "?", " "],
        "spacing" : [1, 1]
    }

Notes:
    - Character_order values can have several characters. In example below, value "Aa" means
        that the first character image in font_image file will be assign to letter "A" and
        also to letter "a". This is useful in case font is missing for example lower case
        characters.

'''

__all__ = ['BitmapFont']

import pygame # For picture manipulation
import json # For reading the JSON font definition

########################################################
### Module functions
########################################################

def clip(surf, x, y, x_size, y_size):
    ''' Get defined surface from the larger surface
    '''

    handle_surf = surf.copy()
    clip_rect = pygame.Rect(x, y, x_size, y_size)
    handle_surf.set_clip(clip_rect)
    image = surf.subsurface(handle_surf.get_clip())

    return image.copy()

def color_swap(surf, old_color, new_color):
    ''' Swap one color to other color in the image
    '''

    # Create new empty surface and fill it with the new color
    img_copy = pygame.Surface(surf.get_size())
    img_copy.fill(new_color)

    # Set transparency on the old surface on the old color
    surf.set_colorkey(old_color)

    # Blit the old image to the new surface - as old color is transparent, colors are swaped
    img_copy.blit(surf, (0, 0))

    return img_copy

########################################################
### Module classes
########################################################

class BitmapFont():
    ''' Class containing character font pictures and necessary information.
    '''

    __slots__ = ['font_color', 'colorkey', 'separator_color', 'font_image_path', 'character_order', 'spacing', 'characters', 'font_height', 'char_width']

    def __init__(self, path, size=None, color=None):
        ''' Prepare bitmap font from predefined path in given size and color.

        Parameters:
            :param path: Path to the JSON file defining the font
            :type path: str

            :param size: Size of the font in pixels. Default value is hight of the font_image file.
            :type size: int

            :param color: Color of the font. Swaps default font_color with required color.
            :type color: pygame.Color

            :raise: ValueError - in case there is a problem with font initiation
        '''

        # Open the font json file
        try:
            with open(path, 'r') as font_file:
                json_font_data = font_file.read()
                font_data = json.loads(json_font_data)
        except FileNotFoundError:
            print(f"Bitmap font definition file '{path}' was not found.")
            raise ValueError

        self.font_color = pygame.Color(font_data.get('font_color'))
        self.colorkey = pygame.Color(font_data.get('colorkey', '#000000'))
        self.separator_color = pygame.Color(font_data.get('separator_color'))
        self.font_image_path = font_data.get('font_image')

        try:
            assert color != self.colorkey, 'Color cannot be the same as the color key'
        except AssertionError:
            raise ValueError

        # List of characters included in the font file in the correct order
        self.character_order = font_data.get('character_order')

        # How many pixels of space between characters
        self.spacing = font_data.get('spacing', [1, 1])

        # Store the char images - keys are the letters, numbers and chars
        self.characters = {}

        # Store char width in pixels - keys are the letters, numbers and chars
        self.char_width = {}

        # Load the PNG with the font
        font_img = pygame.image.load(self.font_image_path).convert()

        # Calculate the scaling factor for the font size
        scale = 1 if size is None else size / font_img.get_height()

        # Store the font height
        self.font_height = int(font_img.get_height() * scale)

        # Keep track of witdh of the current character and number of characters
        current_char_width = 0
        character_count = 0

        # Iterate the font image column by column
        for x in range(font_img.get_width()):

            # Read the column color and check if encountered the separation bar/pixel - start of the character was found
            if font_img.get_at((x, 0)) == self.separator_color:

                # Cut the char image
                char_img = clip(font_img, x - current_char_width, 0, current_char_width, font_img.get_height())

                # Scale the font as required
                char_img = pygame.transform.scale(char_img, (int(char_img.get_width() * scale), int(char_img.get_height() * scale)))

                # Change color if required
                if color is not None:
                    char_img = color_swap(char_img, self.font_color, color)

                # Set colorkey - not necessary here. The colorkey is used in the final render function
                # char_img.set_colorkey(self.colorkey)

                # Save it to the characters dictionary, key is the name of the character
                # Multiple characters are supported
                for char in self.character_order[character_count]:
                    self.characters[char] = char_img
                    self.char_width[char] = char_img.get_width()

                character_count += 1
                current_char_width = 0

            else:
                current_char_width += 1

        # Update the font color
        self.font_color = color

    def _get_text_width(self, text):
        ''' Returns width in pixels of the given text.
        It is used internally tin render function to determine the final dimensions
        of a font surface.
        '''

        return sum([self.char_width[char] for char in text]) + (self.spacing[0] * len(text))

        # Almost same speed as above
        #return sum(self.char_width[char] + self.spacing[0] for char in text)

        # Slower than above
        #return sum([self.char_width[char] for char in text]) + (self.spacing[0] * len(text))

        # Below is 1-2 frames slower than above
        #return sum([self.characters[char].get_width() + self.spacing[0] for char in text])

        # Below is 1-2 frames slower than above
        #return sum([self.characters[char].get_width() + self.spacing[0] for char in text if char in self.characters.keys()])

    def _get_text_height(self, text=None):
        ''' Returns height in pixels of the given text
        '''
        return self.font_height

    def _render_row(self, text):
        ''' Returns surface containing text in a row.
        It is used internally to render the final wrapped text surface
        '''

        # Prepare empty surface
        row_surf = pygame.Surface((self._get_text_width(text), self._get_text_height(text)))

        # Fill the surface with the font background color
        row_surf.fill(self.colorkey)

        # Blit the text onto the surface
        x_offset = 0

        for char in text:
            try:
                row_surf.blit(self.characters[char], (x_offset, 0))
                x_offset += self.char_width[char] + self.spacing[0]
            except KeyError:
                # Skip if the character is not defined by the font
                pass

        return row_surf

    def render(self, text, color=None, align='LEFT'):
        ''' Renders given text in given color and in given
        alignment to the new surface.
        '''

        assert color != self.colorkey, 'Color cannot be the same as the color key'

        # Generate each row on a separate surface
        rows_surfaces = []
        max_length = 0

        # Prepare individual surface for every row
        for row_text in text.split('\n'):

            # Generate the row surface
            row_surf = self._render_row(row_text)

            # Update the max row width value
            max_length = max(max_length, row_surf.get_width())

            # Add to the list of row surfaces
            rows_surfaces.append(row_surf)

        # Join the rows into one surface
        final_surface = pygame.Surface((max_length, (self._get_text_height() + self.spacing[1]) * len(rows_surfaces)))

        # Fill the surface with the font background color
        final_surface.fill(self.colorkey)

        for i, row_surface in enumerate(rows_surfaces):

            # Horizontal alignment
            if align == 'LEFT':
                x_align = 0
            elif align == 'RIGHT':
                x_align = max_length - row_surface.get_width()
            elif align in ['CENTER', 'CENTRE']:
                x_align = (max_length - row_surface.get_width()) // 2
            else:
                x_align = 0

            final_surface.blit(row_surface, (x_align, i * (self._get_text_height() + self.spacing[1])))

            # Change color as required
            if color is not None:
                final_surface = color_swap(final_surface, self.font_color, color)

        # Must set colorkey otherwise background will not be transparent
        final_surface.set_colorkey(self.colorkey)

        return final_surface

########################################################
### Module DEMO
########################################################

if __name__ == '__main__':

    import sys, pathlib

    pygame.init()
    pygame.display.set_caption('Bitmap Font Test')
    screen = pygame.display.set_mode((500, 500), 0, 32)

    # Where to find the JSON fonts
    FONT_PATH = pathlib.Path('experiments/ecs/resources/fonts')

    # One way to init font
    my_first_font = BitmapFont(FONT_PATH / 'small_font.json', color=pygame.Color('grey'))

    # Other way to init font (size included)
    my_second_font = BitmapFont(FONT_PATH / 'small_font.json', 16)

    # Yet another way ti init font (color included)
    my_third_font = BitmapFont(FONT_PATH /'small_font.json', 16, pygame.Color('purple'))

    # Yet another font - gradient
    my_fourth_font = BitmapFont(FONT_PATH /'red_gradient_capital_font.json', 15)

    # Yet another font - good neighbours
    my_fifth_font = BitmapFont(FONT_PATH /'good_neighbours_font.json', 32, pygame.Color('blue'))

    while True:

        screen.fill((128, 0, 128))

        # Second render method - blit manually
        screen.blit(my_second_font._render_row('Render row text'), (40, 40))

        # Third render method - blit manually multiple lines, alignment left
        screen.blit(my_third_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.'), (60, 60))

        # Third render method - blit manually multiple lines, alignment right
        screen.blit(my_third_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.', align='RIGHT'), (260, 60))

        # Third render method - blit manually multiple lines, alignment center
        screen.blit(my_third_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.', pygame.Color('#010101'), align='CENTER'), (260, 260))

        # Gradient font
        screen.blit(my_fourth_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.', pygame.Color('#010101'), align='CENTER'), (160, 260))

        # Good Neighbours font
        screen.blit(my_fifth_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.', align='CENTER'), (60, 260))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
