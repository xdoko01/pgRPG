''' Implementation of class that can handle font represented as bitmap file

  - module bitmap_font
  - class Font(filename, size)
    - filename specifies the json with font info
    - json contains
      - link to the bitmap
      - dictionary with info about rect in the bitmap for particular char, alternativelly list where position is ascii value

  - method render(text: str, alignment (Font.LEFT, Font.RIGHT, Font.CENTER)) -> Surface
  - Namedtuple(image, (width, height))

'''
import pygame


# Dict with font information
font_info = {
    'image_file' : 'experiments/bitmap_font/pixel-simplicity_grey.png',
    'colorkey' : '#000000',
    'range' : 69,
    'offset' : 32,
    'char_dim' : [5, 7],
    'columns' : 18,
    'spacing' : [0, 0]
}

#font_info = {
#    'image_file' : 'experiments/bitmap_font/font5x7.png',
#    'colorkey' : '#000000',
#    'char_dim' : [5, 7],
#    'columns' : 32,
#    'spacing' : [0, 0]
#}

#font_info = {
#    'image_file' : 'experiments/bitmap_font/good_neighbors.png',
#    'colorkey' : '#000000',
#    'char_dim' : [10, 16],
#    'columns' : 90 
#}


class Font:

    def __init__(self, filename, resize=1):
        self.image_file = font_info.get('image_file')
        self.colorkey = font_info.get('colorkey')
        self.char_dim = font_info.get('char_dim')
        self.columns = font_info.get('columns')
        self.spacing = font_info.get('spacing')
        self.range = font_info.get('range')
        self.offset = font_info.get('offset')

        self.image = pygame.image.load(self.image_file).convert()
        self.image.set_colorkey(pygame.Color(self.colorkey))

        self.font_list = []

        for i in range(127):
            
            if i < self.offset:
                print(f'{i} - Ommiting character: {chr(i)}')
                self.font_list.append(pygame.Surface((self.char_dim[0], self.char_dim[1])))

            else:
                print(f'{i} - Saving character: {chr(i)}')

                rect = ((i % self.columns) * self.char_dim[0],
                        (i // self.columns) * self.char_dim[1],
                        self.char_dim[0], self.char_dim[1])
                
                self.font_list.append(self.image.subsurface(rect))


    def render(self, text, align='LEFT'):

        # Generate each row on a separate surface
        rows_surfaces = []
        max_length = 0

        # Prepare individual surface for every row
        for row_text in text.split('\n'):

            # Calculate dimensions of the row surface
            rendered_surface = pygame.Surface((len(row_text) * (self.char_dim[0] + self.spacing[0]), (self.char_dim[1] + self.spacing[1])))

            max_length = max(max_length, rendered_surface.get_size()[0])

            for pos, c in enumerate(row_text):
                rendered_surface.blit(self.font_list[ord(c)], (pos * (self.char_dim[0] + self.spacing[0]), 0))

            # Add to the list
            rows_surfaces.append(rendered_surface)

        # Join the rows into one surface
        final_surface = pygame.Surface((max_length, (self.char_dim[1] + self.spacing[1]) * len(rows_surfaces)))

        for i, row_surface in enumerate(rows_surfaces):

            # Horizontal alignment
            if align == 'LEFT':
                x_align = 0
            elif align == 'RIGHT':
                x_align = max_length - row_surface.get_size()[0]
            elif align == 'CENTER':
                x_align = (max_length - row_surface.get_size()[0]) // 2
            else:
                x_align = 0

            final_surface.blit(row_surface, (x_align, i * (self.char_dim[1] + self.spacing[1])))

        return final_surface

## TEST
if __name__ == '__main__':

    # Init pygame
    pygame.init()
    window = pygame.display.set_mode((300, 300), 0, 32)
    window.fill((0,0,0))

    fixed_font = Font('whatever')

    window.blit(fixed_font.render('Ahoj svete\nJak to jde\n...ale jo, jde to', align='LEFT'), (0, 0))

    pygame.display.update()

    running = True

    while running:

        # Check for End and keys
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
