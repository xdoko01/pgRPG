''' Module for handling frames decoration around surfaces (typically around text)

Frame is defined by picture and json definition.
'''

import pygame, json


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

class BitmapFrame():
    '''
    '''

    #__slots__ = []

    def __init__(self, path, size=None, color=None):
        '''
        '''

        # Open the model json file
        try:
            with open(path, 'r') as frame_file:
                json_frame_data = frame_file.read()
                frame_data = json.loads(json_frame_data)
        except FileNotFoundError:
            print(f"Bitmap frame definition file '{path}' was not found.")
            raise ValueError

        self.frame_color = pygame.Color(frame_data.get('frame_color'))
        self.colorkey = pygame.Color(frame_data.get('colorkey', '#000000'))
        self.separator_color = pygame.Color(frame_data.get('separator_color'))
        self.frame_image_path = frame_data.get('frame_image')

        try:
            assert(color != self.colorkey, 'Color cannot be the same as the color key')
        except AssertionError:
            raise

        # List of characters included in the font file in the correct order
        self.elements_order = frame_data.get('elements_order')

        # How many pixels of space between characters
        #self.spacing = font_data.get('spacing', [1, 1])

        # Store the char images - keys are the letters, numbers and chars
        self.elements = {}

        # Load the PNG with the font
        frame_img = pygame.image.load(self.frame_image_path).convert()

        # Calculate the scaling factor for the font size
        scale = 1 if size is None else size / frame_img.get_height()

        # Store the font height
        self.frame_height = int(frame_img.get_height() * scale)

        # Keep track of witdh of the current character and number of characters
        current_element_width = 0
        element_count = 0

        # Iterate the font image column by column
        for x in range(frame_img.get_width()):

            # Read the column color and check if encountered the separation bar/pixel - start of the character was found
            if frame_img.get_at((x, 0)) == self.separator_color:

                # Cut the char image
                element_img = clip(frame_img, x - current_element_width, 0, current_element_width, frame_img.get_height())

                # Scale the font as required
                element_img = pygame.transform.scale(element_img, (int(element_img.get_width() * scale), int(element_img.get_height() * scale)))

                # Change color if required
                if color is not None:
                    element_img = color_swap(element_img, self.frame_color, color)

                # Set colorkey
                element_img.set_colorkey(self.colorkey)

                # Save it to the characters dictionary, key is the name of the character
                self.elements[self.elements_order[element_count]] = element_img

                element_count += 1
                current_element_width = 0

            else:
                current_element_width += 1
        
        # Update the font color
        self.frame_color = color

    def _get_frame_height(self):
        return self.frame_height

    def _get_frame_width(self, element):
        return self.elements[element].get_width()

    def render(self, text_surf):
        ''' Returns surface that is framed
        '''

        # Calculate dimensions of the new surface
        TM_element_count = text_surf.get_width() // self._get_frame_width('T') + 1
        BM_element_count = text_surf.get_width() // self._get_frame_width('B') + 1
        LM_element_count = RM_element_count = text_surf.get_height() // self._get_frame_height() + 1

        # Create new surface
        final_surf = pygame.Surface(
            ((TM_element_count * self._get_frame_width('T'))  + self._get_frame_width('TL') + self._get_frame_width('TR'),
            (LM_element_count * self._get_frame_height()) + self._get_frame_width('TL') + self._get_frame_width('BL'))
            )

        # Blit frame on the new surface
        x_offset = y_offset = 0

        for y in range(LM_element_count + 2):

            if y == 0:
                final_surf.blit(self.elements['TL'], (x_offset, y_offset))
                x_offset += self._get_frame_width('TL')

            elif y == LM_element_count + 1:
                final_surf.blit(self.elements['BL'], (x_offset, y_offset))
                x_offset += self._get_frame_width('BL')

            else:
                final_surf.blit(self.elements['L'], (x_offset, y_offset))
                x_offset += self._get_frame_width('L')

            for x in range(TM_element_count):
                if y == 0:
                    final_surf.blit(self.elements['T'], (x_offset, y_offset))
                    x_offset += self._get_frame_width('T')
                
                elif y == LM_element_count + 1:
                    final_surf.blit(self.elements['B'], (x_offset, y_offset))
                    x_offset += self._get_frame_width('B')

                else:
                    final_surf.blit(self.elements['M'], (x_offset, y_offset))
                    x_offset += self._get_frame_width('M')

            if y == 0:
                final_surf.blit(self.elements['TR'], (x_offset, y_offset))
                x_offset = 0
                y_offset += self._get_frame_height()

            elif y == LM_element_count + 1:
                final_surf.blit(self.elements['BR'], (x_offset, y_offset))
                # Finished!

            else:
                final_surf.blit(self.elements['R'], (x_offset, y_offset))
                x_offset = 0
                y_offset += self._get_frame_height()

        # Blit text on the new surface - in the center
        final_surf.blit(text_surf, (int(final_surf.get_width() / 2 - text_surf.get_width() / 2), int(final_surf.get_height() / 2 - text_surf.get_height() / 2)))

        # Must set colorkey otherwise background will not be transparent
        final_surf.set_colorkey(self.colorkey)

        return final_surf



if __name__ == '__main__':

    import sys
    from bitmap_font import *

    pygame.init()
    pygame.display.set_caption('game base')
    screen = pygame.display.set_mode((500, 500), 0, 32)

    # One way to init font
    my_first_font = BitmapFont('experiments/bitmap_font/small_font.json', color=pygame.Color('grey'))

    # Other way to init font (size included)
    my_second_font = BitmapFont('experiments/bitmap_font/small_font.json', 16)

    # Yet another way ti init font (color included)
    my_third_font = BitmapFont('experiments/bitmap_font/small_font.json', 16, pygame.Color('purple'))

    # New frame
    my_frame = BitmapFrame('experiments/bitmap_font/small_frame.json', color=pygame.Color('blue'))

    while True:

        screen.fill((255, 255, 255))

        # First render method - where and what to blit
        my_first_font.render(screen, 'Hello World', (20, 20))

        # Second render method - blit manually
        screen.blit(my_frame.render(my_second_font._render_row('Render row text')), (40, 40))

        # Third render method - blit manually multiple lines, alignment left
        screen.blit(my_frame.render(my_third_font.render_new(f'Render text\nthat is rendered\nonto multiple\nlines.')), (60, 60))

        # Third render method - blit manually multiple lines, alignment right
        screen.blit(my_frame.render(my_third_font.render_new(f'Render text\nthat is rendered\nonto multiple\nlines.', align='RIGHT')), (260, 60))

        # Third render method - blit manually multiple lines, alignment center
        screen.blit(my_frame.render(my_third_font.render_new(f'Render text\nthat is rendered\nonto multiple\nlines.', pygame.Color('yellow'), align='CENTER')), (260, 260))

        # Render frame
        screen.blit(my_frame.render(my_third_font.render_new(f'Render text that is rendered onto multiple\nlines.', align='CENTER')), (30, 300))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
