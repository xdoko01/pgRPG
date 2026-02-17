# Example of JSON describing dialog including all possible parameters

"id" : "dlg_example",

"templates" : ["basic_dlg"],

"dimensions" : [400, 200],

"background" : {
    "color" : "#FFFFFF",
    "image" : "quake.png",
    "alpha" : 128
},

"font" : {
    "path" : "small_font.json",
    "size" : 16,
    "color" : "#FFFFFF",
    "align" : "CENTER"
    },

"texts" : [
    {
        "font" : {
            "path" : "small_font.json",
            "color" : "#FF0000",
            "align" : "LEFT"
        },
        "text" : "This is dialog level text no 1",
        "position" : [0, 0]
    },
    {
        "text" : "This is dialog\nlevel text no 2",
        "position" : [0, 20]
    },
    {
        "text" : "This is dialog\nlevel text no 3",
        "position" : [50, 100],
        "font" : {
            "path" : "good_neighbours_font.json"
        }
    }
],

"frames" : [
    {
        "font" : {
            "path" : "small_font.json",
            "size" : 8,
            "color" : "#00FFFF",
            "align" : "RIGHT"
        },

        "background" : {
            "color" : "#FF0000",
            "alpha" : 128
        },

        "images" : [
            {
                "path" : "quake.png",
                "position" : [50, 50]
            },
            {
                "path" : "bluesquare.png",
                "position" : [100, 50]
            }
        ],

        "texts" : [
            {
                "text" : "Once upon\nthe time",
                "position" : [0, 100]
            }
        ]
    },
    {
        "texts" : [
            {
                "text" : "There was\nlovely little sausage called\nBaldrick",
                "position" : [100, 100]
            }
        ]
    },
    {
        "texts" : [
            {
                "text" : "And he lived happily\never after",
                "position" : [0, 100]
            }
        ]
    }
]


# Dialog JSON emelents description


## Key `/id`

Key `id` describes the internal identificator of the dialog. It should be the same as the filename of the JSON (if the `id` of the dialog is example, it should be stored in `example.json` document). When loaded, dialog will be stored and referenced by the `id` in the pgrpg engine.

### Examples

  - "id" : "dlg_basic"
  - "id" : "dlg_teleport_hint"
  - "id" : "dlg_scene_start"

### Mandatory / Optional

  - Mandatory

### Element path(s)

  - `/id`


## Key `/templates`

Key `templates` defines none or many dialog `id`s in a form of list from which the dialog inherits its structure. By specifying more `id`s in the list the template can inherit its properties from more than onew dialog. If same property is part of more templates in the `templates` list, the latter is used (overwritten) by the former. In other words, the more right in the list the template is the more priority it has in the final dialog. 

By having such multiple inheritance, the definition of new dialogs is easier as we can reuse existing definitions. For example there can be some basic dialog definition (dlg_basic) that defines background and fonts. All the used dialogs can then inherit from this dlg_basic dialog and do not need to have information about font and background within their definition - hence making the definition more readable. Of course the dialog can override the font or background property by defining it in its definition.

### Examples

  - "templates" : ["dlg_empty"]
  - "templates" : ["dlg_empty", "dlg_basic", "dlg_scene_start"]

### Mandatory / Optional

  - Optional (default empty list)

### Element path(s)

  - `/templates`


## Key `/dimensions`

Key `dimensions` specifies `[width, height]` of the dialog in pixels.

### Examples

  - "dimensions" : [200, 200]

### Mandatory / Optional

  - Mandatory

### Element path(s)

  - `/dimensions`


## Key `/background`

Key `background` defines the dialog's background by color, picture and transparency. Picture needs to be uploaded in `resources/images/` path.

### Examples

    "background" : {
        "color" : "#FFFFFF",
    }

    "background" : {
        "color" : "#FFFFFF",
        "alpha" : 128
    }

    "background" : {
        "image" : "quake.png",
    }

    "background" : {
        "image" : "quake.png",
        "alpha" : 128
    }

