''' REad the font from JSON
'''

import pygame, sys, json

mainClock = pygame.time.Clock()
pygame.init()
pygame.display.set_caption('game base')
screen = pygame.display.set_mode((500, 500), 0, 32)

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

class BitmapFont():
    '''
    '''

    def __init__(self, path, size=None, color=None):
        '''
        '''

        # Open the model json file
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
            assert(color != self.colorkey, 'Color cannot be the same as the color key')
        except AssertionError:
            raise

        # List of characters included in the font file in the correct order
        self.character_order = font_data.get('character_order')

        # How many pixels of space between characters
        self.spacing = font_data.get('spacing', [1, 1])

        # Store the char images - keys are the letters, numbers and chars
        self.characters = {}

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

                # Set colorkey
                char_img.set_colorkey(self.colorkey)

                # Save it to the characters dictionary, key is the name of the character
                print(f'Saving {character_count} - {self.character_order[character_count]}')
                self.characters[self.character_order[character_count]] = char_img

                character_count += 1
                current_char_width = 0

            else:
                current_char_width += 1
        
        # Update the font color
        self.font_color = color

    def render(self, surf, text, loc):
        x_offset = 0

        for char in text:
            surf.blit(self.characters[char], (loc[0] + x_offset, loc[1]))
            x_offset += self.characters[char].get_width() + self.spacing[0]

    def _get_text_width(self, text):
        ''' Returns width in pixels of the given text.
        It is used internally tin render function to determine the final dimensions
        of a font surface.
        '''
        return sum([self.characters[char].get_width() + self.spacing[0] for char in text])

        #x_width = 0

        #for char in text:
        #    x_width += self.characters[char].get_width() + self.spacing[0]

    def _get_text_height(self, text=None):
        return self.font_height

    def _render_row(self, text):
        ''' Returns surface containing text in a row.
        It is used internally to render the final wrapped text surface
        '''

        # Prepare empty surface
        row_surf = pygame.Surface((self._get_text_width(text), self._get_text_height(text)))

        # Blit the text onto the surface
        x_offset = 0

        for char in text:
            row_surf.blit(self.characters[char], (x_offset, 0))
            x_offset += self.characters[char].get_width() + self.spacing[0]

        return row_surf

    def render_new(self, text, color=None, align='LEFT'):

        assert(color != self.colorkey, 'Color cannot be the same as the color key')

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


if __name__ == '__main__':

    # Test dictionary
    test_dict = {
        'head' : {'eyes' : 2, 'ears' : 2},
        'torso' : {'arms' : 2, 'nips' : 2},
        'legs' : {'nails' : 10}
    }

    # One way to init font
    my_first_font = BitmapFont('experiments/bitmap_font/small_font.json', color=pygame.Color('grey'))

    # Other way to init font (size included)
    my_second_font = BitmapFont('experiments/bitmap_font/small_font.json', 16)

    # Yet another way ti init font (color included)
    my_third_font = BitmapFont('experiments/ecs/resources/fonts/small_font.json', 16, pygame.Color('purple'))

    # ANother font
    my_forth_font = BitmapFont('experiments/bitmap_font/red_gradient_capital_font.json')

    while True:

        screen.fill((255, 255, 255))

        # First render method - where and what to blit
        my_first_font.render(screen, 'Hello World', (20, 20))

        # Second render method - blit manually
        screen.blit(my_second_font._render_row('Render row text'), (40, 40))

        # Third render method - blit manually multiple lines, alignment left
        screen.blit(my_third_font.render_new(f'Render text\nthat is rendered\nonto multiple\nlines.'), (60, 60))

        # Third render method - blit manually multiple lines, alignment right
        screen.blit(my_third_font.render_new(f'Render text\nthat is rendered\nonto multiple\nlines.', align='RIGHT'), (260, 60))

        # Third render method - blit manually multiple lines, alignment center
        screen.blit(my_third_font.render_new(f'Rendertext\nthat is rendered\nonto multiple\nlines.', pygame.Color('yellow'), align='CENTER'), (260, 260))

        # Try different font
        #screen.blit(my_forth_font.render_new(f'RENDER TEXT\nTHAT IS RENDERED\nONTO MULTIPLE\nLINES', align='CENTER'), (260, 160))


        # Test printing of dictionaries
        from pprint import pformat
        screen.blit(my_third_font.render_new(f'{pformat(test_dict)}', pygame.Color('blue')), (10, 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()