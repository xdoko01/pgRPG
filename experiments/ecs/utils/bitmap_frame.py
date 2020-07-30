''' Module for handling frames decoration around surfaces (typically around text)

Bitmap frame is defined by picture and json definition. Picture needs to be in
non-data-loss format (png/bmp). All frame picture elements are on one row and 
are delimited by pixel on the first row that is in specified color (separator_color).
The JSON definition of the frame specifies information needed for frame initiation and
rendering, i.e.

    - frame_image - Specifies path to the bitmap picture with the frame elements.

    - frame_color - Specifies the color of the frame. It is used when the user
        wants to change the color of the frame (substitute frame_color by other
        color).

    - colorkey - Specifies the background color of the frame. It is needed for
        keying-out the color in the frame image.

    - separator_color - Specifies the color of the pixel that is used to separate
        individual frame elements in the frame_image file.

    - elements_order - Specifies list of elements in the same order that those
        are present in the frame_image file.
            - TL ... top-left corner element
            - TR ... top-right corner element
            - BL ... bottom-left corner element
            - BR ... bottom-right corner element
            - T ... top edge element
            - B ... bottom edge element
            - L ... left edge element
            - R ... right edge element
            - M ... middle element - fills the frame

Example of JSON frame file is below:

{
    "frame_image" : "experiments/ecs/resources/images/small_font_frame.png",
    "frame_color" : "#FF0000",
	"colorkey" : "#FF00FF",
    "separator_color" : "#7F7F7F",
    "elements_order" : ["TL", "TR", "T", "BL", "BR", "R", "L", "B", "M"]
}

'''

__all__ = ['BitmapFrame']

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

class BitmapFrame():
    ''' Class containing frame pictures and necessary information.
    '''

    __slots__ = ['frame_color', 'colorkey', 'separator_color', 'frame_image_path', 'elements_order', 'elements', 'frame_height']

    def __init__(self, path, size=None, color=None):
        ''' Prepare bitmap frame from predefined path in given size and color.

        Parameters:
            :param path: Path to the JSON file defining the frame
            :type path: str

            :param size: Size of the frame in pixels. Default value is hight of the frame_image file.
            :type size: int

            :param color: Color of the frame. Swaps default frame_color with required color.
            :type color: pygame.Color

            :raise: ValueError - in case there is a problem with frame initiation
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
            assert color != self.colorkey, 'Color cannot be the same as the color key'
        except AssertionError:
            raise ValueError

        # List of characters included in the font file in the correct order
        self.elements_order = frame_data.get('elements_order')

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

                # Set colorkey - not necessary here. The colorkey is used in the final render function
                #element_img.set_colorkey(self.colorkey)

                # Save it to the characters dictionary, key is the name of the character
                self.elements[self.elements_order[element_count]] = element_img

                element_count += 1
                current_element_width = 0

            else:
                current_element_width += 1
        
        # Update the font color
        self.frame_color = color

    def _get_frame_width(self, element):
        ''' Returns width in pixels of the given frame element.
        '''
        return self.elements[element].get_width()

    def _get_frame_height(self):
        ''' Returns height in pixels of the given frame
        '''
        return self.frame_height

    def get_frame_dim(self, text_surf_dim):
        ''' Returns dimensions of the framed surface
        '''

        # Calculate dimensions of the new surface
        TM_element_count = text_surf_dim[0] // self._get_frame_width('T') + 1
        BM_element_count = text_surf_dim[0] // self._get_frame_width('B') + 1
        LM_element_count = RM_element_count = text_surf_dim[1] // self._get_frame_height() + 1

        return (
            (TM_element_count * self._get_frame_width('T')) + self._get_frame_width('TL') + self._get_frame_width('TR'),
            (LM_element_count * self._get_frame_height()) + self._get_frame_width('TL') + self._get_frame_width('BL')
            )

    def render(self, text_surf):
        ''' Returns surface that is framed by the bitmap frame
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

    def render_on(self, target_surf, dest, text_surf, alpha=100):
        ''' Returns surface that is framed by the bitmap frame
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

        # Must set colorkey otherwise background will not be transparent
        final_surf.set_colorkey(self.colorkey)

        # Must set colorkey otherwise background will not be transparent
        final_surf.set_alpha(alpha)

        # Get target coordinates
        (x_dest, y_dest) = dest

        # Blit the frame to the target surface
        target_surf.blit(final_surf, (x_dest, y_dest))

        # Blit text on the target surface - in the center
        target_surf.blit(text_surf, (x_dest + int(final_surf.get_width() / 2 - text_surf.get_width() / 2), y_dest + int(final_surf.get_height() / 2 - text_surf.get_height() / 2)))

    def render_frame_only(self, text_surf_dim, alpha=255):
        ''' Returns only frame without text blitted on it
        '''
        # Calculate dimensions of the new surface
        TM_element_count = text_surf_dim[0] // self._get_frame_width('T') + 1
        BM_element_count = text_surf_dim[0] // self._get_frame_width('B') + 1
        LM_element_count = RM_element_count = text_surf_dim[1] // self._get_frame_height() + 1

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

        # Must set colorkey otherwise background will not be transparent
        final_surf.set_colorkey(self.colorkey)

        final_surf.set_alpha(alpha)

        return (final_surf, ((int(final_surf.get_width() / 2 - text_surf_dim[0] / 2), int(final_surf.get_height() / 2 - text_surf_dim[1] / 2))))


########################################################
### Module DEMO
########################################################

if __name__ == '__main__':

    import sys, pathlib
    from bitmap_font import * # to test together with the bitmap font

    pygame.init()
    pygame.display.set_caption('Bitmap Frame Test')
    screen = pygame.display.set_mode((500, 500), 0, 32)

    # Where to find the JSON frames and fonts
    FRAME_PATH = pathlib.Path('experiments/ecs/resources/frames')
    FONT_PATH = pathlib.Path('experiments/ecs/resources/fonts')

    # One way to init font
    my_first_font = BitmapFont(FONT_PATH / 'small_font.json', color=pygame.Color('grey'))

    # Other way to init font
    my_second_font = BitmapFont(FONT_PATH / 'good_neighbours_font.json')

    # Yet another way to init font (color included)
    my_third_font = BitmapFont(FONT_PATH / 'small_font.json', 16, pygame.Color('purple'))

    # New frame
    my_frame = BitmapFrame(FRAME_PATH / 'small_frame.json', 16, pygame.Color('#00FF00'))

    while True:

        screen.fill((127, 127, 255))

        # Second render method - blit manually
        screen.blit(my_frame.render(my_second_font._render_row('Render row text')), (40, 40))

        # Third render method - blit manually multiple lines, alignment left
        screen.blit(my_frame.render(my_third_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.')), (60, 60))

        # Third render method - blit manually multiple lines, alignment right
        screen.blit(my_frame.render(my_third_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.', align='RIGHT')), (260, 60))

        # Third render method - blit manually multiple lines, alignment center
        screen.blit(my_frame.render(my_third_font.render(f'Render text\nthat is rendered\nonto multiple\nlines.', pygame.Color('yellow'), align='CENTER')), (260, 260))

        # Render frame
        screen.blit(my_frame.render(my_second_font.render(f'Render text that is rendered onto multiple\nlines.', align='CENTER')), (30, 300))
        #screen.blit(my_second_font.render(f'Render text that is rendered onto multiple\nlines.', align='CENTER'), (30, 400))

        # Render alpha frame
        my_frame.render_on(screen, (30, 400), my_second_font.render(f'Render text that is rendered onto multiple\nlines.', align='CENTER'), alpha=127)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
