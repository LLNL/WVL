'''OpenGL extension SGI.texture_color_table

Automatically generated by the get_gl_extensions script, do not edit!
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_SGI_texture_color_table'
_DEPRECATED = False
GL_TEXTURE_COLOR_TABLE_SGI = constant.Constant( 'GL_TEXTURE_COLOR_TABLE_SGI', 0x80BC )
glget.addGLGetConstant( GL_TEXTURE_COLOR_TABLE_SGI, (1,) )
GL_PROXY_TEXTURE_COLOR_TABLE_SGI = constant.Constant( 'GL_PROXY_TEXTURE_COLOR_TABLE_SGI', 0x80BD )


def glInitTextureColorTableSGI():
    '''Return boolean indicating whether this extension is available'''
    return extensions.hasGLExtension( EXTENSION_NAME )
