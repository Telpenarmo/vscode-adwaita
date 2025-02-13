#!/usr/bin/env python3
from xml.etree.ElementTree import ElementTree, parse as parse_xml


# A dictionary of GtkSourceView style names mapped to TextMate scopes.
# Use "Inspect Editor Tokens and Scopes" in VS Code to inspect TM scopes.
# Use this link to figure out what matches a style name: https://gitlab.gnome.org/GNOME/gtksourceview/-/blob/master/data/language-specs/
# Use these snippets to test how your rules look: https://gitlab.gnome.org/GNOME/gtksourceview/-/tree/master/tests/syntax-highlighting/
MAP = {
    # Default color
    'text': [
        # Empty selector applies to everything
        '',
        # Embedded expressions, e.g. ${→something←} in a string
        'meta.embedded',
        # Most operators are symbolic. Make them of default color. Also include some symbolic keyboards.
        # Alphabetical operators should be specifically whitelisted in def:keyword.
        'keyword.operator',
        'storage.type.function.arrow',  # =>
        # YAML symbolic keywords
        'keyword.control.flow.block-scalar.literal.yaml',
        'keyword.control.flow.block-scalar.folded.yaml',
        'storage.modifier.chomping-indicator.yaml',

        # Python
        'storage.type.string.python',  # f, b, r string prefixes
        'meta.function-call.python support.type.python',  # super() calls
        # Rust
        'string.quoted.byte.raw.rust',  # b string prefix
        # macro_rules! →hello_world_macro← {
        'meta.macro.rules entity.name.function.macro.rust',
    ],
    'def:base-n-integer': [
        # Whole number (in e.g. JS)
        'constant.numeric.binary',  # 0b1
        'constant.numeric.octal',  # 0o1
        'constant.numeric.hex',  # 0x1
        # Just the prefix/postfix (in e.g. C, Go)
        'keyword.other.unit.binary',  # 0b
        'keyword.other.unit.octal',  # 0o
        'keyword.other.unit.hexadecimal',  # 0x
        'keyword.other.unit.imaginary',  # 0x01→i←
        'keyword.other.unit.exponent'  # 0x01→p←2
    ],
    'def:boolean': [
        'constant.language.boolean',  # e.g. in JS
        'constant.language.bool'  # e.g. in Rust
    ],
    'def:comment': [
        'comment',
        # YAML
        'entity.other.document.begin.yaml',  # ---
        'entity.other.document.end.yaml'  # ...
    ],
    'def:constant': [
        # 'constant', # applies to CAPS_VARIABLES, which is unwanted
        'support.type.property-name',  # { →"key"←: ... } (in e.g. JSON)
        # Character (e.g. in Rust). Note: there should probably be a separate def:character rule,
        # but Adwaita scheme doesn't include it (and falls back to def:constant).
        'string.quoted.single.char',
        # CSS
        'support.constant.property-value.css',  # absolute, bold, etc
        # CSS has many units (em, vw, ...) with potentially more to come in the future.
        # Until wildcards are implemented https://github.com/microsoft/vscode-textmate/issues/160,
        # we can use this instead of `keyword.other.unit.*.css`:
        'source.css keyword.other.unit',
    ],
    'def:decimal': [
        'constant.numeric',
        # Rust
        'constant.numeric.decimal entity.name.type.numeric.rust'  # 1→i64←
    ],
    # 'def:deletion': [],
    'def:doc-comment-element': [
        'comment.block.documentation'
    ],
    'def:floating-point': [
        'constant.numeric.float'
    ],
    # gtksv is being inconstistent here, e.g. this applies to function names in definitions in
    # Python, but not in C or JS. I say less color is better than more color, so these are commented out.
    'def:function': [
        # 'meta.function entity.name.function',
        # 'meta.function.python support.function.magic.python'  # __init__, __getitem__, etc
    ],
    'def:heading': [
        'markup.heading.markdown'
    ],
    'def:keyword': [
        # Most keywords (operators are unstyled in 'text')
        'keyword',
        # Specifically include alphabetical operators and keywords
        'keyword.operator.new',  # new
        'keyword.operator.logical.python',  # and, or
        'source.js keyword.operator.expression',  # typeof, instanceof
        'source.ts keyword.operator.expression',
        # →const← name = ..., →class← Class: ..., →def← fn(): ...
        'storage.type',
        # →static← void Main(string[] args)
        'storage.modifier',
        # YAML
        'entity.name.tag.yaml'  # key names
    ],
    # 'def:link-destination': [],
    # 'def:link-text': [],
    # 'def:list-marker': [],
    # 'def:net-address': [],
    'def:number': [
        'constant.numeric'
    ],
    'def:preformatted-section': [],
    'def:preprocessor': [
        'meta.preprocessor',
        # →#include← <config.h> (override def:keyword)
        'meta.preprocessor keyword.control',
        # @decorator
        'entity.name.function.decorator',
        # At-rules (in e.g. CSS)
        'keyword.control.at-rule.media',
        # &amp;
        'constant.character.entity',
        # ${} (in e.g. JS)
        'punctuation.definition.template-expression',
        # Nix, Svelte
        # In JSX these scopes match {} in <a b={...}>, not what we want
        'punctuation.section.embedded.begin.nix',  # ${
        'punctuation.section.embedded.begin.svelte',
        'punctuation.section.embedded.end.nix',  # }
        'punctuation.section.embedded.end.svelte'
    ],
    'def:shebang': [
        'comment.line.number-sign.shebang'
    ],
    'def:special-char': [
        'constant.character.escape'  # \n
    ],
    'def:string': [
        'string'
    ],
    'def:strong-emphasis': [
        'markup.bold.markdown'
    ],
    'def:type': [
        'support.type',
        # C#
        'keyword.type.cs',
        # Go
        'source.go storage.type',
        # Rust
        'entity.name.type',
        # JS built-in constructors
        'support.class.builtin.js',
        'support.class.promise'
    ],
    # 'def:underlined': [],
    # 'def:warning': [],

    # 'c-sharp:format': [],
    'c-sharp:preprocessor': [
        'meta.preprocessor.cs'
    ],

    'c:printf': [
        'string constant.other.placeholder'  # %s
    ],
    # 'c:signal-name': [],
    'c:storage-class': [
        # →const← char *var_name = ...
        'source.c storage.modifier'
    ],
    'c:type-keyword': [
        'source.c storage.type'
    ],

    'css:id-selector': [
        'entity.other.attribute-name.id.css'
    ],
    'css:property-name': [
        'support.type.property-name.css'
    ],
    'css:pseudo-selector': [
        'entity.other.attribute-name.pseudo-element.css',
        'entity.other.attribute-name.pseudo-class.css',
        'meta.selector.css punctuation.section.function'
    ],
    'css:selector-symbol': [
        # >
        'meta.selector.css keyword.operator',
        # Intentionally different: instead of coloring [, = and ] in elem[attr="val"], color just attr
        'entity.other.attribute-name.css'
    ],
    # 'css:type-selector': [],
    'css:vendor-specific': [
        # -webkit-property: ...
        'support.type.vendored.property-name.css'
    ],

    'diff:added-line': [
        'markup.inserted.diff'
    ],
    'diff:changed-line': [
        'markup.changed'
    ],
    'diff:diff-file': [
        'meta.diff.header'
    ],
    'diff:location': [
        'meta.diff.range'
    ],
    'diff:removed-line': [
        'markup.deleted.diff'
    ],

    # 'go:printf': [],

    'python:builtin-function': [
        'support.function.builtin.python'
    ],
    'python:class-name': [
        'entity.name.type.class.python'
    ],
    'python:module-handler': [
        'keyword.control.import.python'
    ],

    'rust:attribute': [
        'meta.attribute.rust',
        'meta.attribute.rust keyword.operator'
    ],
    'rust:lifetime': [
        'entity.name.type.lifetime.rust'
    ],
    'rust:macro': [
        'entity.name.function.macro'
    ],
    # 'rust:scope': [], # no selector

    'xml:attribute-name': [
        # <property →name←="variant">...
        'meta.tag entity.other.attribute-name',
        # <property name→=←"variant">... in JSX
        'meta.tag keyword.operator.assignment',
        # <property name→=←"variant">... in HTML and alike
        'punctuation.separator.key-value.html',
        'punctuation.separator.key-value.svelte',
        # XML doesn't have a selector for =
        'text.xml meta.tag'
    ],
    'xml:attribute-value': [
        'meta.tag string'
    ],
    'xml:element-name': [
        # <→property← name="variant">...
        'entity.name.tag',
        # <→property← name="variant">... in Svelte
        'support.class.component.svelte',
        # →<←property name="variant"→>←...
        'punctuation.definition.tag'
    ],
    # 'xml:namespace': [],
    'xml:processing-instruction': [
        # <?→xml← version="1.0" encoding="UTF-8"?>
        'text.xml meta.tag.preprocessor entity.name.tag',
        # →<?←xml version="1.0" encoding="UTF-8"?→>←
        'text.xml meta.tag.preprocessor punctuation.definition.tag'
    ]
}