### Mandatory / Optional

  - `/background` Optional (default empty dict)
  - `/background/color` Optional (default #FFFFFF - black)
  - `/background/image` Optional (default None)
  - `/background/alpha` Optional (default 255 - no transparency)

### Element path(s)

  - `/background`
  - `/frames/*item*/background`


## Key `/font`

Key `font` defines the font that is used to display text in the dialog. The font is defined by the `path` value that is referencing BitMap font definition in a JSON file stored in `resources/fonts/` folder.

### Examples

    "font" : {
        "path" : "small_font.json"
        }

    "font" : {
        "path" : "small_font.json",
        "size" : 16
        }

    "font" : {
        "path" : "small_font.json",
        "size" : 16,
        "color" : "#FFFFFF"
        }

    "font" : {
        "path" : "small_font.json",
        "size" : 16,
        "color" : "#FFFFFF",
        "align" : "RIGHT"
        }

### Mandatory / Optional

  - `/font` Mandatory
  - `/font/path` Mandatory
  - `/font/size` Optional (default taken from the BitMap font image)
  - `/font/color` Optional (default taken from the BitMap font JSON)
  - `/font/align` Optional (default is LEFT)


### Element path(s)

  - `/font`
  - `/texts/*item*/font`
  - `/frames/*item*/font`
  - `/frames/*item*/texts/*item*/font`


## Key `/texts`

Key `texts` defines the individual text items that should be displayed on the dialog (above the background). Part of the text item specification can be also font specification that will override font specification stated higher in the hierarchy, i.e. on dialog level or on frame level.

### Examples

    "texts" : [
        {
            "text" : "Empty dialog",
        }
    ]

    "texts" : [
        {
            "text" : "Empty dialog",
            "position" : [0, 0]
        }
    ]

    "texts" : [
        {
            "font" : {
                "path" : "small_font.json",
                "size" : 16,
                "color" : "#FFFFFF",
                "align" : "RIGHT"
            },

            "text" : "Empty dialog",
            "position" : [0, 0]
        },
        {
            "text" : "Some other text",
            "position" : [100, 100]
        }
    ]


### Mandatory / Optional

  - `/texts` Optional (default no texts are shown)
  - `/texts/*item*/text` Mandatory
  - `/texts/*item*/position` Optional (default is [0,0])

### Element path(s)

  - `/texts`
  - `/frames/*item*/texts`


## Key `/images`

Key `images` defines the individual images that should be displayed on the dialog (above the background and below the texts). The `path` key must be in `resources/images/` folder.

### Examples

    "images" : [
        {
            "path" : "quake.png",
        }
    ]

    "images" : [
        {
            "path" : "quake.png",
            "position" : [10, 10]
        }
    ]

    "images" : [
        {
            "path" : "quake.png",
            "position" : [10, 10],
            "alpha" : 128
        }
    ]

    "images" : [
        {
            "path" : "quake.png",
            "position" : [10, 10],
            "alpha" : 128
        },
        {
            "path" : "random.png",
            "position" : [100, 100]
        }
    ]

### Mandatory / Optional

  - `/images` Optional (default no images are shown)
  - `/images/*item*/path` Mandatory
  - `/images/*item*/position` Optional (default is [0,0])
  - `/images/*item*/alpha` Optional (default is 255 - no transparency)

### Element path(s)

  - `/images`
  - `/frames/*item*/images`


## Key `/frames`

The dialog can have none to many frames. Frame is basicly element with images and texts that is shown within dialog. Dialogs using frames can have several slided that are changed after some key is pressed. Key `frames` defines dialog frames. 

### Examples

    "frames" : [
        {
            "font" : {
                "color" : "#00FF00",
                "align" : "CENTER"
            },

            "images" : [],

            "texts" : [
                {
                    "text" : "Use the teleport for/n transfering to different world!",
                    "position" : [50, 0]
                }
            ]
        }
    ]

### Mandatory / Optional

  - `/frames` Optional (default no frames)

### Element path(s)

  - `/frames`