def gsv_get_named_colors(scheme: ElementTree):
    '''Get all colors from a GtkSourceView style scheme.'''
    colors = {}
    for color_elem in scheme.findall('color'):
        colors[color_elem.get('name')] = color_elem.get('value')
    return colors


def gsv_to_textmate(scheme: ElementTree):
    '''Convert a GtkSourceView style scheme to a TextMate theme.'''
    colors = gsv_get_named_colors(scheme)

    default_elem = scheme.find('style[@name="text"]')
    default_foreground = None

    if default_elem is not None:
        default_foreground = colors[default_elem.get('foreground')]
    if default_foreground is None:
        raise Exception('no default color defined in scheme')

    rules = []

    scope_paths = []
    for style_name in MAP:
        scope = MAP[style_name]
        style_elem = scheme.find(f'style[@name="{style_name}"]')

        if style_elem is None:
            print(f'warning: no {style_name} in scheme')
            continue

        settings = {}

        if style_elem.get('foreground'):
            settings['foreground'] = colors[style_elem.get('foreground')]

        font_styles = []
        for font_style in 'italic', 'bold', 'strikethorugh':
            if style_elem.get(font_style) == 'true':
                font_styles.append(font_style)
        settings['fontStyle'] = ' '.join(font_styles)

        rule = {'scope': scope, 'settings': settings}
        rules.append(rule)

    return rules


def get_adwaita_colors(theme_type):
    if theme_type == 'dark':
        file = 'gtksourceview_xml/Adwaita-dark.xml'
    else:
        file = 'gtksourceview_xml/Adwaita.xml'
    scheme = parse_xml(file)
    named_colors = gsv_get_named_colors(scheme)
    syntax_colors = gsv_to_textmate(scheme)
    return named_colors, syntax_colors
